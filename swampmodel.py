#!/usr/bin/python3

import string
import scipy
import numpy

import dataframe

class MarshGenerator():
    
    _nfeatures = 0
    _ntaxa = 0
    _taxon_namelen = 0
    _model = None

    def __init__(self, nfeatures = 0, ntaxa = 0, taxon_namelen = 3, model=None):
        assert isinstance(nfeatures,int),"nfeatures must be an integer"
        assert isinstance(ntaxa,int),"ntaxa must be an integer"
        assert isinstance(taxon_namelen,int),"taxon_namelen must be an integer"
        assert taxon_namelen > 0, "taxon name length must be 1 or more"
        assert ntaxa > 0, "ntaxa must be 1 or more"
        assert nfeatures > 0, "nfeatures must be 1 or more"
        self._nfeatures = nfeatures
        self._ntaxa = ntaxa
        self._taxon_namelen = taxon_namelen
        if model == None:
            # Default model
            model = { "type": "simple" }
        if "min" not in model.keys():
            model["min"] = 1
        if "max" not in model.keys():
            model["max"] = self._ntaxa
        if "samples" not in model.keys():
            model["samples"] = 10
        self.assertModel(model)
        self._model = model

    def assertModel(self,model):
        assert (model["type"] in ("simple","poisson")), "Unrecognized model"
        if model["type"] == "poisson":
            assert isinstance(model["lambda"],int), "Lambda must be an integer"
            assert isinstance(model["samples"],int), "Samples must be an interger"
        elif model["type"] == "simple":            
            assert isinstance(model["min"],int),"Model parameter 'min' must be an integer"
            assert isinstance(model["max"],int),"Model parameter 'max' must be an integer"
            assert model["min"] <= model["max"], "Model parameter 'min' cannot exceed 'max'"
            assert model["max"] <= self._ntaxa, "Model parameter 'max' cannot exceed 'ntaxa'"

    def generate_data(self):
        taxa = self._generateTaxa()
        alignment = self._generateAlignment()
        features = self._generateFeatureNames()
        data = dataframe.DataFrame()
        for taxon, values in zip(taxa, alignment):
            if taxon not in data.data:
                data.data[taxon] = {}
            assert len(values) == len(features)
            for feature, value in zip(features, values):
                data.data[taxon][feature] = value
        return data
        
    def _generateTaxa(self):
        taxa = []
        for i in range(self._ntaxa):
            current = self._generateTaxon()
            while current in taxa:
                current = self._generateTaxon()
            taxa.append(current)
        return taxa
    
    def _generateTaxon(self):
        taxon = ""
        for i in range(self._taxon_namelen):
            taxon += numpy.random.choice(list(string.ascii_lowercase))
        return taxon

    def _generateAlignment(self):
        output = []
        for i in range(self._ntaxa):
            output.append([])

        # Get appropriate distribution
        if self._model["type"] == "simple":
            dist = scipy.stats.randint(self._model["min"],self._model["max"] + 1)
        if self._model["type"] == "poisson":
            dist = scipy.stats.poisson(self._model["lambda"])

        # Generate cognate class counts
        feature_sizes = dist.rvs(self._nfeatures)
        test_counter = int(self._model["samples"])
        while 0 in feature_sizes:
            feature_sizes = dist.rvs(self._nfeatures)
            test_counter -= 1
            if test_counter == 0:
                print("Could not generate a suitable sample of features with " + str(self._model["samples"]) + " sampling attempts. Try different parameters, or increase the number of sampling attempts.")
                exit(1)

        # Assign taxa to cognate classes
        for i in range(self._nfeatures):
            classes = feature_sizes[i]
            cognates = range(classes)
            for j in range(self._ntaxa):
                output[j].append(numpy.random.choice(cognates))
        return output

    
    def _generateFeatureNames(self):
        output = []
        for i in range(1,self._nfeatures+1):
            output.append("f" + str(i).zfill(len(str(self._nfeatures))))
        return output
    
    def __del__(self):
        pass
