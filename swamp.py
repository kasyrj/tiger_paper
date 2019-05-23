#!/usr/bin/python3

# Generate non-tree-like characer alignment data

import swampmodel
import argparse

PARSER_DESC = "Produce a non-tree-like cognate set dataset."

if __name__=="__main__":

    parser = argparse.ArgumentParser(description=PARSER_DESC)
    
    parser.add_argument("-t", "--taxa",
                        dest="ntaxa",
                        help="Number of taxa (languages) to generate. Default: 26",
                        metavar='NTAXA',
                        default=26,
                        type=int)

    parser.add_argument("-f","--features",
                        dest="nfeatures",
                        help="Number of features (e.g. meanings) to generate. Default: 313",
                        metavar='NFEATURES',
                        default=313,
                        type=int)

    parser.add_argument("-m", "--model",
                        dest="model",
                        help="Which model is used to generate the data. Options: simple, poisson.",
                        default="simple",
                        type=str)

    parser.add_argument("-p", "--parameters",
                        dest="params",
                        help="Model parameters. For 'simple' one should specify \"min=n max=m\"  where 'min'is the minimum number of cognate classes and 'max' the maximum number of classes (which should not exceed the number of taxa). For 'poisson' one should specify \"lambda=l\", specifying the expected average number of cognate classes.",
                        default=["min=1", "max=26", "lambda=12"],
                        nargs="+",
                        type=str)

    parser.add_argument("-n","--name_length",
                        dest="namelength",
                        help="Number of random ASCII characters generated as a taxon name (must be at least 1). Default: 3",
                        metavar='NAMELENGTH',
                        default=3,
                        type=int)

    parser.add_argument("-s","--random_seed",
                        dest="randomseed",
                        help="Seed for random number generator (optional).",
                        metavar='RANDOMSEED',
                        default=None)

    
    args = parser.parse_args()
    model = {}
    model["type"] = args.model
    for elem in args.params:
        parts = elem.split("=")
        model[parts[0]] = int(parts[1])
        
    m = swampmodel.MarshGenerator(args.nfeatures,
                                  args.ntaxa,
                                  args.randomseed,
                                  args.namelength,
                                  model)
    m.generate().print() 
