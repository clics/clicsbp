"""
Calculate colexification networks for individual families.
"""
import itertools

from csvw.dsv import UnicodeWriter
from cltoolkit import Wordlist
from pyclts import CLTS
import networkx as nx
from lingpy.convert.graph import networkx2igraph
from pyclics.colexifications import get_colexifications, weight_by_cognacy, get_transition_matrix
from pyclics.util import write_gml

from lexibank_clicsbp import Dataset as _CLICS


def register(parser):
    parser.add_argument(
        "--acd-threshold",
        help="Select the threshold for automatic cognate detection",
        default=0.45,
        type=float)
    parser.add_argument(
        "--steps",
        help="define steps for the random walk",
        default=10,
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
