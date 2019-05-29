#!/usr/bin/env python3
import glob
import os.path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

def cognate_class_count_plot():
    cognate_counts = []
    with open("uralex_min_counts.csv","r") as fp:
        for line in fp:
            meaning, cognates = line.strip().split(",")
            cognate_counts.append(int(cognates))
    plt.hist(cognate_counts,26)
    plt.tight_layout()
    plt.savefig("cognate_dist.png")

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
                rates.extend([float(x.strip()) for x in fp.readlines()])
        df = pd.DataFrame({name: rates})
        dfs.append(df)
    df = pd.concat(dfs)

    plt.figure(figsize=(12,6))
    sns.set(style="whitegrid", palette="muted")
    sns.set_context("paper",font_scale=2.0)
    ax = sns.boxplot(data=df,order=list(reversed(data_names)), orient="h")
    ax.set(xlabel='TIGER rates')
    ax.set_xticks([0.00, 0.25,0.50,0.75,1.00])
    plt.xticks(rotation=90)
    plt.tight_layout()
    plt.savefig("tiger_rates_plot.png")

if __name__ == "__main__":
    cognate_class_count_plot()
    tiger_rate_plot()
