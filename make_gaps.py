#!/usr/bin/python3

# Make random gaps to each data type.
# Coverage of chars: 90 percent, 80 percent, 70 percent, 60 percent, 50 percent.
# Analyze gapped data with TIGER. Results in folder "datagaps".
# Tabulate means and stds as separate tables in "datagaps".

import sys
import os
import master_script
import random
import numpy
import glob

TIGER_PARAMS = ["-f","harvest","-n", "-i", "?"]

# Run 001 used from each simulated dataset. From borrowing simulations only borrowing_20 used.

in_files = ["analyses/uralex/uralex.csv",
            "analyses/borrowing_20/borrowing_20_001.csv",
            "analyses/pure_tree/pure_tree_001.csv",
            "analyses/dialect/dialect_001.csv",
            "analyses/swamp/swamp_001.csv"]

datasets = ["uralex",
            "borrowing",
            "pure_tree",
            "dialect",
            "swamp"]

out_dir = "datagaps"
coverages = [0.9, 0.8, 0.7, 0.6, 0.5]
random_seed = 1234

def make_random_gaps(coverage, data):
    '''Drop random data points from data. coverage (float between 0..1) controls output size (percentage of output data points relative to input data points, rounded to the nearest integer. data expected to be in format similar to tiger-calculator'''
    taxa = data[0]
    chars = data[1]
    choices = range(len(chars[0]))
    items = round(len(chars[0]) * coverage)

    selection = sorted(random.sample(choices,items))
    newchars = []
    for i in range(len(chars)):
        newchars.append([])
        for j in selection:
            newchars[i].append(chars[i][j])
    print("Original data: " + str(len(data[1][0])) + " chars => New data: " + str(len(newchars[0])) + " chars")
    return [taxa,newchars]
    
if __name__ == '__main__':


    try:
        os.mkdir("datagaps")
    except OSError:
        print("Failed to create folder datagaps.")
        exit(1)
        
    # generate gapped datasets
    random.seed(random_seed)
    sys.path.append(os.path.join(master_script.MATERIALS_FOLDER, master_script.TIGER_FOLDER))
    import formats
    reader = formats.getReader("harvest")
    results = {}
    for n in range(len(in_files)):
        rates = []
        current_data = datasets[n]
        results[current_data] = {}
        results[current_data][1.0] = []
        content = reader.getContents(in_files[n])
        tiger_rates_file = glob.glob(in_files[n][:-4] + "*_rates.txt")[0]
        print("Adding TIGER results from " + tiger_rates_file)
        with open(tiger_rates_file, "r") as fp:
            rates.extend([float(x.strip().split()[-1]) for x in fp.readlines()])
            results[current_data][1.0].append(numpy.mean(rates))
            results[current_data][1.0].append(numpy.std(rates))
        for c in coverages:
            results[current_data][c] = []
            gapped_content = make_random_gaps(coverage=c, data=content)
            taxa = gapped_content[0]
            chars = gapped_content[1]
            output = []
            for i in range(len(taxa)):
                outline = ""
                outline += taxa[i]
                for elem in chars[i]:
                    outline += "," + elem
                outline += "\n"
                output.append(outline)
            outfile_name = os.path.join("datagaps", current_data + str(c) + ".csv")
            with open(outfile_name, "w") as f:
                for line in output:
                    f.write(line)
            master_script.run_tiger(outfile_name, TIGER_PARAMS, outfile_name)
            rates = []
            with open(outfile_name + "_rates.txt", "r") as fp:
                rates.extend([float(x.strip().split()[-1]) for x in fp.readlines()])
                results[current_data][c].append(numpy.mean(rates))
                results[current_data][c].append(numpy.std(rates))
    print("Writing tables...")
    for dataset in results.keys():
        table_file = []
        table_file.append(dataset)
        table_file.append("coverage" + "\t" + "mean" + "\t" + "sd")
        for coverage in sorted(results[dataset].keys(),reverse=True):
            table_file.append(str(coverage) + "\t" +
                              str(results[dataset][coverage][0]) + "\t" +
                              str(results[dataset][coverage][1]))
            with open("datagaps/" + dataset + "_gaps.tsv", "w") as fp:
                for line in table_file:
                    fp.write(line + "\n")
