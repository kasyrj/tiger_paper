#!/usr/bin/python3

# Download the necessary files
# Generate and analyze samples
# Produce plots and CSVs

import urllib.request
import zipfile
import sys
import os
import glob
import subprocess

MATERIALS_FOLDER    = 'materials'
ANALYSIS_FOLDER     = 'analyses'
PYTHON_CMD          = 'python3'
URALEX_URL          = 'https://zenodo.org/record/1459402/files/lexibank/uralex-v1.0.zip?download=1'
URALEX_ZIP          = "uralex-v1.0.zip"
URALEX_FOLDER       = "lexibank-uralex-efe0a73"
TIGER_URL           = 'https://github.com/kasyrj/tiger-calculator/archive/91b4509615bb91441f51eb4f8f1974dca01814dc.zip'
TIGER_ZIP           = "tiger-calculator.zip"
TIGER_FOLDER        = "tiger-calculator-91b4509615bb91441f51eb4f8f1974dca01814dc"
N_REPETITIONS       = 2
URALEX_BASE         = "uralex"
SWAMP_BASE          = 'swamp'
SWAMP_PARAMS        = ["-m", "swamp", "-p", "type=negbinom", "alpha=0.9", "sampling=1000000"]
DIALECT_BASE        = 'dialect'
DIALECT_PARAMS      = ["-m", "chain", "-c", "2.0", "-B", "5.0"]
BORROWING_BASE      = 'borrowing'
BORROWING_PARAMS    = ["-m", "dollo", "-c", "2.0", "-B", "0.3"]
HARVEST_BASE        = 'pure_tree'
HARVEST_PARAMS      = ["-m", "dollo", "-c", "2.0"]
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

    
def run_generator_with_params(output_directory,filebase,params):
    try:
        os.mkdir(output_directory)
    except OSError:
        print("Failed to create folder %s." % output_directory)
        exit(1)

    params = ["-l",  "26", "-f", "313"] + params
    for i in range(N_REPETITIONS):
        code,out,err = run([PYTHON_CMD, "generate.py"] + params)
        print(err.decode("utf-8"), file=sys.stderr)
        write_lines_to_file(out.decode("utf-8"), os.path.join(output_directory,filebase + "_" + str(i+1).zfill(len(str(N_REPETITIONS))) + ".csv"))

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

    print("Generating swamp data...")
    swampdir = os.path.join(ANALYSIS_FOLDER,SWAMP_BASE)
    run_generator_with_params(output_directory=swampdir, filebase=SWAMP_BASE, params=SWAMP_PARAMS)
    print("Done.")

    print("Generating dialect chain data...")
    dialectdir = os.path.join(ANALYSIS_FOLDER,DIALECT_BASE)
    run_generator_with_params(output_directory=dialectdir, filebase=DIALECT_BASE, params=DIALECT_PARAMS)
    print("Done.")

    print("Generating harvest data with borrowing...")
    for borrowing_rate in (0.05, 0.10, 0.15, 0.20):
        BASE = BORROWING_BASE + ("_%02d" % int(100*borrowing_rate))
        borrowingdir = os.path.join(ANALYSIS_FOLDER,BASE)
        PARAMS = HARVEST_PARAMS + ["-B",str(borrowing_rate)]
        print(borrowingdir, BASE, PARAMS)
        run_generator_with_params(output_directory=borrowingdir, filebase=BASE, params=PARAMS)
    print("Done.")

    print("Generating harvest data...")
    harvestdir = os.path.join(ANALYSIS_FOLDER,HARVEST_BASE)
    run_generator_with_params(output_directory=harvestdir, filebase=HARVEST_BASE, params=HARVEST_PARAMS)
    print("Done.")

    print("Processing UraLex data...")
    uralexdir = os.path.join(ANALYSIS_FOLDER,URALEX_BASE)
    try:
        os.mkdir(uralexdir)
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
    for i in sorted(glob.glob(os.path.join(swampdir,"*.csv"))):
        run_tiger(i,["-f","harvest","-n"])
        if os.path.isfile(os.path.join(swampdir,"splitstree_input.nex")) == False: # only create for first file
            harvest_to_nexus(swampdir, i)
        calculate_delta_and_q(i)

    print("Processing dialect chain data...")
    for i in sorted(glob.glob(os.path.join(dialectdir,"*.csv"))):
        run_tiger(i,["-f","harvest","-n"])
        if os.path.isfile(os.path.join(dialectdir,"splitstree_input.nex")) == False: # only create for first file
            harvest_to_nexus(dialectdir, i)
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

    print("Processing harvest data...")
    for i in sorted(glob.glob(os.path.join(harvestdir,"*.csv"))):
        run_tiger(i,["-f","harvest","-n"])
        if os.path.isfile(os.path.join(harvestdir,"splitstree_input.nex")) == False: # only create for first file
            harvest_to_nexus(harvestdir, i)
        calculate_delta_and_q(i)

    print("Plotting results...")
    run([PYTHON_CMD, "make_plots.py"])
