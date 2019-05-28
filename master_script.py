#!/usr/bin/python3

# Download the necessary files
# Generate and analyze samples
# Produce plots and CSVs

import urllib.request
import zipfile
import os
import glob
import subprocess

MATERIALS_FOLDER = 'materials'
ANALYSIS_FOLDER  = 'analyses'
PYTHON_CMD       = 'python3'
URALEX_URL       = 'https://zenodo.org/record/1459402/files/lexibank/uralex-v1.0.zip?download=1'
URALEX_ZIP       = "uralex-v1.0.zip"
URALEX_FOLDER    = "lexibank-uralex-efe0a73"
TIGER_URL        = 'https://github.com/kasyrj/tiger-calculator/archive/9671dc0ac7283ee87bebc5fc18f63d6c8bc91baf.zip'
TIGER_ZIP        = "tiger-calculator.zip"
TIGER_FOLDER     = "tiger-calculator-9671dc0ac7283ee87bebc5fc18f63d6c8bc91baf"
N_REPETITIONS    = 1
SWAMP_BASE       = 'swamp'
SWAMP_PARAMS     = ["-m", "swamp", "-p", "min=1", "max=10"]
DIALECT_BASE     = 'dialect'
DIALECT_PARAMS   = ["-m", "chain"]
BORROWING_BASE   = 'borrowing'
BORROWING_PARAMS = ["-m", "dollo", "-b" "0.3"]
HARVEST_BASE     = 'harvest'
HARVEST_PARAMS = ["-m", "dollo"]

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

    
def run_generator_with_params(output_directory,filebase,params):
    try:
        os.mkdir(output_directory)
    except OSError:
        print("Failed to create folder %s." % output_directory)
        exit(1)

    for i in range(N_REPETITIONS):
        code,out,err = run([PYTHON_CMD, "generate.py"] + params)
        write_lines_to_file(out.decode("utf-8"), os.path.join(output_directory,filebase + "_" + str(i+1).zfill(len(str(N_REPETITIONS))) + ".csv"))

def run_tiger(filename,params):
    params = params + [filename]
    tigercmd = os.path.join(MATERIALS_FOLDER,TIGER_FOLDER, "tiger-calculator.py")
    code,out,err = run([PYTHON_CMD, tigercmd] + params)
    print(err.decode("utf-8"))
    write_lines_to_file(out.decode("utf-8"), filename + "_rates.txt")

        
if __name__ == '__main__':

    download_and_extract(URALEX_URL, URALEX_ZIP, MATERIALS_FOLDER)
    download_and_extract(TIGER_URL, TIGER_ZIP, MATERIALS_FOLDER)
    
    print ("Creating analysis folder...")
    if os.path.exists(ANALYSIS_FOLDER):
        print("Folder %s already exists. Remove or rename it to proceed." % ANALYSIS_FOLDER)
        exit(1)
    try:
        os.mkdir(ANALYSIS_FOLDER)
    except OSError:
        print("Failed to create folder %s." % ANALYSIS_FOLDER)
        exit(1)

    print("Successfully created folder %s" % ANALYSIS_FOLDER)

    print("Calculating TIGER rates for UraLex dataset...")
    print("Done.")

    print("Generating swamp data...")
    swampdir = os.path.join(ANALYSIS_FOLDER,SWAMP_BASE)
    run_generator_with_params(output_directory=swampdir, filebase=SWAMP_BASE, params=SWAMP_PARAMS)
    print("Done.")

    print("Generating dialect chain data...")
    dialectdir = os.path.join(ANALYSIS_FOLDER,DIALECT_BASE)
    run_generator_with_params(output_directory=dialectdir, filebase=DIALECT_BASE, params=DIALECT_PARAMS)
    print("Done.")

    print("Generating harvest data with borrowing...")
    borrowingdir = os.path.join(ANALYSIS_FOLDER,BORROWING_BASE)
    run_generator_with_params(output_directory=borrowingdir, filebase=BORROWING_BASE, params=BORROWING_PARAMS)
    print("Done.")

    print("Generating harvest data...")
    harvestdir = os.path.join(ANALYSIS_FOLDER,HARVEST_BASE)
    run_generator_with_params(output_directory=harvestdir, filebase=HARVEST_BASE, params=HARVEST_PARAMS)
    print("Done.")

    print("Running TIGER for swamp data...")
    for i in glob.glob(os.path.join(swampdir,"*.csv")):
        run_tiger(i,["-f","harvest"])

    print("Running TIGER for dialect chain data...")
    for i in glob.glob(os.path.join(dialectdir,"*.csv")):
        run_tiger(i,["-f","harvest"])

    print("Running TIGER for borrowing data...")
    for i in glob.glob(os.path.join(borrowingdir,"*.csv")):
        run_tiger(i,["-f","harvest"])

    print("Running TIGER for harvest data...")
    for i in glob.glob(os.path.join(harvestdir,"*.csv")):
        run_tiger(i,["-f","harvest"])





