#!/usr/bin/python3

# Download the necessary files
# Generate and analyze samples
# Produce plots and CSVs

import urllib.request
import zipfile
import sys
import os
import glob
import random
import subprocess
import numpy as np
import scipy.stats

from dollo import DolloSimulator
from chain import ChainSimulator
from swamp import SwampSimulator
from make_tables import main as make_tables
from make_plots import main as make_plots

MATERIALS_FOLDER    = 'materials'
ANALYSIS_FOLDER     = 'analyses'
PYTHON_CMD          = 'python3'
URALEX_URL          = 'https://zenodo.org/record/1459402/files/lexibank/uralex-v1.0.zip?download=1'
URALEX_ZIP          = "uralex-v1.0.zip"
URALEX_FOLDER       = "lexibank-uralex-efe0a73"
TIGER_URL           = 'https://github.com/kasyrj/tiger-calculator/archive/d8325684f8d6e60e52fcb3e6c7ad8205aa44ea33.zip'
TIGER_ZIP           = "tiger-calculator.zip"
TIGER_FOLDER        = "tiger-calculator-d8325684f8d6e60e52fcb3e6c7ad8205aa44ea33"
N_REPETITIONS       = 100
N_EXPLORE_REPS      = 20
URALEX_BASE         = "uralex"
URALEX_N_LANGS      = 26
URALEX_N_FEATURES   = 313
URALEX_ALPHA        = 0.267
URALEX_COG_DIST     = scipy.stats.nbinom(9, 0.49)
SWAMP_BASE          = 'swamp'
DIALECT_BASE        = 'dialect'
HARVEST_BASE        = 'pure_tree'
URALEX_COG_BIRTH    = 2.0
BORROWING_BASE      = 'borrowing'
URALEX_TIGER_PARAMS = ["-f","cldf","-n", "-x", "Proto-Uralic*", "-i", "?"]

def run(cmd):
    proc = subprocess.Popen(cmd, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
    stdout, stderr = proc.communicate()
    return proc.returncode, stdout, stderr 

def write_lines_to_file(lines,filename):
    print("Writing to file %s" % filename)
    outfile = open(filename,"w")
    outfile.writelines(lines)
    outfile.close()
    #print("Done.")

def download_and_extract(url,filename,destination):
    try:
        zf = zipfile.ZipFile(filename, 'r')
    except FileNotFoundError:
        print("Downloading %s" % filename)
        urllib.request.urlretrieve(url,filename)
        print("Done.")
        zf = zipfile.ZipFile(filename, 'r')
    print("Extracting data to %s" % destination)
    zf.extractall(destination)
    zf.close()
    print("Done.")

def run_simulator(simulator, output_directory, filebase, repetition=0):

    try:
        os.makedirs(output_directory, exist_ok=True)
    except OSError:
        print("Failed to create folder %s." % output_directory)
        exit(1)

    data = simulator.generate_data()
    output = data.format_output()
    filename = os.path.join(output_directory,filebase + "_" + str(repetition+1).zfill(3) + ".csv")
    write_lines_to_file(output, filename)

def run_tree_model(output_directory, filebase, languages, features, cognate_birthrate, cognate_gamma=1.0, borrowing_probability=0.0, repetitions=N_REPETITIONS):
    for i in range(repetitions):
        simulator = DolloSimulator(languages, features, cognate_birthrate, cognate_gamma, borrowing_probability, i)
        run_simulator(simulator, output_directory, filebase, i)

def run_tree_model_with_uralex_params(output_directory, filebase, borrowing_probability=0.0):
    run_tree_model(output_directory, filebase, URALEX_N_LANGS, URALEX_N_FEATURES, URALEX_COG_BIRTH, 1.0, borrowing_probability)

def run_chain_model(output_directory, filebase, languages, features, alpha, dist, repetitions=N_REPETITIONS):
    for i in range(repetitions):
        simulator = ChainSimulator(languages, features, alpha, dist)
        run_simulator(simulator, output_directory, filebase, i)

def run_chain_model_with_uralex_params(output_directory, filebase):
    run_chain_model(output_directory, filebase, URALEX_N_LANGS, URALEX_N_FEATURES, URALEX_ALPHA, URALEX_COG_DIST, repetitions=N_REPETITIONS)

def run_swamp_model(output_directory, filebase, languages, features, alpha, dist, repetitions=N_REPETITIONS):
    for i in range(repetitions):
        simulator = SwampSimulator(languages, features, alpha, dist)
        run_simulator(simulator, output_directory, filebase, i)

def run_swamp_model_with_uralex_params(output_directory, filebase):
    run_swamp_model(output_directory, filebase, URALEX_N_LANGS, URALEX_N_FEATURES, URALEX_ALPHA, URALEX_COG_DIST)

def run_tiger(filename,params,outfile=None):
    print("Calculating TIGER rates for %s" % filename)
    params = params + [filename]
    tigercmd = os.path.join(MATERIALS_FOLDER,TIGER_FOLDER, "tiger-calculator.py")
    code,out,err = run([PYTHON_CMD, tigercmd] + params)
    print(err.decode("utf-8"), file=sys.stderr)
    if outfile == None:
        write_lines_to_file(out.decode("utf-8"), filename + "_rates.txt")
    else:
        write_lines_to_file(out.decode("utf-8"), outfile + "_rates.txt")

def harvest_to_nexus(directory, filename):
    print("Creating NEXUS for %s..." % filename)
    code,out,err = run([PYTHON_CMD, "harvestcsv2nexus.py", filename])
    print(err.decode("utf-8"), file=sys.stderr)
    write_lines_to_file(out.decode("utf-8"), os.path.join(directory,"splitstree_input.nex"))

def cldf_to_harvest(directory, cldf_path):
    code,out,err = run([PYTHON_CMD, "cldf2harvest.py", "-x", "Proto-Uralic*", cldf_path]) 
    print(err.decode("utf-8"), file=sys.stderr)
    write_lines_to_file(out.decode("utf-8"), os.path.join(directory,"uralex.csv"))

def calculate_delta_and_q(filename): 
    print("Calculating delta scores and Q-residuals for %s" % filename)
    params = [filename]
    code,out,err = run([PYTHON_CMD, "calculate_delta_and_q.py"] + params)
    print(err.decode("utf-8"), file=sys.stderr)
    write_lines_to_file(out.decode("utf-8"), filename + "_delta_qresidual.txt")

def get_uralex_counts():
    code,out,err = run([PYTHON_CMD, "get_uralex_counts.py"])    
    
def generate_synthetic_datasets():

    print ("Creating analysis folder...")
    if os.path.exists(ANALYSIS_FOLDER):
        print("Folder %s already exists. Remove or rename it to proceed." % ANALYSIS_FOLDER)
        exit(1)
    try:
        os.makedirs(ANALYSIS_FOLDER, exist_ok=True)
    except OSError:
        print("Failed to create folder %s." % ANALYSIS_FOLDER)
        exit(1)

    print("Successfully created folder %s" % ANALYSIS_FOLDER)

    print("Getting UraLex cognate counts...")
    get_uralex_counts()

    print("Generating swamp data...")
    swampdir = os.path.join(ANALYSIS_FOLDER,SWAMP_BASE)
    run_swamp_model_with_uralex_params(swampdir, SWAMP_BASE)
    print("Done.")

    print("Generating dialect chain data...")
    dialectdir = os.path.join(ANALYSIS_FOLDER,DIALECT_BASE)
    run_chain_model_with_uralex_params(dialectdir, DIALECT_BASE)
    print("Done.")

    print("Generating harvest data...")
    harvestdir = os.path.join(ANALYSIS_FOLDER,HARVEST_BASE)
    run_tree_model_with_uralex_params(harvestdir, HARVEST_BASE)
    print("Done.")

    print("Generating harvest data with borrowing...")
    for borrowing_rate in (0.05, 0.10, 0.15, 0.20):
        BASE = BORROWING_BASE + ("_%02d" % int(100*borrowing_rate))
        borrowingdir = os.path.join(ANALYSIS_FOLDER,BASE)
        run_tree_model_with_uralex_params(borrowingdir, BASE, borrowing_rate)
        print(borrowingdir, BASE, borrowing_rate)
    print("Done.")

def analyse_all_datasets():

    print("Processing UraLex data...")
    uralexdir = os.path.join(ANALYSIS_FOLDER,URALEX_BASE)
    try:
        os.makedirs(uralexdir, exist_ok=True)
    except OSError:
        print("Failed to create folder %s." % uralexdir)
        exit(1)
    uralexdata = os.path.join(MATERIALS_FOLDER,URALEX_FOLDER,"cldf")
    run_tiger(uralexdata,URALEX_TIGER_PARAMS,outfile=os.path.join(uralexdir,URALEX_BASE))
    cldf_to_harvest(uralexdir, uralexdata)
    calculate_delta_and_q(os.path.join(uralexdir,"uralex.csv"))
    harvest_to_nexus(uralexdir, os.path.join(uralexdir, "uralex.csv"))
    
    print("Done.")    

    print("Processing swamp data...")
    swampdir = os.path.join(ANALYSIS_FOLDER,SWAMP_BASE)
    for i in sorted(glob.glob(os.path.join(swampdir,"*.csv"))):
        run_tiger(i,["-f","harvest","-n"])
        if os.path.isfile(os.path.join(swampdir,"splitstree_input.nex")) == False: # only create for first file
            harvest_to_nexus(swampdir, i)
        calculate_delta_and_q(i)

    print("Processing dialect chain data...")
    dialectdir = os.path.join(ANALYSIS_FOLDER,DIALECT_BASE)
    for i in sorted(glob.glob(os.path.join(dialectdir,"*.csv"))):
        run_tiger(i,["-f","harvest","-n"])
        if os.path.isfile(os.path.join(dialectdir,"splitstree_input.nex")) == False: # only create for first file
            harvest_to_nexus(dialectdir, i)
        calculate_delta_and_q(i)

    print("Processing harvest data...")
    harvestdir = os.path.join(ANALYSIS_FOLDER,HARVEST_BASE)
    for i in sorted(glob.glob(os.path.join(harvestdir,"*.csv"))):
        run_tiger(i,["-f","harvest","-n"])
        if os.path.isfile(os.path.join(harvestdir,"splitstree_input.nex")) == False: # only create for first file
            harvest_to_nexus(harvestdir, i)
        calculate_delta_and_q(i)

    print("Processing borrowing data...")
    for borrowing_rate in (0.05, 0.10, 0.15, 0.20):
        BASE = BORROWING_BASE + ("_%02d" % int(100*borrowing_rate))
        borrowingdir = os.path.join(ANALYSIS_FOLDER,BASE)
        for i in sorted(glob.glob(os.path.join(borrowingdir,"*.csv"))):
            run_tiger(i,["-f","harvest","-n"])
            if os.path.isfile(os.path.join(borrowingdir,"splitstree_input.nex")) == False: # only create for first file
                harvest_to_nexus(borrowingdir, i)
            calculate_delta_and_q(i)

def explore_parameter_space():

    dirname = "param_exploration"

    # Create output directories
    for name in ("swamp", "chain", "tree"):
        subdirname = os.path.join(dirname, name)
        try:
            os.makedirs(subdirname, exist_ok=True)
        except OSError:
            print("Failed to create folder %s." % subdirname)
            exit(1)

    # Do swamp and chain model exploration
    print("Exploring swamp and chain model parameter spaces...")

    for taxa_count in (10, 25, 50, 100, 250, 500):
        for i, alpha in enumerate((0.25, 0.5, 0.75, 1.0, 1.5, 2.0, 3.0, 5.0)):
            basename = "{}_taxa_alpha_{}".format(taxa_count, i)

            for i in range(N_EXPLORE_REPS):
                if taxa_count == 10:
                    dist = scipy.stats.binom(taxa_count, 0.33)
                else:
                    p = max(random.normalvariate(0.33, 0.1), 0.13)
                    dist = scipy.stats.binom(taxa_count, p)

                for name, Simulator in zip(("swamp", "chain"), (SwampSimulator, ChainSimulator)):
                    subdirname = os.path.join(dirname, name)
                    simulator = Simulator(taxa_count, 200, alpha, dist)
                    while True:
                        try:
                            data = simulator.generate_data()
                            break
                        except ValueError:
                            pass
                    output = data.format_output()
                    filename = os.path.join(subdirname,basename + "_" + str(i+1).zfill(len(str(N_EXPLORE_REPS))) + ".csv")
                    write_lines_to_file(output, filename)

    for name in ("swamp", "chain"):
        subdirname = os.path.join(dirname, name)
        for filename in sorted(glob.glob(os.path.join(subdirname,"*.csv"))):
            run_tiger(filename,["-f","harvest","-n"])

    # Tree model
    print("Exploring tree model parameter space...")

    subdirname = os.path.join(dirname, "tree")
    theta = 10**0.5 # (square root of 10)
    for taxa_count in (10, 25, 50, 100, 250, 500):
        for i, relative_cognate_br in enumerate((theta**x for x in range(-6, 7))):
            basename = "{}_taxa_br_{}".format(taxa_count, i)
            run_tree_model(subdirname, basename, taxa_count, features=200, cognate_birthrate=relative_cognate_br, repetitions=N_EXPLORE_REPS)
    for filename in sorted(glob.glob(os.path.join(subdirname,"*.csv"))):
        run_tiger(filename,["-f","harvest","-n"])

def gap_test():
    code,out,err = run([PYTHON_CMD, "make_gaps.py"])
    print(err.decode("utf-8"), file=sys.stderr)
        
if __name__ == '__main__':

    download_and_extract(URALEX_URL, URALEX_ZIP, MATERIALS_FOLDER)
    download_and_extract(TIGER_URL, TIGER_ZIP, MATERIALS_FOLDER)

    generate_synthetic_datasets()
    analyse_all_datasets()
    explore_parameter_space()
    gap_test()

    print("Tabulating agreements with simulations...")
    make_tables()
        
    print("Plotting results...")
    make_plots()
