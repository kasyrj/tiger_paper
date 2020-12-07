#!/usr/bin/python3

import string
import scipy
import numpy
import random

import dataframe

class SwampSimulator():
    
    _n_features = 0
    _n_langs = 0
    _taxon_namelen = 0
    _model = None

    def __init__(self, n_langs, n_features, alpha, dist=None, taxon_namelen = 3):
        assert taxon_namelen > 0, "taxon name length must be 1 or more"
        self._n_features = n_features
        self._n_langs = n_langs
        self.alpha = alpha
        # Accept arbitrary cognate class count distributions,
        # but default to a very basic uniform distribution between 1 and n_langs
        if not dist:
            self.dist = scipy.stats.randint(1, n_langs + 1)
        else:
            self.dist = dist

        self._taxon_namelen = taxon_namelen

    def generate_data(self):
        # Generate data
        taxa = self._generateTaxa()
        alignment = self._generateAlignment()
        features = self._generateFeatureNames()
        # Insert into harvest-style DataFrame
        data = dataframe.DataFrame()
        for taxon, values in zip(taxa, alignment):
            if taxon not in data.data:
                data.data[taxon] = {}
            assert len(values) == len(features)
            for feature, value in zip(features, values):
                data.data[taxon][feature] = value
        return data
        
    def _generateTaxa(self):
        taxa = []
        for i in range(self._n_langs):
            current = self._generateTaxon()
            while current in taxa:
                current = self._generateTaxon()
            taxa.append(current)
        return taxa
    
    def _generateTaxon(self):
        taxon = ""
        for i in range(self._taxon_namelen):
            taxon += numpy.random.choice(list(string.ascii_lowercase))
        return taxon

    def _generateAlignment(self):
        output = []
        for i in range(self._n_langs):
            output.append([])

        # Generate cognate class counts
        feature_sizes = self.dist.rvs(self._n_features)
        test_counter = 100000
        while 0 in feature_sizes or max(feature_sizes) > self._n_langs:
            feature_sizes = self.dist.rvs(self._n_features)
            test_counter -= 1
            if test_counter == 0:
                print("Could not generate a suitable sample of features with many sampling attempts.")
                exit(1)

        # Assign taxa to cognate classes
        for classes in feature_sizes:
            # For each meaning, we're going to generate a list `assignments`, which contains one element per language.
            # The elements indicate which cognate class a language is assigned to.
            # E.g. If there were 3 cognate classes for a meaning, and 10 languages, a valid `assignments` might be:
            # assignments = [0, 1, 1, 0, 2, 0, 0, 0, 0, 2]
            # We are generating these knowing only the number of cognates, e.g. 3 above.
            # It is a requirement that each cognate class is represented at least once.  So, we start off `assignments`
            # by sampling each cognate class precisely once (in numeric order, but fear not, all will get shuffled at the end)
            assignments = list(range(classes))
            # Now, we probably need to make some additional assignments.  How many?
            remaining = self._n_langs - len(assignments)
            if remaining:
                # Now, we don't care, for the remaining assignments, that every cognate class is represented at least once.
                # We can just sample randomly, and add the results to what we already have.  We could just sample uniformly
                # from range(0, classes) (and previously did!), but it's not realistic that all cognate classes are equally
                # sized on average.  So, let's instead sample the remaining assignments from a non-uniform multinomial
                # distribution, which is itself sampled from a symmetric Dirichlet distribution.  By setting the Dirichlet's
                # alpha parameter very high, we can gracefully degrade to the original uniform distribution.
                # First, sample the multinomial probabilities.
                multinomial_probs = scipy.stats.dirichlet.rvs(alpha=[self.alpha]*classes)[0]
                # Now sample the counts of each class, after making `remaining` draws from the multinomial dist
                multinomial_counts = scipy.stats.multinomial.rvs(n=remaining,p=multinomial_probs)
                # Add the actual assignments to `assignments`
                for j,count in enumerate(multinomial_counts):
                    assignments.extend([j]*count)
            # Shuffle everything as promised earlier
            random.shuffle(assignments)
            # Sanity checks
            assert len(assignments) == self._n_langs
            assert len(set(assignments)) == classes
            # Add to master output
            for j, x in enumerate(assignments):
                output[j].append(x)
        return output

    def _generateFeatureNames(self):
        output = []
        for i in range(1,self._n_features+1):
            output.append("f" + str(i).zfill(len(str(self._n_features))))
        return output
    
    def __del__(self):
        pass
