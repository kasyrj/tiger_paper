#!/usr/bin/env python3
import glob
from math import log
import os, os.path

import scipy.stats
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import numpy

def cognate_class_count_plot():
    # Actual class counts
    cognate_counts = []
    with open("uralex_counts.csv","r") as fp:
        for line in fp:
            meaning, cognates = line.strip().split(",")
            cognate_counts.append(int(cognates))

    # Best fitting distribution
    nbinom_support = range(0,max(cognate_counts)+2)
    nbinom_probs = [scipy.stats.nbinom(9,0.49).pmf(n) for n in nbinom_support]

    plt.figure(figsize=(12,6))
    fig, ax1 = plt.subplots()
    ax2 = ax1.twinx()

    ax1.hist(cognate_counts,bins=range(1,max(cognate_counts)+2), align="left")
    ax1.set_xticks([5,10,15,20])
    ax1.set_xlim(0,max(cognate_counts)+1.5)
    ax1.set_xlabel("Cognate classes", fontsize=12)
    ax1.set_ylabel("Meanings in UraLex", fontsize=12)
    ax2.stem(nbinom_support,nbinom_probs, linefmt="C1-", markerfmt="C1o")
    a, b = ax2.get_ylim()
    ax2.set_ylim(0.0,b)
    ax2.set_ylabel("Negative binomial probability", fontsize=12)
    plt.tight_layout()
    plt.savefig("plots/cognate_dist.png")

def tiger_rate_dist_plot():
    rates = []
    with open("analyses/uralex/uralex_rates.txt","r") as fp:
        for line in fp:
            rates.extend([float(line.strip().split()[-1])])
    fig, ax = plt.subplots()
    ax.hist(rates,19)
    ax.set_xlabel("TIGER value")
    ax.set_ylabel("Number of meanings")
    plt.tight_layout()
    plt.savefig("plots/uralex_rates_dist.png")

def tiger_rate_plot():
    dfs = []
    data_models = glob.glob("analyses/*")
    data_names = []
    for model in data_models:
        name = os.path.split(model)[-1]
        data_names.append(name)
        rates_files = glob.glob(os.path.join(model, "*rates.txt"))
        rates = []
        for rates_file in rates_files:
            with open(rates_file, "r") as fp:
                rates.extend([float(x.strip().split()[-1]) for x in fp.readlines()])
        df = pd.DataFrame({name: rates})
        dfs.append(df)
    df = pd.concat(dfs)

    data_names.sort(key=lambda x: df[x].mean())

    plt.figure(figsize=(12,12))
    sns.set(style="whitegrid", palette="muted")
    sns.set_context("paper",font_scale=2.0)
    ax = sns.violinplot(data=df,order=list(reversed(data_names)), orient="h")
    ax.set(xlabel='TIGER values')
    ax.set_xticks([0.00, 0.25,0.50,0.75,1.00])
    plt.xticks(rotation=90)
    plt.tight_layout()
    plt.savefig("plots/tiger_rates_plot.png")

def tiger_rates_semantic_categories():
    rates = {}
    categories = {}
    categories["basic"] = []
    categories["non-basic"] = []
    dfs = []
    with open("analyses/uralex/uralex_rates.txt", "r") as fp:
        for line in fp:
            meaning, rate = line.strip().split()
            rates[meaning] = float(rate)
    with open("uralex_supplement.tsv", "r") as fp:
        fp.readline() # headers
        for line in fp:
            meaning, basic, category, rank = line.strip().split()
            if basic == "yes":
                categories["basic"].append(rates[meaning])
            else:
                categories["non-basic"].append(rates[meaning])
            if category not in categories:
                categories[category] = []
            categories[category].append(rates[meaning])
        df = pd.concat([pd.DataFrame({cat:rates}) for cat,rates in categories.items()])

    plt.figure(figsize=(12,12))
    sns.set(style="whitegrid", palette="muted")
    sns.set_context("paper",font_scale=2.0)
    ax = sns.violinplot(data=df, orient="h", scale="count")
    ax.set(xlabel='TIGER values by category')
    ax.set_xticks([0.50,0.75,1.00])
    plt.xticks(rotation=90)
    plt.tight_layout()
    plt.savefig("plots/tiger_rates_plot_2.png")

def metric_comparison_plot():
    x_axis = ["pure_tree","borrowing_05","borrowing_10","borrowing_15","borrowing_20","dialect","swamp","uralex"]
    y_axis = []
    analyses = glob.glob("analyses/*")
    tiger_rates = {}
    qresiduals = {}
    delta_scores = {}
    
    for a in analyses:
        current_analysis = os.path.split(a)[-1]    
        tiger_files = glob.glob(os.path.join(a, "*rates.txt"))
        delta_q_files = glob.glob(os.path.join(a,"*delta_qresidual.txt"))

        tiger_rates[current_analysis] = []
        qresiduals[current_analysis] = []
        delta_scores[current_analysis] = []
        
        for f in tiger_files:
            with open(f, "r") as fp:
                tiger_rates[current_analysis].extend([float(x.strip().split()[-1]) for x in fp.readlines()])

        for f in delta_q_files:
            with open(f, "r") as fp:
                lines = fp.readlines()
                for l in lines[1:]:
                    delta_scores[current_analysis].extend([float(l.strip().split()[1])])
                    qresiduals[current_analysis].extend([float(l.strip().split()[2])])


    sns.set(style="whitegrid", palette="muted")
    sns.set_context("paper",font_scale=1.0)
    
    y_axis = []
    for k in x_axis:
        y_axis.append(numpy.mean(tiger_rates[k]))

    plt.subplot(2,2,1)    
    plt.xticks(rotation=90)
    plt.plot(x_axis[:-1], y_axis[:-1],"bo--")
    plt.plot(x_axis[-1], y_axis[-1],"bx")
    plt.title("TIGER value")

    y_axis = []
    for k in x_axis:
        y_axis.append(numpy.mean(delta_scores[k]))

    plt.subplot(2,2,2)    
    plt.xticks(rotation=90)
    plt.plot(x_axis[:-1], y_axis[:-1],"bo--")
    plt.plot(x_axis[-1], y_axis[-1],"bx")
    plt.title("delta score")

    y_axis = []
    for k in x_axis:
        y_axis.append(numpy.mean(qresiduals[k]))

    plt.subplot(2,2,3)    
    plt.xticks(rotation=90)
    plt.plot(x_axis[:-1], y_axis[:-1],"bo--")
    plt.plot(x_axis[-1], y_axis[-1],"bx")
    plt.title("Q-residual")
    
    plt.tight_layout()
    plt.savefig("plots/metric_comparison_plot.png", dpi=300)

def tiger_rate_cognates_plot():
    rates = {}
    cognates = {}
    with open("analyses/uralex/uralex_rates.txt", "r") as fp:
        for line in fp:
            meaning, rate = line.strip().split()
            rates[meaning] = float(rate)
    with open("uralex_counts.csv","r") as fp: # counts based on minimising strategy
        for line in fp:
            meaning, cognate_count = line.strip().split(",")
            cognates[meaning] = int(cognate_count)
    rates_sorted = []
    cognates_sorted = []
    for k in sorted(rates.keys()):
        rates_sorted.append(rates[k])
        cognates_sorted.append(cognates[k])
    y_axis = range(min(cognates_sorted), max(cognates_sorted)+1)
    fig,ax = plt.subplots()
    sns.set(style="whitegrid", palette="muted")
    sns.set_context("paper",font_scale=2.0)
    plt.tight_layout()
    ax.scatter(rates_sorted, cognates_sorted)
    plt.yticks(y_axis[1::2])
    ax.set_xlabel('TIGER value')
    ax.set_ylabel('Cognate count')
    plt.savefig("plots/tiger_rates_vs_cognates.png")

def _read_param_exp_rates(directory, param_name, param_values):

    # param_values is used to translate the numeric indicies (1, 2, 3,...) used
    # in the filenames of simulated data/TIGER values, into the actual numeric
    # values used
    ids = []
    taxon_counts = []
    params = []
    mean_tigers = []
    for i, filename in enumerate(glob.glob(os.path.join(directory, "*_rates.txt"))):
        print(filename)
        taxa, _, _, param, n = filename.split("/")[-1].split(".")[0].split("_")
        print(taxa, param, n)
        with open(filename, "r") as fp:
            x, N = 0, 0
            for line in fp:
                _, r = line.strip().split("\t")
                x += float(r)
                N += 1
        assert N == 200
        ids.append(i)
        mean_tigers.append(x/N)
        taxon_counts.append(taxa)
        params.append(param_values[int(param)])
    df = pd.DataFrame({"id": ids,
        "taxon_count": taxon_counts,
        param_name: params,
        "mean_tiger": mean_tigers
        })
#    df.to_csv(os.path.join(directory, "param_exp.csv"))
    return df

def param_exploration_plot():

    theta = 1000**0.125 # (8th root of 1000)
    brs = [theta**x for x in range(-8, 9)]
    df =_read_param_exp_rates("param_exploration/tree", "birth_rate", brs)
    make_param_exp_plot("tree_param_exploration.png", df, "birth_rate", "Relative cognate birthrate", brs, log_x=True)

    alphas = (0.25, 0.5, 0.75, 1.0, 1.5, 2.0, 3.0, 5.0)
    df =_read_param_exp_rates("param_exploration/swamp", "alpha", alphas)
    make_param_exp_plot("swamp_param_exploration.png", df, "alpha", "Alpha parameter", alphas)

    df =_read_param_exp_rates("param_exploration/chain", "alpha", alphas)
    make_param_exp_plot("chain_param_exploration.png", df, "alpha", "Alpha parameter", alphas)

def make_param_exp_plot(filename, df, param_col, param_fancy_name, param_values, log_x=False):

    plt.figure(figsize=(12,6))
    sns.set(style="whitegrid", palette="muted")
    sns.set_context("paper",font_scale=2.0)
    ax = sns.lineplot(data=df,
            x = param_col,
            y = "mean_tiger",
            hue = "taxon_count",
            hue_order = ("10", "25", "50", "100", "250", "500"))
    ax.set(xlabel=param_fancy_name)
    ax.set(ylabel='Mean TIGER value')
    if log_x:
        ax.set(xscale='log')
    ax.set_xticks(param_values)
    ax.set_xticklabels(["{:.3f}".format(x) if len(str(x)) > 3 else str(x) for x in param_values])
    plt.xlim(min(param_values), max(param_values))
    plt.xticks(rotation=90)
    plt.tight_layout()
    plt.savefig(os.path.join("plots", filename))

def main():
    if not os.path.exists("plots"):
        os.mkdir("plots")
    cognate_class_count_plot()
    tiger_rate_plot()
    tiger_rates_semantic_categories()
    tiger_rate_dist_plot()
    metric_comparison_plot()
    tiger_rate_cognates_plot()
    param_exploration_plot()

if __name__ == "__main__":
    main()
