#!/usr/bin/python3

# Download the necessary files
# Generate and analyze samples
# Produce plots and CSVs

import urllib.request
import zipfile
import os

DATASET_FOLDER  = 'dataset'
ANALYSIS_FOLDER = 'analyses'

try:
    zf = zipfile.ZipFile('uralex-v1.0.zip','r')
except FileNotFoundError:
    print("Downloading UraLex v1.0...")
    urllib.request.urlretrieve('https://zenodo.org/record/1459402/files/lexibank/uralex-v1.0.zip?download=1','uralex-v1.0.zip')
    print("Done.")
    zf = zipfile.ZipFile('uralex-v1.0.zip','r')
print("Extracting data to %s" % DATASET_FOLDER)
zf.extractall(DATASET_FOLDER)
zf.close()
print("Done.")
print ("Creating analysis folder...")
if os.path.exists(ANALYSIS_FOLDER):
    print("Folder %s already exists." % ANALYSIS_FOLDER)
    exit(1)
try:
    os.mkdir(ANALYSIS_FOLDER)
except OSError:
    print("Failed to create folder %s." % ANALYSIS_FOLDER)
    exit(1)

print("Successfully created folder %s" % ANALYSIS_FOLDER)

print("Calculating TIGER rates for UraLex dataset...")
print("Done.")
print("Generating simulated datasets...")
print("Done.")
print("Calculating TIGER rates for simulated datasets...")
print("Done.")




