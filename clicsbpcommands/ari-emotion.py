"""
Compute adjusted rand indices.
"""

from lexibank_clicsbp import Dataset as _CLICS
from tabulate import tabulate
from csvw.dsv import UnicodeDictReader
from collections import defaultdict
from itertools import combinations
from sklearn.metrics import adjusted_rand_score, adjusted_mutual_info_score
from lingpy.evaluate.acd import _get_bcubed_score as bcubes


def run(args):

    CLICS = _CLICS()
    families = [row["Family"] for row in 
            CLICS.etc_dir.read_csv(
                "families.tsv", 
                dicts=True, 
                delimiter="\t")]


    with UnicodeDictReader(CLICS.dir.joinpath("output", "colexifications.tsv"),
            delimiter="\t") as reader:
        data = [row for row in reader]

    concepts = sorted(set([row["CONCEPT"] for row in data if row["TAG"] == "emotion"
            ]))

    fams = defaultdict(dict)
    for row in data:
        if row["TAG"] == "emotion":
            fams[row["FAMILY"]][row["CONCEPT"]] = row["COMMUNITY"]
    
    pairs = {}
    for famA, famB in combinations(list(fams), r=2):
        print(famA, famB)
        dtA, dtB = fams[famA], fams[famB]
        labelsA, labelsB, labelsBC, labelsAC = [], [], [], []
        trackA = max([int(row["COMMUNITY"]) for row in data])+1
        trackB = trackA
        for concept in concepts:
            if concept in dtA and concept in dtB:
                comA, comB = dtA[concept], dtB[concept]
                if comA == "0":
                    labelsA += [trackA]
                    trackA += 1
                else:
                    labelsA += [int(comA)]
                if comB == "0":
                    labelsB += [trackB]
                    trackB += 1
                else:
                    labelsB += [int(comB)]
                labelsBC += [int(comB)]
        ari = adjusted_rand_score(labelsA, labelsB)
        ami = adjusted_mutual_info_score(labelsA, labelsB)
        p, r = bcubes(labelsA, labelsBC), bcubes(labelsBC, labelsA)
        f = 2*(p*r)/(p+r)
        pairs[famA, famB] = [ari, ami, f]
    with open(CLICS.dir.joinpath("output", "ari-emotion.tsv"), "w") as f:
        f.write("FAMILY_A\tFAMILY_B\tARI_EMOTION\tAMI_EMOTION\tBCUBES_EMOTION\n")
        for (fA, fB), (ari, ami, bc) in pairs.items():
            f.write("{0}\t{1}\t{2:.4f}\t{3:.4f}\t{4:.4f}\n".format(
                fA, fB, ari, ami, bc))






