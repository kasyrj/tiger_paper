#!/usr/bin/env python3
import argparse

import dendropy
import numpy

from dollo import DolloSimulator
from chain import ChainSimulator
from swampmodel import MarshGenerator

PARSER_DESC = "Generate a simulated cognate set dataset using one of several models."

def main():

    # Parse options
    parser = argparse.ArgumentParser(description=PARSER_DESC)
    ## Data specification
    parser.add_argument('-l', '--languages', action="store", dest="languages", type=int, default=10, help="Number of languges to generate data for (integer)")
    parser.add_argument('-f', '--features', action="store", dest="features", type=int, default=10, help="Number of features to generate (prior to duplication) (integer)")
    ## Tree related stuff
    parser.add_argument('-b', '--birthrate', action="store", dest="birthrate", type=float, default=1.0, help="Birthrate for Yule tree growing process (positive float)")
    parser.add_argument('-B', '--borrowing', action="store", dest="borrowing", type=float, default=0.00, help="Borrowing probability"),
    ## Model specification
    parser.add_argument('-m', '--model', action="store", dest="model", type=str, default="swamp", help="Model to use for data generation (either \"swamp\", \"dollo\" or \"chain\")")
    parser.add_argument('-g', '--gamma', action="store", dest="gamma", type=float, default=1.0, help="Gamma rate variation shape parameter (positive float)"),
    parser.add_argument('-c', '--cognate', action="store", dest="cognate_birthrate", type=float, default=1.0, help="Birthrate for new cognate classes for Dollo model (positive float)")
    parser.add_argument("-s","--random_seed", dest="randomseed", help="Seed for random number generator (optional).", metavar='RANDOMSEED', type=int, default=None)
    parser.add_argument("-p", "--parameters", dest="params", help="Swamp model parameters. For 'simple' one should specify \"min=n max=m\"  where 'min'is the minimum number of cognate classes and 'max' the maximum number of classes (which should not exceed the number of taxa). For 'poisson' one should specify \"lambda=l\", specifying the expected average number of cognate classes. Low lambda values may not work, as they're more likely to contain zeroes. To try to overcome this, you can specify \"samples=s\" to attempt to sample the distribution multiple times. By default the model attempts to sample 10 times before giving up.", default=["min=1", "max=26", "lambda=12","samples=10"], nargs="+", type=str)
    options = parser.parse_args()

    # Seed RNG
    if options.randomseed:
        numpy.random.seed(options.randomseed)

    # Simulate data
    if options.model == "dollo":
        simulator = DolloSimulator(options.languages, options.features, options.cognate_birthrate)
    elif options.model == "chain":
        simulator = ChainSimulator(options.languages, options.features, 0.8)
    elif options.model == "swamp":
        # Further process swamp-specific options
        model = { "type": "simple" }
        for elem in options.params:
            parts = elem.split("=")
            try:
                model[parts[0]] = int(parts[1])
            except ValueError: 
                model[parts[0]] = parts[1]
        simulator = MarshGenerator(options.features, options.languages, model=model)
    else:
        print("No model specified")
        return
    data = simulator.generate_data()

    # Do borrwing for tree models
    # (not for chain!  Borrowing there happens internally, but is controlled by the same param,
    # so doing it here too is double borrowing
    if options.model == "dollo":
        data.borrow(options.borrowing)

    # Output
    print(data.format_output())

if __name__ == "__main__":
    main()
