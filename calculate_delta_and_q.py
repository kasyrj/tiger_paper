#!/usr/bin/python3
import argparse
import phylogemetric

def harvest_to_matrix(csv):
    matrix = {}
    cleaned_lines = []
    for line in csv:
        cleaned_lines.append(line.strip().rstrip().split(","))
    for i in range(len(cleaned_lines)):
        if i == 0:
            continue
        fields = line.split(",")
        matrix[fields[0]] = fields[1:]
    return matrix

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=PARSER_DESC)

    parser.add_argument(dest="infile",
                        help="Input file",
                        metavar='INFILE',
                        type=str,
                        default = None)
    
    args = parser.parse_args()
    in_file = args.infile
    try:
        f = open(in_file,"r")
        infile = f.readlines()
        f.close()

    except FileNotFoundError:
        print("Could not find file",in_file)
        quit()

    matrix = harvest_csv_to_matrix(infile)
    delta_score = phylogemetric.DeltaScoreMetric(matrix)
    q_residual  = phylogemetric.QResidualMetric(matrix)
    
