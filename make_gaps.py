#!/usr/bin/python3

# Make random gaps to each data type. The script produces two kinds of gapped data:
# 1. data with less aligned characters, meaning that we have less data from which to calculate TIGER values
# 2. data with the same number of aligned characters but more unknowns (missing data points). Every character
#    column needs to retain at least one character. 
# Coverage of chars: 90 percent, 80 percent, 70 percent, 60 percent, 50 percent.
# Analyze gapped data with TIGER. Results in folder "datagaps".
# Tabulate means and stds as separate tables in "datagaps".
# - Run 001 is used from each simulated dataset to calculate the gapped and missing data
# - Only one borrowing simulation is used

import sys
import os
import master_script
import random
import numpy
import glob
import copy

TIGER_PARAMS = ["-f","harvest","-n", "-i", "?"]

IN_FILES = [sorted(glob.glob("analyses/pure_tree/*_*1.csv"))[0],
            sorted(glob.glob("analyses/borrowing_10/*_*1.csv"))[0],
            sorted(glob.glob("analyses/dialect/*_*1.csv"))[0],
            sorted(glob.glob("analyses/swamp/*_*1.csv"))[0],
            "analyses/uralex/uralex.csv"]

DATASETS = ["pure_tree",
            "borrowing_10",
            "dialect",
            "swamp",
            "uralex"]

DATAGAPS_DIR = "datagaps"
COVERAGES = [0.9,0.8,0.7]
RANDOM_SEED = 1234

def make_random_unknowns(coverage, data, retain_sets = True):
    '''Change random data points from data to unknowns (?). coverage (float between 0..1) controls output size (percentage of known output data points relative to input data points, rounded to the nearest integer. data expected to be in format similar to tiger-calculator. Ensures that every column retains at least 1 character state. if retain_sets is True, the character state counts (e.g. the number of cognate sets) for each character is ensured to remain the same as it is in the input data; if retain_sets is False, character state counts are allowed to be reduced until 1.'''
    new_data = copy.deepcopy(data)
    taxa = new_data[0]
    chars = new_data[1]
    names = new_data[2]
    total_count = len(chars) * len(chars[0])         # theoretical maximum of data points. Some will be ?s.
    requested_count = round(total_count * coverage)  # how many data points we want
    valid_positions = {}                             # dict indexing data per aligned character
    character_states = {}                            # character states for each aligned character
    valid_count = 0                                  # actual number of data points
    for i in range(len(chars[0])):
        valid_positions[i] = []
        character_states[i] = set() 
    for i in range(len(chars)):
        for j in range(len(chars[i])):
            if chars[i][j] != "?":
                valid_positions[j].append(i)
                valid_count += 1
                character_states[j].add(chars[i][j])
    if retain_sets == False:
        for i in character_states:
            character_states[i] = set(random.choice(list(character_states[i]))) # 1 random state per position
    # Eliminate empty keys
    for a in valid_positions.keys():               
        if len(valid_positions[a]) == 0:
           valid_positions.pop(a, None)
    old_states = copy.deepcopy(character_states)
    # Prerequisite sanity checks
    min_valid_count = 0                       # at least one of each character state must remain
    for k in character_states.keys():
        min_valid_count += len(character_states[k])

    if requested_count < min_valid_count:             # requesting less data than practical minimum
        print("Cannot reduce data beyond "
              + str(min_valid_count) + " data points ("
              + str(round(float(min_valid_count) / total_count * 100, 2))
              + "%); requested: " + str(requested_count) + " data points (" + str(coverage * 100) + "%)")
        return None

    if requested_count > valid_count:             # requesting more data points than available
        print("Requested number of data points (" + str(requested_count) + ") exceeds number of recorded data points (" + str(valid_count) + ")")
        return None

    if requested_count == valid_count:            # data already at the requested size
        print("Data already of requested size (" + str(requested_count) + " data points)")
        return data

    counter = valid_count - requested_count       # counter for data points to remove
    while True:
        if counter == 0:
            break
        a = random.choice(list(valid_positions.keys()))
        random.shuffle(valid_positions[a])
        b = valid_positions[a].pop()                    
        if chars[b][a] in character_states[a]:  # we do not yet have a representative for this character
            character_states[a].remove(chars[b][a])
            if len(valid_positions[a]) == 0:
                valid_positions.pop(a, None)
            continue
        chars[b][a] = "?"
        counter -= 1
        if len(valid_positions[a]) == 0:
            valid_positions.pop(a, None)
    # Sanity checks: all character states remain if retain_sets is True; number of valid characters
    # is as requested
    valid_chars = 0
    new_states = {}
    for i in range(len(chars[0])):
        new_states[i] = set() 
    for i in range(len(chars)):
        for j in range(len(chars[i])):
            if chars[i][j] != "?":
                new_states[j].add(chars[i][j])
                valid_chars += 1
    for i in old_states.keys():
        if retain_sets:
            assert(old_states[i] == new_states[i])
    assert(valid_chars == requested_count)

    print("Original data coverage: "
          + str(valid_count) + " data points ("
          + str(round(float(valid_count) / total_count * 100, 2)) + " %)"
          + " => New data coverage: "
          + str(requested_count) + " data points ("
          + str(round(float(requested_count) / total_count * 100, 2)) + " %)"
          )
    return [taxa,chars,names]

def make_random_gaps(coverage, data):
    '''Drop random data points (meanings) from data. coverage (float between 0..1) controls output size (percentage of output data points relative to input data points, rounded to the nearest integer. data expected to be in format similar to tiger-calculator'''
    taxa = data[0]
    chars = data[1]
    names = data[2]
    choices = range(len(chars[0]))
    items = round(len(chars[0]) * coverage)
    selection = sorted(random.sample(choices,items))
    newchars = []
    newnames = []
    for i in range(len(chars)):
        newchars.append([])
        for j in selection:
            newchars[i].append(chars[i][j])
    for i in range(len(selection)):
        newnames.append(names[i])
    print("Original data: " + str(len(data[1][0])) + " chars => New data: " + str(len(newchars[0])) + " chars")
    return [taxa,newchars,newnames]

def write_harvest_csv(content, filename):
    '''Write content to harvest-style CSV'''
    taxa = content[0]
    chars = content[1]
    names = content[2]
    output = []
    outline = "lang"
    for name in names:
        outline += "," + name
    output.append(outline + "\n")
    for i in range(len(taxa)):
        outline = ""
        outline += taxa[i]
        for elem in chars[i]:
            outline += "," + elem
        outline += "\n"
        output.append(outline)
        with open(filename, "w") as f:
            for line in output:
                f.write(line)

if __name__ == '__main__':

    try:
        os.mkdir(DATAGAPS_DIR)
    except OSError:
        print("Failed to create folder %s." % DATAGAPS_DIR)
        exit(1)
        
    random.seed(RANDOM_SEED)
    sys.path.append(os.path.join(master_script.MATERIALS_FOLDER, master_script.TIGER_FOLDER))
    import formats
    reader = formats.getReader("harvest")
    results_gapped = {}
    results_missing = {}
    for c in COVERAGES:
        results_gapped[c] = {}
        results_missing[c] = {}        
    results_gapped[1.0] = {}
    results_missing[1.0] = {}

    for n in range(len(IN_FILES)):
        current_data = DATASETS[n]
        content = reader.getContents(IN_FILES[n])
        tiger_rates_file = glob.glob(IN_FILES[n][:-4] + "*_rates.txt")[0] # we do not recalculate full rates
        print("Adding TIGER results from " + tiger_rates_file)
        with open(tiger_rates_file, "r") as fp:
            rates = []
            rates.extend([float(x.strip().split()[-1]) for x in fp.readlines()])
            results_gapped[1.0][current_data] = numpy.mean(rates)
            results_missing[1.0][current_data] = numpy.mean(rates)
        for c in COVERAGES:
            gapped_content = make_random_gaps(coverage=c, data=content)
            missing_content = make_random_unknowns(coverage=c, data=content)
            if gapped_content == None or missing_content == None:
                print("Something went wrong. Exiting.")
                exit(1)
            outfile_gapped = os.path.join(DATAGAPS_DIR, current_data + "_" + str(c) + "_gaps.csv")
            outfile_missing = os.path.join(DATAGAPS_DIR, current_data + "_" + str(c) + "_unknowns.csv")            
            write_harvest_csv(gapped_content, outfile_gapped)
            write_harvest_csv(missing_content, outfile_missing)
            master_script.run_tiger(outfile_gapped, TIGER_PARAMS, outfile_gapped)
            master_script.run_tiger(outfile_missing, TIGER_PARAMS, outfile_missing)
            with open(outfile_gapped + "_rates.txt", "r") as fp:
                rates = []
                rates.extend([float(x.strip().split()[-1]) for x in fp.readlines()])
                results_gapped[c][current_data] = numpy.mean(rates)
            with open(outfile_missing + "_rates.txt", "r") as fp:
                rates = []
                rates.extend([float(x.strip().split()[-1]) for x in fp.readlines()])
                results_missing[c][current_data] = numpy.mean(rates)      
                
    print("Writing tables...")
    table_file = []
    table_file.append("dataset")
    for coverage in sorted(results_gapped.keys(), reverse=True):
        table_file[-1] += "\t" + str(coverage)
    table_file[-1] += "\tmean\tsd"
    for dataset in DATASETS:
        table_file.append(dataset)
        values = []
        for coverage in sorted(results_gapped.keys(), reverse=True):
            table_file[-1] += "\t" + str(results_gapped[coverage][dataset])
            values.append(results_gapped[coverage][dataset])
        table_file[-1] += "\t" + str(numpy.mean(values)) + "\t" + str(numpy.std(values))
    with open(os.path.join(DATAGAPS_DIR, "gaps.tsv"), "w") as fp:
        for line in table_file:
            fp.write(line + "\n")

    table_file = []
    table_file.append("dataset")
    for coverage in sorted(results_missing.keys(), reverse=True):
        table_file[-1] += "\t" + str(coverage)
    table_file[-1] += "\tmean\tsd"
    for dataset in DATASETS:
        table_file.append(dataset)
        values = []
        for coverage in sorted(results_missing.keys(), reverse=True):
            table_file[-1] += "\t" + str(results_missing[coverage][dataset])
            values.append(results_missing[coverage][dataset])
        table_file[-1] += "\t" + str(numpy.mean(values)) + "\t" + str(numpy.std(values))
                
    with open(os.path.join(DATAGAPS_DIR, "missing.tsv"), "w") as fp:
        for line in table_file:
            fp.write(line + "\n")
            
    #for dataset in results_gapped.keys():
    #    for item in DATASETS:
    #        table_file.append(item + "\t")
    
