import pdb
import scipy.stats
import numpy as np

# Attempt to fit various scipy-supported discrete probability distributions to
# UraLex cognate class data, so we can simulate UraLex-like data better.

N=26

# First, try to fit a Dirichlet alpha to match Uralex's value of "mean_max_props", 
# the mean value over all meanings of the proportion of languages which have the
# most common cognate class.

# Load the empirical cognate class count distributions
cognate_counts = []
with open("uralex_counts.csv","r") as fp:
    for line in fp:
        meaning, cognates = line.strip().split(",")
        cognate_counts.append(int(cognates))

# Compute the empirical mean_meax_prob
max_props = []
with open("uralex_max_props.csv","r") as fp:
    for line in fp:
        max_props.append(float(line))
mean_max_props = sum(max_props) / len(max_props)

# Define a function to estimate mean_max_prob for a given value of alpha, via simulation

def estimate_mean_max_prop(alpha):
    sim_max_props = []
    for i in range(0,250):
        for count in cognate_counts:
            multinomial_probs = scipy.stats.dirichlet.rvs(alpha=[alpha]*count)[0]
            multinomial_counts = scipy.stats.multinomial.rvs(n=N,p=multinomial_probs)
            max_prop = max(multinomial_counts)/N
            sim_max_props.append(max_prop)
    return sum(sim_max_props) / len(sim_max_props)

# Use grid search with ever reducing step size to identify the best alpha

print("Fitting alpha...")

best_alpha = 5.5
mean_sim_max_props = estimate_mean_max_prop(best_alpha)
best_delta = abs(mean_sim_max_props - mean_max_props)
step = 1.0
for i in range(0, 6):
    candidates = [best_alpha + k*step for k in range(-5,6)]
    for alpha in candidates:
        try:
            mean_sim_max_props = estimate_mean_max_prop(alpha)
            delta = abs(mean_sim_max_props - mean_max_props)
            if delta < best_delta:
                best_delta = delta
                best_alpha = alpha
        except ValueError:
            # Happens for very small alphas
            continue
    step /= 10

print("Best alpha: ", str(best_alpha))

# Second, try to fit various parametric probability distributions to Uralex's
# distribution of cognate class counts.
# Bafflingly, scipy only supports fitting continuous distributions, so here's
# some ugly, slow, redundant code to do the fitting ourselves.
# All likelihoods below are log likelihoods

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

# Fit and compare all families
best_lh = -999999999999999999

print("Fitting binomial...")
rate, lh = fit_binomial(cognate_counts)
if lh > best_lh:
    best_lh = lh
    best_family = "Binomial"
    best_params = rate

print("Fitting negative binomial...")
params, lh = fit_nbinomial(cognate_counts)
if lh > best_lh:
    best_lh = lh
    best_family = "Negative binomial"
    best_params = params

print("Fitting Poisson...")
rate, lh = fit_poisson(cognate_counts)
if lh > best_lh:
    best_lh = lh
    best_family = "Poisson"
    best_params = rate

print("Best fitting distribution is: ", best_family, best_params)
