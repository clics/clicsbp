"""
Calculate coverage for the data.
"""

from cltoolkit import Wordlist
from pycldf import Dataset
from lexibank_clicsbp import Dataset as _CLICS
from pyclts import CLTS
import itertools
from collections import defaultdict
import statistics
from tabulate import tabulate
from pylexibank import progressbar


def mutual_coverage(data):
    scores = []
    #data = []
    for (langA, conceptsA), (langB, conceptsB) in itertools.combinations(data, r=2):
        scores += [len(conceptsA.intersection(conceptsB))]
    return statistics.mean(scores)


def run(args):

    CLICS = _CLICS()
    clts = CLTS()
    all_concepts = {concept["CONCEPTICON_GLOSS"] for concept in CLICS.concepts}

    wl = Wordlist(
            [Dataset.from_metadata(
        CLICS.cldf_dir / "Wordlist-metadata.json")],
            ts=clts.bipa)
    args.log.info("loaded wordlist")
    
    languages = sorted(
            wl.languages, key=lambda x: len(x.concepts),
            reverse=True)
    unique_glottocode = []
    visited = set()
    for lang in languages:
        if lang.glottocode in visited:
            pass
        else:
            visited.add(lang.glottocode)
            unique_glottocode.append(lang)
        
    concepts = sorted(
            wl.concepts, key=lambda x: len(set([form.language.glottocode for
            form in x.forms_with_sounds])), reverse=True)
    
    table = []
    for i in progressbar(range(1500, 200, -100)):
        for j in range(1500, 200, -100):
            new_languages = unique_glottocode[:i]
            new_concepts = [concept.id for concept in concepts[:j]]
            data = []
            for lang in new_languages:
                data += [(lang.id, set([concept.id for concept in lang.concepts if
                    concept.id in new_concepts]))]

            families = defaultdict(list)
            for language in new_languages:
                families[language.family] += [language.glottocode]
            valid_families = sum([1 for x, y in families.items() if len(set(y)) >= 5])
            valid_languages = sum([len(set(y)) for x, y in families.items() if
                len(set(y)) >= 5])
            coverage = mutual_coverage(data)
            average_concepts = sum([len(c) for l, c in data])/len(data)
            table += [[
                len(new_languages), len(new_concepts), coverage,
                coverage / len(new_concepts),
                valid_families, valid_languages, average_concepts]]

    print(
            tabulate(
                table, 
                headers=["Languages", "Concepts", "Coverage", 
                    "Coverage Ratio", "Families", "Valid Languages", "Average Concepts"],
                tablefmt="pipe"))
