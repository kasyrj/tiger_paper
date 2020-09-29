import itertools
import random

import scipy.stats

import dataframe

dummy_isos = set(["".join(chars) for chars in itertools.combinations("abcdefghijklmnopqrstuvwxyz",3)])

class ChainSimulator():

    def __init__(self, n_langs, n_features, alpha):
        self.n_langs = n_langs
        self.n_features = n_features
        self.alpha = alpha

    def generate_data(self):
        """Generate cognate class data in a Dollo-like fashion."""
        self.data = dataframe.DataFrame()
        self.data.datatype = "binary"

        langs = random.sample(dummy_isos, self.n_langs)
        self.langs = langs
        dist = scipy.stats.nbinom(9, 0.49)

        # Generate cognate class counts
        feature_sizes = dist.rvs(self.n_features)
        test_counter = 100000
        while 0 in feature_sizes or max(feature_sizes) > self.n_langs:
            feature_sizes = dist.rvs(self.n_features)
            test_counter -= 1
            if test_counter == 0:
                print("Could not generate a suitable sample of features with many sampling attempts.")
                exit(1)

        # Assign taxa to cognate classes
        for i, classes in enumerate(feature_sizes):
            # First, sample the multinomial probabilities.
            multinomial_probs = scipy.stats.dirichlet.rvs(alpha=[self.alpha]*classes)[0]
            # Now sample the counts of each class, after making `remaining` draws from the multinomial dist
            # Everything needs to be above zero!
            multinomial_counts = scipy.stats.multinomial.rvs(n=self.n_langs - classes,p=multinomial_probs)
            multinomial_counts = [c+1 for c in multinomial_counts]
            assert sum(multinomial_counts) == self.n_langs
            # Start off by structuring cognate classes as uninterrupted chains of consecutive languages,
            # in random order
            segments = [[j]*count for j,count in enumerate(multinomial_counts)]
            # Now iteratively "merge" classes by either concatenating a random pair or inserting one
            # class into another at a random index class.  This second operation is consistent with the
            # structure of one class "evolving over the top of" some now unobserved portion of a larger
            # other class.
            while len(segments) > 1:
                random.shuffle(segments)
                a, b = segments.pop(), segments.pop()
                if random.random() < 0.75 or len(a) == len(b) == 1:
                    # Concatenate
                    c = a + b
                else:
                    # Insert
                    longest = a if len(a) > len(b) else b
                    shortest = b if len(a) > len(b) else a
                    insertion_index = random.randint(1,len(longest)-1)
                    c = longest[0:insertion_index] + shortest + longest[insertion_index:]
                segments.append(c)
            assignments = segments[0]
            # Sanity checks
            assert len(assignments) == self.n_langs
            assert len(set(assignments)) == classes

            # Store
            for lang, cognate in zip(self.langs, assignments):
                if lang not in self.data.data:
                    self.data.data[lang] = {}
                self.data.data[lang]["f_%03d" % i] = cognate

        return self.data
