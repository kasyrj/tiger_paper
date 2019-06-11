#!/usr/bin/python3
# Convert harvest csv file to SplitsTree-compatible NEXUS representation

import argparse

PARSER_DESC = "Convert harvest-style CSV to SplitsTree-compatible NEXUS."

class Feature():
    def __init__(self,state,possible_states):
        self._state = state
        self._states = possible_states
        
    def __del__(self):
        pass

    def asBinary(self):
        string = ""
        if self._state == "?":
            string = "?" * len(self._states)
        else:
            for state in self._states:                
                if state == self._state:
                    string += "1"
                else:
                    string += "0"
        return string

    def asMultistate(self):
        return self._state

    def getStates(self):
        return self._states

class DataMatrix():
    _csv = []
    def __init__(self,csv):
        for line in csv:
            self._csv.append(line.strip().rstrip().split(","))
        self._matrix = {}
        for taxon in self.getTaxa():
            self._matrix[taxon] = {}
            for feature in self.getFeatures():
                self._matrix[taxon][feature] = self._makeTaxonFeature(taxon,feature)
    def __del__(self):
        pass
    def getTaxa(self):
        taxa = set()
        for line in self._csv[1:]:
            taxa.add(line[0])
        return sorted(taxa)
    def getFeatures(self):
        return sorted(set(self._csv[0][1:]))
    def _makeTaxonFeature(self,taxon,feature):
        possible_states = set()
        current_state = None
        for i in range(len(self._csv)):
            if i == 0:
                continue
            for j in range(len(self._csv[i])):
                if self._csv[0][j] == feature:
                    possible_states.add(self._csv[i][j])
                    if self._csv[i][0] == taxon:
                        current_state = self._csv[i][j]
        if "?" in possible_states:
            possible_states.remove("?")
        return Feature(current_state,sorted(possible_states,key=int))

    def getTaxonFeature(self,taxon,feature):
        return self._matrix[taxon][feature]

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=PARSER_DESC)

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

    dm = DataMatrix(infile)
    taxlabel_string = ""
    for l in dm.getTaxa():
        taxlabel_string += " " + l
    
    nexus_file = []
    nexus_file.append("#NEXUS")
    nexus_file.append("begin taxa;")
    nexus_file.append("dimensions ntax=" + str(len(dm.getTaxa())) + ";")
    nexus_file.append("taxlabels" + taxlabel_string + ";")
    nexus_file.append("end;")
    nexus_file.append("")
    nexus_file.append("begin characters;")

    chars = ""
    first_taxon = dm.getTaxa()[0]
    for feature in dm.getFeatures():
        chars += dm.getTaxonFeature(first_taxon,feature).asBinary()
        
    nexus_file.append("dimensions nchar=" + str(len(chars)) + ";")
    nexus_file.append('format symbols="01" missing=?;')
    nexus_file.append("matrix")
    for taxon in dm.getTaxa():
        current_line = taxon + " "
        for feature in dm.getFeatures():
            current_line += dm.getTaxonFeature(taxon,feature).asBinary()
        nexus_file.append(current_line)
    nexus_file.append(";")
    nexus_file.append("end;")
    for line in nexus_file:
        print(line)
