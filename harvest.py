#!/usr/bin/env python
import optparse

import dendropy

import dataframe
from dollo import DolloSimulator
from chain import ChainSimulator

def main():

    # Parse options
    parser = optparse.OptionParser()
    ## Data specification
    parser.add_option('-l', '--languages', action="store", dest="languages", type="int", default=10, help="Number of languges to generate data for (integer)")
    parser.add_option('-f', '--features', action="store", dest="features", type="int", default=10, help="Number of features to generate (prior to duplication) (integer)")
    ## Tree related stuff
    parser.add_option('-b', '--birthrate', action="store", dest="birthrate", type="float", default=1.0, help="Birthrate for Yule tree growing process (positive float)")
    parser.add_option('-B', '--borrowing', action="store", dest="borrowing", type="float", default=0.00, help="Borrowing probability"),
    ## Model specification
    parser.add_option('-m', '--model', action="store", dest="model", type="string", default="mk", help="Model to use for data generation (either \"dollo\" or \"mk\")")
    parser.add_option('-g', '--gamma', action="store", dest="gamma", type="float", default=1.0, help="Gamma rate variation shape parameter (positive float)"),
    parser.add_option('-c', '--cognate', action="store", dest="cognate_birthrate", type="float", default=1.0, help="Birthrate for new cognate classes for Dollo model (positive float)")
    options, files = parser.parse_args()

    # Simulate data
    if options.model == "dollo":
        simulator = DolloSimulator(options.languages, options.features, options.cognate_birthrate)
    elif options.model == "chain":
        simulator = ChainSimulator(options.languages, options.features, options.cognate_birthrate, options.gamma, options.borrowing)
    else:
        print("No model specified")
        return

    simulator.generate_data()
    data = simulator.data

    # Do borrwing
    data.borrow(options.borrowing)

    # Output
    print(data.format_output())

if __name__ == "__main__":
    main()
