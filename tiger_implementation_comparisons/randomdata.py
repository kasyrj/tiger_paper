#!/usr/bin/python3
#
# make random nucleotide data and save it as FASTA and PHYLIP

import random
import string

def getName(length):
    return "".join(random.choices(string.ascii_lowercase,k=length))

def getAlignment(length):
    return random.choices(["A","T","G","C"], k=length)

def getData(namelen,ntaxa,nchars):
    data = {}
    names = []
    for i in range(ntaxa):
        name = getName(namelen)
        while name in data.keys():
            name = getName(namelen)
        data[name] = getAlignment(nchars)
    return data

def makeFiles(data):
    phylip = []
    fasta = []
    outline = ""
    phylip.append(str(len(data)) + " " + str(len(data[list(data.keys())[0]])))
    for i in sorted(data.keys()):
        fasta.append(">" + i)
        fasta.append("".join(data[i]))
        phylip.append(i + " " + "".join(data[i]))
    with open("sampledata.fasta", "w") as f:
        for line in fasta:
            f.write(str(line) + "\n")
        f.close()
    with open("sampledata.phylip", "w") as f:
        for line in phylip:
            f.write(str(line) + "\n")
        f.close()

random.seed(1234)

ntaxa = 20
chars = 500
namelen = 3

makeFiles(getData(namelen,ntaxa,chars))
#for i in range(ntaxa):
#    print(getName(namelen))
#    print(getAlignment(chars))
