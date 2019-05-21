#!/usr/bin/python3

import random
import string
import scipy

class MarshData():
    _taxa = None
    _alignment = None
    _features = None
    
    def __init__(self,taxa,alignment,features):
        self._taxa = taxa
        self._alignment = alignment
        self._features = features
    def __del__(self):
        pass
    
    def print(self,style='csv'):
        if style == 'csv':
            self._print_csv()

    def _print_csv(self):
        output = []
        line = "name,"
        for f in self._features:
            line += f + ","
        line = line[:-1]
        output.append(line)
        for i in range(len(self._taxa)):
            line = self._taxa[i] + ","
            for cognate in self._alignment[i]:
                line += str(cognate) + ","
            line = line[:-1]
            output.append(line)
        for line in output:
            print(line)

class MarshGenerator():
    
    _nfeatures = 0
    _ntaxa = 0
    _random_seed = None
    _taxon_namelen = 0
    _model = None

    def __init__(self, nfeatures = 0, ntaxa = 0, random_seed = None, taxon_namelen = 0, model=None):
        assert isinstance(nfeatures,int),"nfeatures must be an integer"
        assert isinstance(ntaxa,int),"ntaxa must be an integer"
        assert isinstance(taxon_namelen,int),"taxon_namelen must be an integer"
        assert taxon_namelen > 0, "taxon name length must be 1 or more"
        assert ntaxa > 0, "ntaxa must be 1 or more"
        assert nfeatures > 0, "nfeatures must be 1 or more"
        random.seed(random_seed)
        self._random_seed = random_seed
        self._nfeatures = nfeatures
        self._ntaxa = ntaxa
        self._taxon_namelen = taxon_namelen
        self.assertModel(model)
        self._model = model

    def assertModel(self,model):
        assert (model["type"] in ("simple","poisson")), "Unrecognized model"
        if model["type"] == "poisson":
            assert isinstance(model["lambda"],int), "Lambda must be an integer"
        elif model["type"] == "simple":
            assert isinstance(model["min"],int),"Model parameter 'min' must be an integer"
            assert isinstance(model["max"],int),"Model parameter 'max' must be an integer"
            assert model["min"] <= model["max"], "Model parameter 'min' cannot exceed 'max'"
            assert model["max"] <= self._ntaxa, "Model parameter 'max' cannot exceed 'ntaxa'"

    def generate(self):
        taxa = self._generateTaxa()
        alignment = self._generateAlignment()
        features = self._generateFeatureNames()
        m = MarshData(taxa,alignment,features)
        return m
        
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
            taxon += random.choice(string.ascii_lowercase)
        return taxon

    def _generateAlignment(self):
        if self._model["type"] == "simple":
            return self._generateSimpleAlignment()
        if self._model["type"] == "poisson":
            return self._generatePoissonAlignment()
    
    def _generateSimpleAlignment(self):
        output = []
        for i in range(self._ntaxa):
            output.append([])
        for i in range(self._nfeatures):
            classes = random.randint(self._model["min"],self._model["max"])
            cognates = range(classes)
            for j in range(self._ntaxa):
                output[j].append(random.choice(cognates))
        return output

    def _generatePoissonAlignment(self):
        output = []
        for i in range(self._ntaxa):
            output.append([])
        feature_sizes = list(scipy.random.poisson(self._model["lambda"],self._nfeatures))
        print(feature_sizes)
        for i in range(self._nfeatures):
            classes = feature_sizes[i]
            cognates = range(classes)
            for j in range(self._ntaxa):
                output[j].append(random.choice(cognates))
        return output

    
    def _generateFeatureNames(self):
        output = []
        for i in range(1,self._nfeatures+1):
            output.append("f" + str(i).zfill(len(str(self._nfeatures))))
        return output
    
    def __del__(self):
        pass
