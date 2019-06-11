#!/usr/bin/python3
import argparse
import sys
import os
import master_script

sys.path.append(os.path.join(master_script.MATERIALS_FOLDER, master_script.TIGER_FOLDER))
import formats

parser = argparse.ArgumentParser(description="Create harvest CSV with tiger-calculator's CLDF reader")

parser.add_argument(dest="in_file",
                    help="Input file to analyze.",
                    metavar='IN_FILE',
                    default=None,
                    type=str)

args = parser.parse_args()
reader = formats.getReader("cldf")
content = reader.getContents(args.in_file)
taxa = content[0]
chars = content[1]
names = content[2]

out = []
current_line = ""
current_line = "lang"
for n in names:
    current_line += "," + n
out.append(current_line)
for i in range(len(taxa)):
    current_taxon = str(taxa[i])
    current_taxon = current_taxon.replace(" ","_")
    current_taxon = current_taxon.replace("õ","o")
    current_line = current_taxon
    for j in range(len(chars[i])):
        current_line += "," + str(chars[i][j])
    out.append(current_line)
for l in out:
    print(l)
