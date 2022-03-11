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
import numpy as np

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
            if form.concept.concepticon_gloss in concepts:
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
                                    varieties = [language.id],
                                    languages=[language.glottocode],
                                    families=[language.family]
                                    )
                        else:
                            G.nodes[c1]["occurrences"] += [f1.id]
                            G.nodes[c1]["words"] += [tokens]
                            G.nodes[c1]["varieties"] += [language.id]
                            G.nodes[c1]["languages"] += [language.glottocode]
                            G.nodes[c1]["families"] += [language.family]
                        if not c2 in G:
                            G.add_node(
                                    c2, 
                                    occurrences=[f2.id],
                                    words=[" ".join(tokens)],
                                    varieties=[language.id],
                                    languages=[language.glottocode],
                                    families=[language.family]
                                    )
                        else:
                            G.nodes[c2]["occurrences"] += [f2.id]
                            G.nodes[c2]["words"] += [tokens]
                            G.nodes[c2]["varieties"] += [language.id]
                            G.nodes[c2]["languages"] += [language.glottocode]
                            G.nodes[c2]["families"] += [language.family]

                        try:
                            G[c1][c2]["count"] += 1
                            G[c1][c2]["words"] += [tokens]
                            G[c1][c2]["varieties"] += [language.id]
                            G[c1][c2]["languages"] += [language.glottocode]
                            G[c1][c2]["families"] += [language.family]
                        except:
                            G.add_edge(
                                    c1,
                                    c2,
                                    count=1,
                                    words=[tokens],
                                    varieties=[language.id],
                                    languages=[language.glottocode],
                                    families=[language.family],
                                    weight=0
                                    )
    for nA, nB, data in G.edges(data=True):
        G[nA][nB]["variety_weight"] = len(set(data["varieties"]))
        G[nA][nB]["language_weight"] = len(set(data["languages"]))
        G[nA][nB]["family_weight"] = len(set(data["families"]))
    for node, data in G.nodes(data=True):
        G.nodes[node]["language_weight"] = len(set(data["languages"]))
        G.nodes[node]["variety_weight"] = len(set(data["varieties"]))
        G.nodes[node]["family_weight"] = len(set(data["families"]))
    return G


def get_transition_matrix(G, steps=10, weight="weight"):
    """
    Compute transition matrix following Jackson et al. 2019
    """
    # prune nodes excluding singletons
    nodes = []
    for node in G.nodes:
        #if len(G[node]) >= 1:
        nodes.append(node)
    print("retained matrix with {0} nodes out of {1}".format(len(nodes), len(G)))

    a_matrix = [[0 for x in nodes] for y in nodes]

    # define i == j as number of languages occurring here
    if weight == "language_weight": # TODO: generalize later
        for i, n in enumerate(nodes):
            a_matrix[i][i] = G.nodes[n]["language_weight"]
        
    for nodeA, nodeB, data in G.edges(data=True):
        idxA, idxB = nodes.index(nodeA), nodes.index(nodeB)
        a_matrix[idxA][idxB] = a_matrix[idxB][idxA] = data[weight]
    d_matrix = [[0 for x in nodes] for y in nodes]
    diagonal = [sum(row) for row in a_matrix]
    for i in range(len(nodes)):
        d_matrix[i][i] = 1 / diagonal[i]

    p_matrix = np.matmul(d_matrix, a_matrix)
    new_p_matrix = np.matmul(d_matrix, a_matrix)
    for i in range(1, steps+1):
        new_matrix = np.linalg.matrix_power(p_matrix, i)
        new_matrix_m1 = np.linalg.matrix_power(p_matrix, i-1)
        new_p_matrix = np.multiply(new_matrix, 1-new_matrix_m1) + new_p_matrix

    return new_p_matrix, nodes, a_matrix
    

        


def weight_by_cognacy(
        graph, 
        threshold=0.45, 
        method="sca",
        cluster_method="infomap"
        ):
    """
    Function weights the data by computing cognate sets.

    :todo: compute cognacy for concept slots to determine self-colexification
    scores.
    """
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
                    weight = 1
                else:
                    weight = 2
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
            weight = 1
        graph[nA][nB]["weight"] = weight


def write_matrix(name, matrix, concepts):
    with open(name, "w") as f:
        for i, row in enumerate(matrix):
            f.write(concepts[i])
            for cell in row:
                f.write("\t{0:.2f}".format(cell))
            f.write("\n")


def run(args):

    CLICS = _CLICS()
    families = [row["Family"] for row in 
            CLICS.etc_dir.read_csv(
                "families.tsv", 
                dicts=True, 
                delimiter="\t")]

    clts = CLTS()
    wl = Wordlist(
            [Dataset.from_metadata(
        CLICS.cldf_dir / "cldf-metadata.json")],
            ts=clts.bipa)
    args.log.info("loaded wordlist")
    concepts = {"all": [], "color": [], "emotion": [], "human body part": []}
    concepts["all"] = [concept.concepticon_gloss for concept in wl.concepts]
    for concept in CLICS.concepts:
        if concept["CONCEPTICON_GLOSS"] in concepts["all"]:
            concepts[concept["TAG"]] += [concept["CONCEPTICON_GLOSS"]]
    args.log.info("loaded concepts and families")
    
    table = []
    for family in families:
        G = get_colexifications(wl, family, concepts["all"])
        weight_by_cognacy(
                G,
                threshold=args.acd_threshold,
                method=args.acd_method
                )

        # get the transition matrix
        if len(G) > 1:
            T, all_nodes, A = get_transition_matrix(G, steps=5, weight="language_weight")
            write_matrix(
                    CLICS.dir.joinpath("output", "p-matrix", "{0}-t.tsv".format(family)),
                    T, 
                    all_nodes
                    )
            write_matrix(
                    CLICS.dir.joinpath("output", "p-matrix", "{0}-a.tsv".format(family)),
                    A, 
                    all_nodes
                    )

            for tag in ["human body part", "color", "emotion"]:
                current_concepts = [c for c in concepts[tag] if c in all_nodes]
                args.log.info("analyzing {0} / {1}".format(family, tag))
                idxs = []
                for c in current_concepts:
                    idxs += [all_nodes.index(c)]
                new_matrix = [[0 for x in idxs] for y in idxs]
                for i, idxA in enumerate(idxs):
                    for j, idxB in enumerate(idxs):
                        new_matrix[i][j] = T[idxA][idxB]
                # convert to graph
                DG = nx.Graph()
                for node in current_concepts:
                    DG.add_node(node, **G.nodes[node])
                for i, idxA in enumerate(idxs):
                    for j, idxB in enumerate(idxs):
                        if i < j:
                            nodeA, nodeB = current_concepts[i], current_concepts[j]
                            score = sum([new_matrix[i][j], new_matrix[j][i]])/2
                            if round(score, 2) > 0:
                                DG.add_edge(nodeA, nodeB, **G[nodeA].get(nodeB, {}))
                                DG[nodeA][nodeB]["tweight"] = score
                if len(DG.nodes) > 5:
                    IG = networkx2igraph(DG)
                    clusters = {c: 0 for c in concepts[tag]}
                    for i, nodes in enumerate(
                            IG.community_infomap(edge_weights="tweight")):
                        for node in nodes:
                            clusters[IG.vs[node]["Name"]] = i+1
                    for concept in current_concepts:
                        links = []
                        if concept in DG:
                            for neighbor, data in DG[concept].items():
                                links += ["{0}:{1:.2f}".format(neighbor, data["tweight"])]
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


    


    
