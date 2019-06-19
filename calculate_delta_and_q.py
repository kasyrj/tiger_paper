#!/usr/bin/python3
import argparse
import sys
try:
    import phylogemetric
except:
    print("Package phylogemetric is required to run this program.", file=sys.stderr)
    exit(1)

def harvest_to_matrix(csv):
    matrix = {}
    cleaned_lines = []
    for line in csv:
        cleaned_lines.append(line.strip().rstrip())
    for i in range(len(cleaned_lines)):
        if i == 0:
            continue
        fields = cleaned_lines[i].split(",")
        matrix[fields[0]] = fields[1:]
    return matrix

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Calculate delta scores and Q-residuals for a harvest-style CSV")

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

    matrix = harvest_to_matrix(infile)
    delta_score = phylogemetric.DeltaScoreMetric(matrix).score()
    q_residual  = phylogemetric.QResidualMetric(matrix).score()
    print("taxon\tdelta-score\tq-residual")
    for taxon in sorted(delta_score.keys()):
        print("%s\t%f\t%f" % (taxon, delta_score[taxon],q_residual[taxon]))
        #    print(delta_score)
        #   print(q_residual)

    
