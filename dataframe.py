import random
import sys

import scipy.stats

def read_from_stdin():
    """Read language data from stdin in .csv format."""

    simulated_data = DataFrame()
    header = sys.stdin.readline()
    header = header.strip().split(",")
    assert header[0] == "iso"
    fnames = header[1:]
    uniqs = []
    for line in sys.stdin:
        line = line.strip().split(",")
        iso, values = line[0], line[1:]
        simulated_data.data[iso] = {}
        for field, value in zip(fnames, values):
            simulated_data.data[iso][field] = value
            if value != "?" and value not in uniqs:
                uniqs.append(value)
    if len(uniqs) == 2:
        simulated_data.datatype = "binary"
    else:
        simulated_data.datatype = "multi"
    return simulated_data

def read_from_beast_xml(filename):
    """Read an XML file produced by a BEAST simulation."""

    simulated_data = DataFrame()
    fp = open(filename,"r")
    for line in fp:
        if "sequence" in line:
            row = {}
            junk, jank, lang, data = line.strip().split()
            iso = lang[7:-1]  
            data = data[7:-3]
            if "," in data:
                data = data.split(",")
            for f,d in enumerate(data):
                row["f%03d" % f] = d
            simulated_data.data[iso] = row
    return simulated_data

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

    def duplication(self, countrate, degree, fidelity, probabilistic_degree=False):
        """Duplicate some features, either deterministically or stochastically."""
        # Choose the features to duplicate
        iso_codes = list(self.data.keys())
        print(iso_codes[0])
        print(self.data[iso_codes[0]])
        fnames = list(self.data[iso_codes[0]].keys())
        if float(countrate).is_integer():
            ## Deterministic number of duped features
            count = int(countrate)
            duplicated_features = random.sample(fnames, count)
        else:
            ## Probabilistic number of duped features, defined by rate
            prob = float(countrate)
            duplicated_features = [f for f in fnames if random.random() <= prob]

        # Choose the number of times to duplicate each feature
        if probabilistic_degree:
            duplication_counts = [1+n for n in scipy.stats.poisson.rvs(degree-1,loc=0,size=len(duplicated_features))]
        else:
            duplication_counts = [degree for i in duplicated_features]

        # Perform the duplication
        ## Random and probably unique ID for this run
        ## (different for each harvest in a pipeline)
        uid = "".join(random.sample("abcdefghijklmnopqrstuvwxyz",3))
        for df,count in zip(duplicated_features, duplication_counts):
            ## Get the empirical distribution if needed
            if self.datatype == "multi":
                empirical= [self.data[i][df] for i in iso_codes]
            for n in range(0,count):
                for iso in self.data:
                    if self.datatype == "binary":
                        ## Binary duplication
                        ## If we don't match, just take the opposite vlaue
                        if random.random() < fidelity:
                            dup = self.data[iso][df]
                        else:
                            dup = {"0":"1", "1":"0"}[self.data[iso][df]]
                    elif self.datatype == "multi":
                        if random.random() < fidelity:
                            dup = self.data[iso][df]
                        else:
                            dup = random.sample(empirical,1)[0]
                    self.data[iso][df+"_dup_%s_%03d" % (uid,n)] = dup

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
                else:
                    borrowable_values.append(self.data[iso][f])
            for iso in borrowers:
                self.data[iso][f] = random.sample(borrowable_values,1)[0]

    def remove(self, removal_rate):
        """Randomly remove some datapoints (replacing them wiht '?') so that the dataset has the specified rate of missing data."""
        iso_codes = list(self.data.keys())
        fnames = self.data[iso_codes[0]].keys()
        n = len(iso_codes) * len(fnames)
        to_kill = int(removal_rate*n)
        for i in range(0, to_kill):
            while True:
                iso = random.sample(iso_codes,1)[0]
                fname = random.sample(fnames,1)[0]
                if self.data[iso][fname] != "?":
                    self.data[iso][fname] = "?"
                    break
