import itertools
import random

import scipy.stats

import dataframe

dummy_isos = set(["".join(chars) for chars in itertools.combinations("abcdefghijklmnopqrstuvwxyz",3)])

class ChainSimulator():

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
