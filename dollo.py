import itertools
import random

import dendropy
from dendropy.simulate import treesim
import scipy.stats
import numpy as np

import dataframe

dummy_isos = set(["".join(chars) for chars in itertools.combinations("abcdefghijklmnopqrstuvwxyz",3)])

class DolloSimulator():

    def __generate_yule_tree(self, taxa, birthrate=1.0, taxa_names=None):
        names = self.tree_rng.sample(dummy_isos, min(taxa, len(dummy_isos)))
        # print(names)
        fancytaxa = dendropy.TaxonNamespace(names)
        tree = treesim.birth_death_tree(birth_rate=birthrate, death_rate=0.0, num_extant_tips=taxa, taxon_namespace=fancytaxa, rng=self.tree_rng)
        # print(tree.as_ascii_plot())
        return tree

    def __init__(self, n_languages, n_features, cognate_birthrate=0.5, cognate_gamma=1.0, borrowing_prob=0.0, rseed=None):
        if rseed == None:
            self.tree_rng = random.Random()
        else:
            self.tree_rng = random.Random(rseed)
            random.seed(rseed)
            np.random.seed(rseed)
        self.tree = self.__generate_yule_tree(n_languages, 1.0, None)
        self.n_features = n_features
        self.cognate_birthrate = cognate_birthrate
        self.cognate_gamma = cognate_gamma
        self.borrowing_prob = borrowing_prob
        self.next_cognate = None
        self.attested_cognates = {} # dict of attested cognate arrays
        self.borrowing_sources = []

    def __evolve_feature(self, feature, parent, gamma):
        '''Evolve immediate children of branch.'''
        # for each child in node, define timerate (average number of changes) as edge length * birth_rate * sampled gamma
        # sample whether a mutation occurs from a poisson distribution, based on timerate
        for child in parent.child_node_iter():
            timerate = child.edge_length * self.cognate_birthrate * gamma
            changes = scipy.stats.poisson(timerate).rvs()
            if changes:
                # A mutation has occurred.
                # define cognate as a new cognate. add new cognate number to attested cognates. Update next_cognate
                child.cognate = self.next_cognate
                self.attested_cognates[feature].append(child.cognate)
                self.next_cognate = max(self.attested_cognates[feature]) + 1
            else:
                # No change has occurred, so propagate the parent's cognate value
                child.cognate = parent.cognate

    def generate_data(self):
        """Generate cognate class data in a Dollo-like fashion."""
        self.data = dataframe.DataFrame()
        self.data.datatype = "binary" # what does this row do?
        for i in range(0, self.n_features):
            self.attested_cognates[i] = []
            gamma = scipy.stats.gamma(self.cognate_gamma,scale=1.0/self.cognate_gamma).rvs()
            self.next_cognate = 1
            first = True
            for parent in self.tree.preorder_node_iter():
                if first:
                    parent.cognate = self.next_cognate
                    self.attested_cognates[i] = [parent.cognate]
                    self.next_cognate = max(self.attested_cognates[i]) + 1
                    first = False
                # Lines here migrated to separate method to allow reusing it in borrowing.
                # Result is identical with previous version when no borrowing occurs and random seeds are defined explicitly.
                self.__evolve_feature(i, parent, gamma)

            self.borrowing_sources = [] # reset borrowing source constraints (populated during previous borrowing simulation)
            if self.borrowing_prob:
                self.__borrow_feature(i, gamma)

            terminal_values = []
            for leaf in self.tree.leaf_node_iter():
                if leaf.cognate not in terminal_values:
                    terminal_values.append(leaf.cognate)
            terminal_values.sort()
            trans = dict([(v,n) for (n,v) in enumerate(terminal_values)])
            for leaf in self.tree.leaf_node_iter():
                iso = str(leaf.taxon)[1:-1]
                if iso not in self.data.data:
                    self.data.data[iso] = {}
                self.data.data[iso]["f_%03d" % i] = trans[leaf.cognate] 
        #if self.borrowing_prob:
        #    self.data.borrow(self.borrowing_prob)

        return self.data

    def __borrow_feature(self, feature, gamma):
        '''Generate cascading borrowing events for feature.'''
        # draw separate gamma for borrowing susceptibility
        gamma_borr = scipy.stats.gamma(self.cognate_gamma,scale=1.0/self.cognate_gamma).rvs()
        # start similarly to when growing data
        for parent in self.tree.preorder_node_iter():
            for child in parent.child_node_iter():
                # check that current node is not dependent on an already generated borrowing event.
                #( = is a borrowing source language, or an ancestor of a borrowing source language). In that case no borrowing can take place.
                if child not in self.borrowing_sources:
                    # Borrowing likelihood similar to cognate change but with borrowing probability replacing cognate birth rate
                    timerate = child.edge_length * self.borrowing_prob * gamma_borr
                    # Similar Poisson sampling process as with cognate mutation, except now we sample for borrowing events
                    changes = scipy.stats.poisson(timerate).rvs()
                    if changes:
                        # A borrowing has occurred.
                        # Sample donor language from languages existing at this point in time. If no plausible sources are available, we skip this node.
                        try:
                            borrowing_source = random.choice(self.__get_borrowing_candidates(child))
                        except IndexError:
                            continue
                        child.cognate = borrowing_source.cognate
                        # add borrowing source and its ancestors to self.borrowing_sources, as their "history" is now constrained by the new borrowing event
                        self.borrowing_sources += [borrowing_source]
                        self.borrowing_sources += self.__get_ancestors(borrowing_source)
                        # remutate subtree's cognates, starting from borrower node, using tree building gamma
                        for node in child.preorder_internal_node_iter():
                            self.__evolve_feature(feature, node, gamma)

    def __get_borrowing_candidates(self,target):
        '''return list of nodes that are not the target or its ancestors, and exist within its time frame (i.e. do not have longer distance from root). If no such nodes exists, returns an empty list'''
        invalid_nodes = self.__get_ancestors(target)
        invalid_nodes.append(target)
        candidates = []
        target_branch_length = target.distance_from_root() # donor language = node whose distance from root <= target branch length
        #print("Target branch length ", target_branch_length)
        for parent in self.tree.preorder_node_iter():
            if parent in invalid_nodes: # reject ancestors and self
                continue
            if parent.distance_from_root() > target_branch_length:
                continue
            if any(parent.child_node_iter()): # returns false if leaf node
                for child in parent.child_node_iter():
                    if child.distance_from_root() > target_branch_length: # child exceeds branch length; parent best candidate
                        #print("Accepted:",parent.distance_from_root())
                        candidates.append(parent)
            else:
                #print("Accepted:",parent.distance_from_root())
                if parent not in candidates:
                    candidates.append(parent)
        #print("Returning",len(candidates),"borrowing candidates for target node with root distance",target_branch_length)
        #for i in candidates:
        #    print("Source root distance ->",i.distance_from_root())
        return candidates
    
    def __get_ancestors(self, node):
        '''Return ancestors of node'''
        nodes = []
        for anc in node.ancestor_iter():
            nodes.append(anc)
        return nodes
