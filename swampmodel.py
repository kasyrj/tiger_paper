#!/usr/bin/python3

import string
import scipy
import numpy
import random

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
        if model["type"] == "poisson" and "lambda" not in model:
            model["lambda"] = ntaxa / 2.0
        if "min" not in model:
            model["min"] = 1
        if "max" not in model:
            model["max"] = self._ntaxa
        if "samples" not in model:
            model["samples"] = 10
        if "lambda" in model:
            model["lambda"] = float(model["lambda"])
        if "alpha" in model:
            model["alpha"] = float(model["alpha"])
        else:
            model["alpha"] = 100.0
        self.assertModel(model)
        self._model = model

    def assertModel(self,model):
        assert (model["type"] in ("simple","poisson")), "Unrecognized model"
        if model["type"] == "poisson":
            assert isinstance(model["lambda"],float), "Lambda must be a float"
            assert isinstance(model["samples"],int), "Samples must be an interger"
        elif model["type"] == "simple":            
            assert isinstance(model["min"],int),"Model parameter 'min' must be an integer"
            assert isinstance(model["max"],int),"Model parameter 'max' must be an integer"
            assert model["min"] <= model["max"], "Model parameter 'min' cannot exceed 'max'"
            assert model["max"] <= self._ntaxa, "Model parameter 'max' cannot exceed 'ntaxa'"

    def generate_data(self):
        # Generate data
        taxa = self._generateTaxa()
        alignment = self._generateAlignment()
        features = self._generateFeatureNames()
        # Insert into harvest-style DataFrame
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
        while 0 in feature_sizes or max(feature_sizes) > self._model["max"]:
            feature_sizes = dist.rvs(self._nfeatures)
            test_counter -= 1
            if test_counter == 0:
                print("Could not generate a suitable sample of features with " + str(self._model["samples"]) + " sampling attempts. Try different parameters, or increase the number of sampling attempts.")
                exit(1)

        # Assign taxa to cognate classes
        for classes in feature_sizes:
            # For each meaning, we're going to generate a list `assignments`, which contains one element per language.
            # The elements indicate which cognate class a language is assigned to.
            # E.g. If there were 3 cognate classes for a meaning, and 10 languages, a valid `assignments` might be:
            # assignments = [0, 1, 1, 0, 2, 0, 0, 0, 0, 2]
            # We are generating these knowing only the number of cognates, e.g. 3 above.
            # It is a requirement that each cognate class is represented at least once.  So, we start off `assignments`
            # by sampling each cognate class precisely once (in numeric order, but fear not, all will get shuffled at the end)
            assignments = list(range(classes))
            # Now, we probably need to make some additional assignments.  How many?
            remaining = self._ntaxa - len(assignments)
            if remaining:
                # Now, we don't care, for the remaining assignments, that every cognate class is represented at least once.
                # We can just sample randomly, and add the results to what we already have.  We could just sample uniformly
                # from range(0, classes) (and previously did!), but it's not realistic that all cognate classes are equally
                # sized on average.  So, let's instead sample the remaining assignments from a non-uniform multinomial
                # distribution, which is itself sampled from a symmetric Dirichlet distribution.  By setting the Dirichlet's
                # alpha parameter very high, we can gracefully degrade to the original uniform distribution.
                # First, sample the multinomial probabilities.
                multinomial_probs = scipy.stats.dirichlet.rvs(alpha=[self._model["alpha"]]*classes)[0]
                # Now sample the counts of each class, after making `remaining` draws from the multinomial dist
                multinomial_counts = scipy.stats.multinomial.rvs(n=remaining,p=multinomial_probs)
                # Add the actual assignments to `assignments`
                for j,count in enumerate(multinomial_counts):
                    assignments.extend([j]*count)
            # Shuffle everything as promised earlier
            random.shuffle(assignments)
            # Sanity checks
            assert len(assignments) == self._ntaxa
            assert len(set(assignments)) == classes
            # Add to master output
            for j, x in enumerate(assignments):
                output[j].append(x)
        return output

    def _generateFeatureNames(self):
        output = []
        for i in range(1,self._nfeatures+1):
            output.append("f" + str(i).zfill(len(str(self._nfeatures))))
        return output
    
    def __del__(self):
        pass
