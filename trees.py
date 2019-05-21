import itertools
import random

import dendropy
from dendropy.simulate import treesim

dummy_isos = set(["".join(chars) for chars in itertools.combinations("abcdefghijklmnopqrstuvwxyz",3)])

def generate_yule_tree(taxa, birthrate=1.0, taxa_names=None):
    names = random.sample(dummy_isos, min(taxa, len(dummy_isos)))
    fancytaxa = dendropy.TaxonNamespace(names)
    tree = treesim.birth_death_tree(birth_rate=birthrate, death_rate=0.0, ntax=taxa, taxon_namespace=fancytaxa)
    return tree
