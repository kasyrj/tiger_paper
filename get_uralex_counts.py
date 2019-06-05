#!/usr/bin/env python3
import csv
import os.path

URALEX_PATH = "materials/lexibank-uralex-efe0a73"

# Read Uralex data
with open(os.path.join(URALEX_PATH, "raw", "Data.tsv")) as fp:
    data = {}
    reader = csv.DictReader(fp, delimiter="\t")
    for row in reader:
        lang, meaning, cog = row["language"], row["uralex_mng"], row["cogn_set"]
        if cog == "?":
            continue
        if meaning not in data:
            data[meaning] = []
        data[meaning].append((lang, cog))

min_counts = {}
max_counts = {}
max_props = []

for meaning, cognates in data.items():
    # Handle the easy case first...
    langs = [l for (l,c) in cognates]
    classes = [c for (l,c) in cognates]
    if len(langs) == len(set(langs)):
        # No synonymy!
        min_counts[meaning] = len(set(classes))
        max_counts[meaning] = len(set(classes))
        continue
    # Now we have synonyms...
    # Count how frequent each cognate class is across all languages
    class_counts = {}
    for (l,c) in cognates:
        class_counts[c] = class_counts.get(c, 0) + 1
    # Gather up all the classes attested in each lang
    forms_by_lang = {}
    for l in langs:
        forms_by_lang[l] = []
    for (l,c) in cognates:
        forms_by_lang[l].append(c)
    # For each lang, discard all forms for a given meaning other than
    # either the most frequent or least frequent form
    maximal = {}
    minimal = {}
    for lang, forms in forms_by_lang.items():
        if len(forms) == 1:
            maximal[lang] = forms[0]
            minimal[lang] = forms[0]
        else:
            ranked_forms = [(class_counts[f],f) for f in forms]
            ranked_forms.sort()
            most_common_form = ranked_forms[-1][1]
            least_common_form = ranked_forms[0][1]
            minimal[lang] = most_common_form
            maximal[lang] = least_common_form
    # Get counts
    min_count = len(set(minimal.values()))
    max_count = len(set(maximal.values()))
    min_counts[meaning] = min_count
    max_counts[meaning] = max_count

    # Measure maximum proportion of languages having same cognate set
    counts = [list(minimal.values()).count(c) for c in set(minimal.values())]
    max_prop = max(counts) / sum(counts)
    max_props.append(max_prop)

for name, counts in zip(("min","max"),(min_counts,max_counts)):
    with open("uralex_%s_counts.csv" % name, "w") as fp:
        for meaning, count in counts.items():
            fp.write("%s,%d\n" % (meaning, count))

with open("uralex_max_props.csv", "w") as fp:
    for m in max_props:
        fp.write("%f\n" % m)
