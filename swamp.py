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

    parser.add_argument("-m","--min_classes",
                        dest="minclasses",
                        help="Minimum number of cognate classes per feature. Default: 1",
                        metavar='MINCLASSES',
                        default=1,
                        type=int)

    parser.add_argument("-M","--max_classes",
                        dest="maxclasses",
                        help="Minimum number of cognate classes per feature. Default: 26",
                        metavar='MAXCLASSES',
                        default=26,
                        type=int)

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
    m = swampmodel.MarshGenerator(args.nfeatures,
                             args.ntaxa,
                             args.randomseed,
                             args.minclasses,
                             args.maxclasses,
                             args.namelength)
    m.generate().print() 
