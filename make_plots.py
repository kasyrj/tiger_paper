#!/usr/bin/env python3
import glob
import os, os.path

import scipy.stats
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

def cognate_class_count_plot():
    # Actual class counts
    cognate_counts = []
    with open("uralex_min_counts.csv","r") as fp:
        for line in fp:
            meaning, cognates = line.strip().split(",")
            cognate_counts.append(int(cognates))

    # Best fitting distribution
    nbinom_support = range(0,max(cognate_counts))
    nbinom_probs = [scipy.stats.nbinom(8,0.45).pmf(n) for n in nbinom_support]

    fig, ax1 = plt.subplots()
    ax2 = ax1.twinx()

    ax1.hist(cognate_counts,19)
    ax2.stem(nbinom_support,nbinom_probs, linefmt="C1-", markerfmt="C1o")
    a, b = ax2.get_ylim()
    ax2.set_ylim(0.0,b)
    plt.tight_layout()
    plt.savefig("plots/cognate_dist.png")

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

    plt.figure(figsize=(12,6))
    sns.set(style="whitegrid", palette="muted")
    sns.set_context("paper",font_scale=2.0)
    ax = sns.boxplot(data=df,order=list(reversed(data_names)), orient="h")
    ax.set(xlabel='TIGER rates')
    ax.set_xticks([0.00, 0.25,0.50,0.75,1.00])
    plt.xticks(rotation=90)
    plt.tight_layout()
    plt.savefig("plots/tiger_rates_plot.png")

if __name__ == "__main__":
    if not os.path.exists("plots"):
        os.mkdir("plots")
    cognate_class_count_plot()
    tiger_rate_plot()
