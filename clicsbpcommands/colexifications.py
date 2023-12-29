"""
Calculate colexification networks for individual families.
"""
import html
import itertools
from collections import defaultdict

import numpy as np
from csvw.dsv import UnicodeWriter
from cltoolkit import Wordlist
from pyclts import CLTS
import networkx as nx
from lingpy.convert.graph import networkx2igraph
from lingpy.align.pairwise import Pairwise
from lingpy.algorithm import extra
from lingpy.algorithm import clustering as cluster

from lexibank_clicsbp import Dataset as _CLICS


def write_gml(graph, path, copy=True):
    """
    Write a graph to GML format (using unicode).

    The graph will be adjusted in such a way that all list and set values in edge and
    node attributes will be represented in the form of a string with // as separator.
    """
    ng = None
    if copy:
        # modify graph TODO
        ng = graph.copy()
        for node, data in ng.nodes(data=True):
            for k, v in data.items():
                if isinstance(v, (list, set)):
                    data[k] = '//'.join([str(x) for x in v])
        for nA, nB, data in ng.edges(data=True):
            for k, v in data.items():
                if isinstance(v, (list, set)):
                    data[k] = '//'.join([str(x) for x in v])

    with open(path, 'w') as f:
        for line in nx.generate_gml(ng or graph):
            f.write(html.unescape(line) + '\n')


def get_colexifications(
        wordlist, family=None, concepts=None, languages=None):
    """
    @param wordlist: A cltoolkit Wordlist instance.
    @param family: A string for a language family (valid in Glottolog). When set to None, won't filter by family.
    @param concepts: A list of concepticon glosses that will be compared with the glosses in the wordlist.
        If set to None, concepts won't be filtered.
    @returns: A networkx.Graph instance.
    """
    graph = nx.Graph()
    if languages is None:
        if family is None:
            languages = [language for language in wordlist.languages]
        else:
            languages = [language for language in wordlist.languages if language.family == family]

    if concepts is None:
        concepts = [concept.concepticon_gloss for concept in wordlist.concepts]

    for language in languages:
        cols = defaultdict(list)
        for form in language.forms_with_sounds:
            if form.concept.concepticon_gloss in concepts:
                tform = str(form.sounds)
                cols[tform] += [form]

        # add nodes to the graph
        colexs = []
        for tokens, forms in cols.items():
            colexs += [
                (
                    tokens,
                    [f for f in forms if f.concept],
                    [f.concept.id for f in forms if f.concept]
                )
            ]
            for (f, concept) in zip(colexs[-1][1], colexs[-1][2]):
                try:
                    graph.nodes[concept]["occurrences"] += [f.id]
                    graph.nodes[concept]["words"] += [tokens]
                    graph.nodes[concept]["varieties"] += [language.id]
                    graph.nodes[concept]["languages"] += [language.glottocode]
                    graph.nodes[concept]["families"] += [language.family]
                except KeyError:
                    graph.add_node(
                        concept,
                        occurrences=[f.id],
                        words=[tokens],
                        varieties=[language.id],
                        languages=[language.glottocode],
                        families=[language.family]
                    )

        for tokens, forms, all_concepts in colexs:
            if len(set(all_concepts)) > 1:
                for (f1, c1), (f2, c2) in itertools.combinations(zip(forms, all_concepts), r=2):
                    if c1 == c2:
                        continue
                    # identical concepts need to be excluded
                    try:
                        graph[c1][c2]["count"] += 1
                        graph[c1][c2]["words"] += [tokens]
                        graph[c1][c2]["varieties"] += [language.id]
                        graph[c1][c2]["languages"] += [language.glottocode]
                        graph[c1][c2]["families"] += [language.family]
                    except KeyError:
                        graph.add_edge(
                            c1,
                            c2,
                            count=1,
                            words=[tokens],
                            varieties=[language.id],
                            languages=[language.glottocode],
                            families=[language.family],
                        )
    for nA, nB, data in graph.edges(data=True):
        graph[nA][nB]["variety_count"] = len(set(data["varieties"]))
        graph[nA][nB]["language_count"] = len(set(data["languages"]))
        graph[nA][nB]["family_count"] = len(set(data["families"]))
    for node, data in graph.nodes(data=True):
        graph.nodes[node]["language_count"] = len(set(data["languages"]))
        graph.nodes[node]["variety_count"] = len(set(data["varieties"]))
        graph.nodes[node]["family_count"] = len(set(data["families"]))
    return graph


def weight_by_cognacy(
        graph,
        threshold=0.45,
        cluster_method="infomap",
):
    """
    Function weights the data by computing cognate sets.

    :todo: compute cognacy for concept slots to determine self-colexification
    scores.
    """
    if cluster_method == "infomap":
        cluster_function = extra.infomap_clustering
    else:
        cluster_function = cluster.flat_upgma

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
                matrix = [[0 for _ in data["words"]] for _ in data["words"]]
                for (i, w1), (j, w2) in itertools.combinations(
                        enumerate(data["words"]), r=2):
                    pair = Pairwise(w1.split(), w2.split())
                    pair.align(distance=True)
                    matrix[i][j] = matrix[j][i] = pair.alignments[0][2]

                results = cluster_function(
                    threshold,
                    matrix,
                    taxa=data["languages"])
                weight = len(results)
        else:
            weight = 1
        graph[nA][nB]["cognate_count"] = weight


def get_transition_matrix(graph, steps=5, weight="weight", normalize=False):
    """
    Compute transition matrix following Jackson et al. 2019
    """
    # prune nodes excluding singletons
    nodes = []
    for node in graph.nodes:
        if len(graph[node]) >= 1:
            nodes.append(node)
    a_matrix: list[list[int]] = [[0 for _ in nodes] for _ in nodes]

    for node_a, node_b, data in graph.edges(data=True):
        idx_a, idx_b = nodes.index(node_a), nodes.index(node_b)
        a_matrix[idx_a][idx_b] = a_matrix[idx_b][idx_a] = data[weight]
    d_matrix = [[0 for _ in nodes] for _ in nodes]
    diagonal = [sum(row) for row in a_matrix]
    for i in range(len(nodes)):
        d_matrix[i][i] = 1 / diagonal[i]

    p_matrix = np.matmul(d_matrix, a_matrix)
    new_p_matrix = sum([np.linalg.matrix_power(p_matrix, i) for i in range(1,
                                                                           steps + 1)])

    # we can normalize the matrix by dividing by the number of time steps
    if normalize:
        new_p_matrix = new_p_matrix / steps

    return new_p_matrix, nodes, a_matrix


def register(parser):
    parser.add_argument(
        "--acd-threshold",
        help="Select the threshold for automatic cognate detection",
        default=0.45,
        type=float)
    parser.add_argument(
        "--steps",
        help="define steps for the random walk",
        default=5,
        type=int)
    parser.add_argument(
        "--community-method",
        help="community method",
        default="infomap")
    parser.add_argument(
        "--weight",
        help="determine the weight to use",
        default="language_count")
    parser.add_argument(
        "--normalize",
        help="normalize weights",
        action="store_true")


def write_matrix(name, matrix, concepts):
    with UnicodeWriter(name, delimiter='\t') as f:
        for i, row in enumerate(matrix):
            f.writerow([concepts[i]] + ["{0:.2f}".format(cell) for cell in row])


def run(args):
    CLICS = _CLICS()
    families = [row["Family"] for row in CLICS.read_etc("families")]

    clts = CLTS()
    wl = Wordlist([CLICS.cldf_reader()], ts=clts.bipa)
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
        weight_by_cognacy(G, threshold=args.acd_threshold)

        # get the transition matrix
        if len(G) > 1:
            T, all_nodes, A = get_transition_matrix(
                G, steps=args.steps, weight=args.weight, normalize=args.normalize)
            write_matrix(CLICS.output / "p-matrix" / "{0}-t.tsv".format(family), T, all_nodes)
            write_matrix(CLICS.output / "p-matrix" / "{0}-a.tsv".format(family), A, all_nodes)
            write_gml(G, CLICS.output / "graphs" / "{0}.gml".format(family))

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
                for (i, idxA), (j, idxB) in itertools.combinations(enumerate(idxs), 2):
                    nodeA, nodeB = current_concepts[i], current_concepts[j]
                    score = sum([new_matrix[i][j], new_matrix[j][i]])/2
                    if round(score, 2) > 0:
                        DG.add_edge(nodeA, nodeB, **G[nodeA].get(nodeB, {}))
                        DG[nodeA][nodeB]["tweight"] = round(score, 2)
                SG = G.subgraph(current_concepts)
                if len(DG.nodes) >= 5 and len(DG.edges) > 0:
                    IG = networkx2igraph(DG)
                    clusters = {c: 0 for c in concepts[tag]}
                    if args.community_method == "infomap":
                        comms = IG.community_infomap(edge_weights="tweight")
                    else:
                        comms = IG.community_optimal_modularity(weights="tweight")
                    for i, nodes in enumerate(comms):
                        for node in nodes:
                            clusters[IG.vs[node]["Name"]] = i+1
                    for concept in current_concepts:
                        links, links2, links3, links4, links5 = [], [], [], [], []
                        if concept in DG:
                            for neighbor, data in DG[concept].items():
                                links += ["{0}:{1:.2f}".format(neighbor, data["tweight"])]
                            
                            for neighbor, data in SG[concept].items():
                                links2 += ["{0}:{1:.2f}".format(neighbor, data["language_count"])]
                                
                                if G.nodes[concept][args.weight] > G.nodes[neighbor]["language_count"]:
                                    c_max = G.nodes[neighbor]["language_count"]
                                else:
                                    c_max = G.nodes[concept]["language_count"]
                                links3 += ["{0}:{1:.2f}".format(
                                    neighbor,
                                    (data["language_count"]**2)/(c_max**2))
                                    ]
                                links4 = ["{0}:{1:.2f}".format(
                                    neighbor,
                                    data["cognate_count"])]
                                links5 = ["{0}:{1:.2f}".format(
                                    neighbor,
                                    (data["cognate_count"]**2)/(c_max**2))]

                        table += [[
                            concept,
                            str(G.nodes[concept][args.weight]),
                            family,
                            tag,
                            str(clusters[concept]),
                            ";".join(links),
                            ";".join(links2),
                            ";".join(links3), 
                            ";".join(links4),
                            ";".join(links5)
                            ]]
                else:
                    args.log.info("skipping family {0} since there are no data for {1}".format(family, tag))
    
                write_gml(SG, CLICS.output / "graphs" / "{0}-{1}.gml".format(family,tag))

    with UnicodeWriter(CLICS.output / "colexifications.tsv", delimiter='\t') as f:
        f.writerow([
            "Concept", "Frequency", "Family", "Tag", "Random_Walk_Community",
            "Random_Walk_Links",
            "Language_Count", 
            "Language_Count_Weighted",
            "Cognate_Count",
            "Cognate_Count_Weighted"
        ])
        f.writerows(sorted(table, key=lambda x: (x[1], x[2], x[3], x[0])))
