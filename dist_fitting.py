import pdb
import scipy.stats

# Attempt to fit various scipy-supported discrete probability distributions to
# UraLex cognate class count data, so we can simulate UraLex-like data better.
# Bafflingly, scipy only supports fitting continuous distributions, so here's
# some ugly, slow, redundant code to do the fitting ourselves.  All likelihoods
# are log likelihoods.

# First, read the cognate class counts
cognate_counts = []
with open("uralex_counts.csv","r") as fp:
    for line in fp:
        meaning, cognates = line.strip().split(",")
        cognate_counts.append(int(cognates))

max_props = []
with open("uralex_max_props.csv","r") as fp:
    for line in fp:
        max_props.append(float(line))
mean_max_props = sum(max_props) / len(max_props)

# First, try to fit Dirichlet alpha so as to match mean max_props
N=26
best_delta = 9999999
# Rough initial fit
for alpha in (0.01, 0.1,0.8, 0.9, 1.0, 1.1, 1.2, 10.0,100.0,1000):
    sim_max_props = []
    for i in range(0,10):
        for count in cognate_counts:
            multinomial_probs = scipy.stats.dirichlet.rvs(alpha=[alpha]*count)[0]
            multinomial_counts = scipy.stats.multinomial.rvs(n=N,p=multinomial_probs)
            max_prop = max(multinomial_counts)/N
            sim_max_props.append(max_prop)
    mean_sim_max_props = sum(sim_max_props) / len(sim_max_props)
    delta = abs(mean_sim_max_props - mean_max_props)
    if delta < best_delta:
        best_delta = delta
        best_alpha = alpha
print("Alpha: ", best_alpha)

# Functions to fit a
# Binomial distribution (N is fixed to number of languages in UraLex, so the
# maximum possible number of cognates is automatically enforced.  Only p is
# fit).

def get_binomial_likelihood(rate, cognate_counts):
    N = 26
    binomial = scipy.stats.binom(N, rate)
    log_lh = 0
    for count in cognate_counts:
        log_lh += binomial.logpmf(min(N,count))
    return log_lh

def fit_binomial(cognate_counts):
    best_lh = -999999999999999999999999
    for step in range(0, 100):
        rate = step*0.01
        lh = get_binomial_likelihood(rate, cognate_counts)
        if lh > best_lh:
            best_rate, best_lh = rate, lh
    return best_rate, best_lh

# Functions to fit a
# Negative binomial distribution (Both r and p are fit).

def get_nbinomial_likelihood(r, p, cognate_counts):
    nbinomial = scipy.stats.nbinom(r, p)
    lh = 0
    for count in cognate_counts:
        lh += nbinomial.logpmf(count)
    return lh

def fit_nbinomial(cognate_counts):
    best_lh = -999999999999999999999999
    for step in range(0, 100):
        p = step*0.01
        for n in range(0,30):
            lh = get_nbinomial_likelihood(n, p, cognate_counts)
            if lh > best_lh:
                best_n, best_p, best_lh = n, p, lh
    return (best_n, best_p), best_lh

# Functions to fit a
# Poisson distribution.

def get_poisson_likelihood(rate, cognate_counts):
    poisson = scipy.stats.poisson(rate)
    lh = 0
    for count in cognate_counts:
        lh += poisson.logpmf(count)
    return lh

def fit_poisson(cognate_counts):
    best_lh = -999999999999999999999999
    # Fit to nearest integer
    for rate in range(1, 30):
        lh = get_poisson_likelihood(rate, cognate_counts)
        if lh > best_lh:
            best_rate, best_lh = rate, lh
    # Refine to two DPs
    min_rate = best_rate -1
    for step in range(0, 200):
        rate = min_rate + step*0.01
        lh = get_poisson_likelihood(rate, cognate_counts)
        if lh > best_lh:
            best_rate, best_lh = rate, lh
    return best_rate, best_lh

# Fit all families
rate, lh = fit_binomial(cognate_counts)
print("Binomial: ", rate, lh)

params, lh = fit_nbinomial(cognate_counts)
print("Negative binomial: ", params, lh)

rate, lh = fit_poisson(cognate_counts)
print("Poisson: ", rate, lh)
