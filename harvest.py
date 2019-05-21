#!/usr/bin/env python
import optparse

import dendropy

import dataframe
import simulator
import trees
from dollo import DolloSimulator
from chain import ChainSimulator

def main():

    # Parse options
    parser = optparse.OptionParser()
    ## Data specification
    parser.add_option('-l', '--languages', action="store", dest="languages", type="int", default=10, help="Number of languges to generate data for (integer)")
    parser.add_option('-f', '--features', action="store", dest="features", type="int", default=10, help="Number of features to generate (prior to duplication) (integer)")
    parser.add_option('-q', '--qmarks', action="store", dest="missing_data_rate", type="float", default=0.0, help="Missing data frequency (probability)")
    ## Tree related stuff
    parser.add_option('-b', '--birthrate', action="store", dest="birthrate", type="float", default=1.0, help="Birthrate for Yule tree growing process (positive float)")
    parser.add_option('-t', '--treefile', action="store", dest="treefile", type="string", default=None, help="Filename to save generated tree to (Newick format)")
    parser.add_option('-T', '--loadtree', action="store", dest="loadtree", type="string", default=None, help="Filename to read tree from (Newick format) instead of simulating")
    parser.add_option('-B', '--borrowing', action="store", dest="borrowing", type="float", default=0.00, help="Borrowing probability"),
    ## Model specification
    parser.add_option('-m', '--model', action="store", dest="model", type="string", default="mk", help="Model to use for data generation (either \"dollo\" or \"mk\")")
    parser.add_option('-g', '--gamma', action="store", dest="gamma", type="float", default=1.0, help="Gamma rate variation shape parameter (positive float)"),
    parser.add_option('--prob-states', action="store_true", dest="prob-states", default=False, help="Whether or not to probabilistically vary number of states")
    parser.add_option('-c', '--cognate', action="store", dest="cognate_birthrate", type="float", default=1.0, help="Birthrate for new cognate classes for Dollo model (positive float)")
    ## Duplication
    parser.add_option('-d', '--duplication-rate', action="store", dest="dupe_n", type="float", default=0.0, help="(mean) number of duplication features (if int), or probabilistic feature duplication rate (if float)")
    parser.add_option('-F', '--duplication-fidelity', action="store", dest="dupe_fidelity", type="float", default=1.0, help="Duplication fidelity (probability)")
    parser.add_option('-k', action="store", dest="dupe_degree", type="int", default=0, help="Duplication degree")
    parser.add_option('--prob-degree', action="store_true", dest="prob_degree", default=False, help="Whether or not to probabilistically vary degree of duplication")
    ## Misc
    parser.add_option('-r', '--recurse', action="store_true", dest="recurse", default=False, help="Read data from stdin, rather than growing on tree")
    options, files = parser.parse_args()

    # Acquire data, either from stdin or by growing a tree
    if options.recurse:
        # Recursive power move!
        data = dataframe.read_from_stdin()
    else:
        if options.loadtree:
            # Load tree from Newick file
            tree = dendropy.Tree.get(path=options.loadtree, schema="newick")
        else:
            # Generate tree
            tree = trees.generate_yule_tree(options.languages, options.birthrate)
            if options.treefile:
                tree.write(file=open(options.treefile, 'w'), schema="newick")

        # Simulate data
        if options.model == "dollo":
            simulator = DolloSimulator(tree,options.features,options.cognate_birthrate)
        elif options.model == "chain":
            simulator = ChainSimulator(options.languages, options.features, options.cognate_birthrate, options.gamma, options.borrowing)
        else:
            print("No model specified")
            return

        simulator.generate_data()
        data = simulator.data

    # Perform duplication
#    data.duplication(options.dupe_n, options.dupe_degree, options.dupe_fidelity, options.prob_degree)

    # Do borrwing
    data.borrow(options.borrowing)

    # Add missing data (or rather, remove present data?)
    data.remove(options.missing_data_rate)

    # Output
    print(data.format_output())

if __name__ == "__main__":
    main()
