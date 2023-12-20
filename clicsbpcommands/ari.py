"""
Compute adjusted rand indices.
"""

from lexibank_clicsbp import Dataset as _CLICS
from csvw.dsv import reader, UnicodeWriter
from collections import defaultdict
from itertools import combinations
from sklearn.metrics import adjusted_rand_score, adjusted_mutual_info_score
from lingpy.evaluate.acd import _get_bcubed_score as bcubes


def register(parser):
    parser.add_argument(
        "--tag",
        help="Select the domain (human body part, emotion, color)",
        default="human body part"
    )


def run(args):
    CLICS = _CLICS()

    data = [row for row in reader(CLICS.output / "colexifications.tsv", delimiter='\t', dicts=True)]

    concepts = sorted(set([row["Concept"] for row in data if row["Tag"] == args.tag]))
    fams = defaultdict(dict)
    for row in data:
        if row["Tag"] == args.tag:
            fams[row["Family"]][row["Concept"]] = row["Random_Walk_Community"]
    
    pairs = {}
    for famA, famB in combinations(list(fams), r=2):
        print(famA, famB)
        dtA, dtB = fams[famA], fams[famB]
        labelsA, labelsB, labelsBC, labelsAC = [], [], [], []
        trackA = max([int(row["Random_Walk_Community"]) for row in data]) + 1
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
        f = 2 * (p * r) / (p + r)
        pairs[famA, famB] = [ari, ami, f]
    with UnicodeWriter(
        CLICS.dir / "output" / "ari-{0}.tsv".format(args.tag.replace(" ", "_")),
        delimiter='\t'
    ) as f:
        f.writerow("FAMILY_A FAMILY_B ARI AMI BCUBES".split())
        f.writerow([[fA, fB, ari, ami, bc] for (fA, fB), (ari, ami, bc) in pairs.items()])
