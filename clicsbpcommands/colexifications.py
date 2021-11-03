"""
Calculate colexification networks for individual families.
"""
from cltoolkit import Wordlist
from pycldf import Dataset
from pyclts import CLTS
from lingpy import Pairwise
from lingpy.algorithm import cluster
from itertools import combinations, product
import networkx as nx
from collections import defaultdict
from tabulate import tabulate
from lingpy.algorithm import extra
from lingpy.convert.graph import networkx2igraph

from lexibank_clicsbp import Dataset as _CLICS

def register(parser):
    parser.add_argument(
            "--acd-threshold",
            help="Select the threshold for automatic cognate detection",
            default=0.45
            )
    parser.add_argument(
            "--acd-method",
            help="Select automatic cognate detection method",
            default="sca"
            )

    
def get_colexifications(wordlist, family, concepts):
    G = nx.Graph()
    languages = [language for language in wordlist.languages if language.family == family]
    for language in languages:
        cols = defaultdict(list)
        for form in language.forms_with_sounds:
            if form.concept.id in concepts:
                tform = str(form.sounds)
                cols[tform] += [form]
        for tokens, forms in cols.items():
            if len(forms) > 1:
                for f1, f2 in combinations(forms, r=2):
                    if f1.concept and f2.concept and (
                            f1.concept.id != f2.concept.id):
                        c1, c2 = f1.concept.id, f2.concept.id
                        if not c1 in G:
                            G.add_node(
                                    c1, 
                                    occurrences=[f1.id],
                                    words=[tokens],
                                    languages=[language.id],
                                    families=[language.family]
                                    )
                        else:
                            G.nodes[c1]["occurrences"] += [f1.id]
                            G.nodes[c1]["words"] += [tokens]
                            G.nodes[c1]["languages"] += [language.id]
                            G.nodes[c1]["families"] += [language.family]
                        if not c2 in G:
                            G.add_node(
                                    c2, 
                                    occurrences=[f2.id],
                                    words=[" ".join(tokens)],
                                    languages=[language.id],
                                    families=[language.family]
                                    )
                        else:
                            G.nodes[c2]["occurrences"] += [f2.id]
                            G.nodes[c2]["words"] += [tokens]
                            G.nodes[c2]["languages"] += [language.id]
                            G.nodes[c2]["families"] += [language.family]

                        try:
                            G[c1][c2]["count"] += 1
                            G[c1][c2]["words"] += [tokens]
                            G[c1][c2]["languages"] += [language.id]
                            G[c1][c2]["families"] += [language.family]
                        except:
                            G.add_edge(
                                    c1,
                                    c2,
                                    count=1,
                                    words=[tokens],
                                    languages=[language.id],
                                    families=[language.family],
                                    weight=0
                                    )
    return G


def weight_by_cognacy(
        graph, 
        threshold=0.45, 
        method="sca",
        cluster_method="infomap"
        ):
    if cluster_method == "infomap":
        clusterm = extra.infomap_clustering
    else:
        clusterm = cluster.flat_upgma

    forms = defaultdict(list)
    edges = {}
    for nA, nB, data in graph.edges(data=True):
        if data["count"] > 1:
            # assemble languages with different cognates
            if data["count"] == 2:
                pair = Pairwise(data["words"][0], data["words"][1])
                pair.align(distance=True)
                if pair.alignments[0][2] <= threshold:
                    weight
            else:
                matrix = [[0 for i in data["words"]] for j in data["words"]]
                for (i, w1), (j, w2) in combinations(
                        enumerate(data["words"]), r=2):
                    pair = Pairwise(w1.split(), w2.split())
                    pair.align(distance=True)
                    matrix[i][j] = matrix[j][i] = pair.alignments[0][2]

                results = clusterm(
                        threshold, 
                        matrix,
                        taxa=data["languages"])
                weight = len(results)
        else:
            weight = 0.5
        graph[nA][nB]["weight"] = weight



def run(args):

    CLICS = _CLICS()
    families = [row["Family"] for row in 
            CLICS.etc_dir.read_csv(
                "families.tsv", 
                dicts=True, 
                delimiter="\t")]

    clts = CLTS()
    concepts = {"color": [], "emotion": [], "human body part": []}
    for concept in CLICS.concepts:
        concepts[concept["TAG"]] += [concept["CONCEPTICON_GLOSS"]]

    args.log.info("loaded concepts and families")

    wl = Wordlist(
            [Dataset.from_metadata(
        CLICS.cldf_dir / "cldf-metadata.json")],
            ts=clts.bipa)

    args.log.info("loaded wordlist")
    
    table = []
    for family in families:
        args.log.info("analyzing {0}".format(family))
        for tag in ["human body part"]:
            G = get_colexifications(wl, family, concepts[tag])
            if len(G) > 0:
                    weight_by_cognacy(
                            G,
                            threshold=args.acd_threshold,
                            method=args.acd_method
                            )
                    IG = networkx2igraph(G)
                    clusters = {c: 0 for c in concepts[tag]}
                    for i, nodes in enumerate(
                            IG.community_infomap(edge_weights="weight")):
                        for node in nodes:
                            clusters[IG.vs[node]["Name"]] = i+1
                    for concept in concepts[tag]:
                        links = []
                        if concept in G:
                            for neighbor, data in G[concept].items():
                                links += ["{0}:{1:.2f}".format(neighbor, data["weight"])]
                        table += [[
                            concept,
                            family,
                            tag,
                            str(clusters[concept]),
                            ";".join(links)]]
            else:
                args.log.info("skipping family {0} since there are no data".format(family))
    with open(CLICS.dir / "output" / "colexifications.tsv", "w") as f:
        f.write("CONCEPT\tFAMILY\tTAG\tCOMMUNITY\tLINKS\n")
        for row in sorted(table, key=lambda x: (x[1], x[2], x[3], x[0])):
            f.write("\t".join(row)+"\n")


    


    
