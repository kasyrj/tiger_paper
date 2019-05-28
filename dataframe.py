import random
import sys

import scipy.stats

class DataFrame:

    def __init__(self):
        self.data = {}

    def format_output(self):
        """Return a string containing a .csv file of the data."""
        languages = list(self.data.keys())
        languages.sort()
        features = list(self.data[languages[0]].keys())
        features.sort()
        lines = []
        lines.append("language,"+",".join(features))
        for l in languages:
            lines.append(l + "," + ",".join(map(str,[self.data[l][f] for f in features])))
        return "\n".join(lines)

    def borrow(self, borrowing_rate):
        """Randomly borrow feature values at a certain rate."""
        if borrowing_rate == 0.0:
            return
        languages = list(self.data.keys())
        languages.sort()
        features = list(self.data[languages[0]].keys())
        for f in features:
            borrowable_values = []
            borrowers = []
            for l in languages:
                if random.random() <= borrowing_rate:
                    borrowers.append(l)
            for l in borrowers:
                current_value = self.data[l][f]
                borrowable_values = [self.data[l][f] for L in languages if L!=l]
                assert current_value not in borrowable_values
                self.data[l][f] = random.sample(borrowable_values,1)[0]
