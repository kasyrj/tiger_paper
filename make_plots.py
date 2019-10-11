#!/usr/bin/env python3
import glob
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
    ax.set_xlabel("TIGER rate")
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

    plt.figure(figsize=(12,6))
    sns.set(style="whitegrid", palette="muted")
    sns.set_context("paper",font_scale=2.0)
    ax = sns.boxplot(data=df,order=list(reversed(data_names)), orient="h")
    ax.set(xlabel='TIGER rates')
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

    plt.figure(figsize=(12,6))
    sns.set(style="whitegrid", palette="muted")
    sns.set_context("paper",font_scale=2.0)
    ax = sns.boxplot(data=df, orient="h")
    ax.set(xlabel='TIGER rates by category')
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
    plt.title("TIGER rate")

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
    
if __name__ == "__main__":
    if not os.path.exists("plots"):
        os.mkdir("plots")
    cognate_class_count_plot()
    tiger_rate_plot()
    tiger_rates_semantic_categories()
    tiger_rate_dist_plot()
    metric_comparison_plot()
    
