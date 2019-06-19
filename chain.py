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
        dist = scipy.stats.nbinom(8, 0.45)

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
            # Do conglomeeraive thing
            segments = [[j]*count for j,count in enumerate(multinomial_counts)]
            while len(segments) > 1:
                random.shuffle(segments)
                a, b = segments.pop(), segments.pop()
                if random.random() < 0.75 or len(a) == len(b) == 1:
                    c = a + b
                else:
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

class OldChainSimulator():
    """Forward direction.
    """

    def __init__(self, n_langs, n_features, cognate_birthrate=0.001, cognate_gamma=1.0, borrowing_rate=0.5):
        self.n_langs = n_langs
        self.n_features = n_features
        self.cognate_birthrate = cognate_birthrate
        self.cognate_gamma = cognate_gamma
        self.borrowing_rate = borrowing_rate

    def generate_data(self):
        """Generate cognate class data in a Dollo-like fashion."""
        self.data = dataframe.DataFrame()
        self.data.datatype = "binary"

        langs = random.sample(dummy_isos, self.n_langs)
        self.langs = langs
        for i in range(0, self.n_features):
            gamma = scipy.stats.gamma(self.cognate_gamma,scale=1.0/self.cognate_gamma).rvs()
            attested_cognates = [1]
            cognates = {}
            for l in langs:
                cognates[l] = 1
            events = []
            t = 0
            while t < 25:
                t += scipy.stats.expon(1/ (gamma * self.cognate_birthrate)).rvs()
                events.append((t,"birth"))
            t = 0
            while t < 25:
                t += scipy.stats.expon(1 / (gamma * self.borrowing_rate)).rvs()
                events.append((t,"borrow"))
            events.sort()
            #print(events)
            for t, event in events:
                if event == "birth":
                    innovator = random.sample(langs, 1)[0]
                    cognates[innovator] = len(attested_cognates) + 1
                    attested_cognates.append(cognates[innovator])
#                    print("language %s has innvoated cognate %d" % (innovator, cognates[innovator]))
                elif event == "borrow":
                    if len(attested_cognates) == 1:
                        continue
                    while True:
                        recipient_index = random.sample(range(0, self.n_langs), 1)[0]
                        if recipient_index == 0:
                            donor_index = recipient_index + 1
                        elif recipient_index == len(langs)-1:
                            donor_index = recipient_index - 1
                        else:
                            if random.random() < 0.5:
                                donor_index = recipient_index + 1
                            else:
                                donor_index = recipient_index - 1
                        recipient, donor = langs[recipient_index], langs[donor_index]
                        if cognates[recipient] < cognates[donor]:
                            break
                    cognates[recipient] = cognates[donor]
#                    print("language %s has borrowed cognate %d from language %s" % (recipient, cognates[recipient], donor))
#            print("---------")
#            for l in langs:
#                print(l, cognates[l])
#            print("---------")
#            print("%d cognates" % len(set(cognates.values())))
            terminal_values = list(cognates.values())
            terminal_values.sort()
            trans = dict([(v,n) for (n,v) in enumerate(terminal_values)])
            for lang, cognate in cognates.items():
                if lang not in self.data.data:
                    self.data.data[lang] = {}
                self.data.data[lang]["f_%03d" % i] = trans[cognate]

        return self.data
