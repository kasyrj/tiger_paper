#!/usr/bin/python3

import os
import glob
import statistics

comparisons = ["pure_tree","borrowing_05","borrowing_10","borrowing_15","borrowing_20","dialect","swamp"]

def read_table_from_file(infile):
    table = []
    with open(infile,"r") as f:
        for line in f:
            table.append(line.strip().rstrip().split("\t"))
    return table

def a_greater_than_b(a,b,metric,results):
    count = 0
    for i in range(len(results["pure_tree"])):
        if results[a][i][metric] > results[b][i][metric]:
            count += 1
    return count

def make_comparison_table():
    results = {}
    analyses = sorted(glob.glob(os.path.join("analyses","*")))
    analyses.remove(os.path.join("analyses","uralex"))
    for a in analyses:
        basename = os.path.basename(os.path.normpath(a))
        results[basename] = []
        replications = sorted(glob.glob(os.path.join(a,"*.csv")))
        for r in replications:
            tiger_file = r + "_rates.txt"
            delta_q_file = r + "_delta_qresidual.txt"
            tiger_rates = read_table_from_file(tiger_file)
            delta_q_rates = read_table_from_file(delta_q_file)[1:] # ignore header
            trates = []
            dscores = []
            qresiduals = []
            for line in tiger_rates:
                trates.append(float(line[1]))
            for line in delta_q_rates:
                dscores.append(float(line[1]))
                qresiduals.append(float(line[2]))
            current = {}
            current["tiger"] = statistics.mean(trates)
            current["delta"] = statistics.mean(dscores)
            current["qresidual"] = statistics.mean(qresiduals)
            results[basename].append(current)
    total = len(results["pure_tree"])
    table = []
    table.append("More tree-like vs. less tree-like\tTIGER rate agreements\tDelta score agreements\tQ-residual agreements\tNumber of replications")
    for i in range(len(comparisons)-1):
        tiger_cmp = a_greater_than_b(comparisons[i],comparisons[i+1],"tiger",results)
        delta_cmp = a_greater_than_b(comparisons[i+1],comparisons[i],"delta",results)    # Reversed metric compared to TIGER rates
        qres_cmp = a_greater_than_b(comparisons[i+1],comparisons[i],"qresidual",results) # Reversed metric compared to TIGER rates
        table.append("%s vs. %s\t%i\t%i\t%i\t%i" % (comparisons[i],comparisons[i+1], tiger_cmp, delta_cmp, qres_cmp, total))
    return table

def make_mean_rates_table():
    results = {}
    analyses = sorted(glob.glob(os.path.join("analyses","*")))
    for a in analyses:
        basename = os.path.basename(os.path.normpath(a))
        results[basename] = {}
        results[basename]["delta"] = []
        results[basename]["tiger"] = []
        results[basename]["qresidual"] = []
        replications = sorted(glob.glob(os.path.join(a,"*.csv")))
        for r in replications:
            if basename != "uralex":
                tiger_file = r + "_rates.txt"
                delta_q_file = r + "_delta_qresidual.txt"
            else:
                tiger_file = os.path.splitext(r)[0] + "_rates.txt"
                delta_q_file = r + "_delta_qresidual.txt"                 
            tiger_rates = read_table_from_file(tiger_file)
            delta_q_rates = read_table_from_file(delta_q_file)[1:] # ignore header
            for line in tiger_rates:
                results[basename]["tiger"].append(float(line[1]))
            for line in delta_q_rates:
                results[basename]["delta"].append(float(line[1]))
                results[basename]["qresidual"].append(float(line[2]))
    table = []
    table.append("Simulation\tMean TIGER rate\tMean delta score\tMean Q-residual")
    for c in comparisons:
        mean_tiger = statistics.mean(results[c]["tiger"])
        mean_delta = statistics.mean(results[c]["delta"])
        mean_qresi = statistics.mean(results[c]["qresidual"])
        table.append("%s\t%f\t%f\t%f" % (c,mean_tiger,mean_delta,mean_qresi))
    return table
    
if __name__ == '__main__':
    comparisons_table = make_comparison_table()
    means_table = make_mean_rates_table()
    if not os.path.exists("tables"):
        os.mkdir("tables")
    with open(os.path.join("tables","comparisons.tsv"), "w") as f:
        for line in comparisons_table:
            f.write(line + "\n")
    with open(os.path.join("tables","means.tsv"), "w") as f:
        for line in means_table:
            f.write(line + "\n")

    
