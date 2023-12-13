"""
Calculate coverage for the data.
"""
import itertools
from collections import defaultdict

from cltoolkit import Wordlist
from lexibank_clicsbp import Dataset as _CLICS
from pyclts import CLTS
import statistics
from pylexibank import progressbar
from clldutils.clilib import Table, add_format


def register(parser):
    add_format(parser, default='pipe')


def mutual_coverage(data):
    scores = []
    #data = []
    for (langA, conceptsA), (langB, conceptsB) in itertools.combinations(data, r=2):
        scores += [len(conceptsA.intersection(conceptsB))]
    return statistics.mean(scores)


def run(args):
    CLICS = _CLICS()
    clts = CLTS()

    wl = Wordlist([CLICS.cldf_reader()], ts=clts.bipa)
    args.log.info("loaded wordlist")
    
    languages = sorted(wl.languages, key=lambda x: len(x.concepts), reverse=True)
    unique_glottocode = []
    visited = set()
    for lang in languages:
        if lang.glottocode not in visited:
            visited.add(lang.glottocode)
            unique_glottocode.append(lang)

    concepts = sorted(
            wl.concepts, key=lambda x: len(set([form.language.glottocode for
            form in x.forms_with_sounds])), reverse=True)

    with Table(
            args,
            "Languages",
            "Concepts",
            "Coverage",
            "Coverage Ratio",
            "Families",
            "Valid Languages",
            "Average Concepts") as table:
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
                table.append([
                    len(new_languages),
                    len(new_concepts),
                    coverage,
                    coverage / len(new_concepts),
                    valid_families,
                    valid_languages,
                    average_concepts])
