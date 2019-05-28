import random
import sys

import scipy.stats

class DataFrame:

    def __init__(self):
        self.data = {}

    def format_output(self):
        """Return a string containing a .csv file of the data."""
        iso_codes = list(self.data.keys())
        iso_codes.sort()
        fnames = list(self.data[iso_codes[0]].keys())
        fnames.sort()
        lines = []
        lines.append("iso,"+",".join(fnames))
        for iso in iso_codes:
            lines.append(iso + "," + ",".join(map(str,[self.data[iso][f] for f in fnames])))
        return "\n".join(lines)

    def borrow(self, borrowing_rate):
        """Randomly borrow feature values at a certain rate."""
        if borrowing_rate == 0.0:
            return
        iso_codes = list(self.data.keys())
        fnames = list(self.data[iso_codes[0]].keys())
        for f in fnames:
            borrowable_values = []
            borrowers = []
            for iso in iso_codes:
                if random.random() <= borrowing_rate:
                    borrowers.append(iso)
            for iso in borrowers:
                current_value = self.data[iso][f]
                borrowable_values = [self.data[i][f] for i in iso_codes if i!=iso]
                assert current_value not in borrowable_values
                self.data[iso][f] = random.sample(borrowable_values,1)[0]
