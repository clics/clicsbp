"""
Investigate degree distributions across different tag sets.
"""
import networkx as nx
from tabulate import tabulate
from lexibank_clicsbp import Dataset as _CLICS
import igraph
from lingpy.convert.graph import igraph2networkx
import random

def register(parser):

    parser.add_argument("--weight", default="cognate_count")
    parser.add_argument("--trials", default=100)


def run(args):
    
    table = []
    CLICS = _CLICS()
    families = [row["Family"] for row in 
            CLICS.etc_dir.read_csv(
                "families.tsv", 
                dicts=True, 
                delimiter="\t")]
    concepts = {"color": [], "emotion": [], "human body part": []}
    for concept in CLICS.concepts:
        if concept["CONCEPTICON_GLOSS"]:
            concepts[concept["TAG"]] += [concept["CONCEPTICON_GLOSS"]]
    args.log.info("loaded concepts and families")
    for family in families:
        if CLICS.dir.joinpath("output", "graphs",
                "{0}.gml".format(family)).exists():
            igr = igraph.read(
                    CLICS.dir.joinpath("output", "graphs",
                        "{0}.gml".format(family)))
            for vs in igr.vs:
                vs["name"] = vs["label"]
            graph = igraph2networkx(igr)
            all_deg = dict(nx.degree(graph, weight=args.weight))
            emo_deg = dict(nx.degree(graph, weight=args.weight, nbunch=[n for n in
                graph.nodes() if n in concepts["emotion"]]))
            bdp_deg = dict(nx.degree(graph, weight=args.weight, nbunch=[n for n in
                graph.nodes() if n in concepts["human body part"]]))
            col_deg = dict(nx.degree(graph, weight=args.weight, nbunch=[n for n in
                graph.nodes() if n in concepts["color"]]))

            emo_val = sum(emo_deg.values())/len(emo_deg)
            bdp_val = sum(bdp_deg.values())/len(bdp_deg)
            col_val = sum(col_deg.values())/len(col_deg)

            rdegs = [0, 0, 0]
            for i in range(args.trials):
                emox = dict(nx.degree(graph, weight=args.weight,
                        nbunch=random.sample(graph.nodes, len(emo_deg))))
                bdpx = dict(nx.degree(graph, weight=args.weight,
                        nbunch=random.sample(graph.nodes, len(bdp_deg))))
                colx = dict(nx.degree(graph, weight=args.weight,
                        nbunch=random.sample(graph.nodes, len(col_deg))))
                if sum(emox.values())/len(emox) > emo_val:
                    rdegs[0] += 1
                if sum(bdpx.values())/len(bdpx) > bdp_val:
                    rdegs[1] += 1
                if sum(colx.values())/len(colx) > col_val:
                    rdegs[2] += 1



            table += [[
                family,
                len(graph),
                len(graph.edges()),
                sum(all_deg.values())/len(all_deg),
                sum(emo_deg.values())/len(emo_deg),
                rdegs[0]/args.trials,
                sum(bdp_deg.values())/len(bdp_deg),
                rdegs[1]/args.trials,
                sum(col_deg.values())/len(col_deg),
                rdegs[2]/args.trials,
                ]]
    print(tabulate(table, headers=["Family", "Nodes", "Edges", "Degree",
        "Emotion", "Emotion R", "Body", "Body R", "Color", "Color R"], floatfmt=".2f", tablefmt="pipe"))
        





