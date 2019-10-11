#!/usr/bin/env python3
import collections
import csv
import os.path

URALEX_PATH = "materials/lexibank-uralex-efe0a73"

# Read Uralex data
with open(os.path.join(URALEX_PATH, "raw", "Data.tsv")) as fp:
    cognates = {}
    reader = csv.DictReader(fp, delimiter="\t")
    for row in reader:
        lang, meaning, cog = row["language"], row["uralex_mng"], row["cogn_set"]
        if cog == "?":
            continue
        if meaning not in cognates:
            cognates[meaning] = {}
        if lang not in cognates[meaning]:
            cognates[meaning][lang] = set()
        cognates[meaning][lang].add(cog)

max_props = []

# Resolve synonyms according to minimising strategy
# Based on code from tiger-calculator
for meaning in cognates:
    # Count cognate classes
    cognate_class_counts = collections.Counter()
    languages = []
    for lang, cognate_classes in cognates[meaning].items():
        languages.append(lang)
        for c in cognate_classes:
            if c != "?":
                cognate_class_counts[c] += 1
    # Divide languages into easy and hard cases
    easy_langs = [l for l in languages if len(cognates[meaning][l]) < 2]
    hard_langs = [l for l in languages if l not in easy_langs]
    # Make easy assignments
    attested_cognates = set()
    for lang in easy_langs:
        if len(cognates[meaning][lang]) == 1:
            cognates[meaning][lang] = cognates[meaning][lang].pop()
            attested_cognates.add(cognates[meaning][lang])
    # Make hard assignments
    for lang in hard_langs:
        options = [(cognate_class_counts[c], c) for c in cognates[meaning][lang]]
        # Sort cognates from rare to common if we want to maximise cognate
        # class count, or from common to rare if we want to minimise it.
        options.sort(reverse=True)
        # Preferentially assign a cognate which has already been
        # assigned if we're trying to minimise, or one which has
        # not if we're trying to maximise.
        for n, c in options:
            if c in attested_cognates:
                cognates[meaning][lang] = c
                break
        # Otherwise just pick the most/least frequent cognate.
        else:
            cognates[meaning][lang] = options[0][1]
        attested_cognates.add(cognates[meaning][lang])

# Get counts
counts = {}
max_props = []
for meaning in cognates:
    cognate_classes = [x for x in cognates[meaning].values() if x != "?"]
    class_count = len(set(cognate_classes))
    counts[meaning] = class_count
    class_freqs = [cognate_classes.count(x) for x in set(cognate_classes)]
    max_prop = max(class_freqs) / sum(class_freqs)
    max_props.append(max_prop)

with open("uralex_counts.csv", "w") as fp:
    for meaning, count in counts.items():
        fp.write("%s,%d\n" % (meaning, count))

with open("uralex_max_props.csv", "w") as fp:
    for m in max_props:
        fp.write("%f\n" % m)
