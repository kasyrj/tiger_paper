#!/usr/bin/python3
import argparse
import sys
import os
import master_script

if __name__ == '__main__':

    sys.path.append(os.path.join(master_script.MATERIALS_FOLDER, master_script.TIGER_FOLDER))
    import formats

    parser = argparse.ArgumentParser(description="Create harvest CSV with tiger-calculator's CLDF reader")

    parser.add_argument(dest="in_file",
                        help="Input file to analyze.",
                        metavar='IN_FILE',
                        default=None,
                        type=str)

    parser.add_argument("-x",
                        dest="excluded_taxa",
                        help="Comma-separated list of taxa to exclude",
                        metavar='EXCLUDED_TAXA',
                        default="",
                        type=str)

    args = parser.parse_args()
    reader = formats.getReader("cldf")
    content = reader.getContents(args.in_file)
    taxa = content[0]
    chars = content[1]
    names = content[2]

    excluded_taxa = args.excluded_taxa.split(",")

    out = []
    current_line = ""
    current_line = "lang"
    for n in names:
        current_line += "," + n
    out.append(current_line)
    for i in range(len(taxa)):
        current_taxon = str(taxa[i])
        if current_taxon in excluded_taxa:
            continue
        current_taxon = current_taxon.replace(" ","_")
        current_taxon = current_taxon.replace("õ","o")
        current_line = current_taxon
        for j in range(len(chars[i])):
            current_line += "," + str(chars[i][j])
        out.append(current_line)
    for l in out:
        print(l)
