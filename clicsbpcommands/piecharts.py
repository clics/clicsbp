"""
Plot graphs to file.
"""

import networkx as nx
from lexibank_clicsbp import Dataset as CLICSBP
from collections import defaultdict
from matplotlib import pyplot as plt
from random import choice

def register(parser):
    """
    """
    pass
    #add_catalog_spec(parser, 'concepticon')
    #add_format(parser, default="simple")
    #parser.add_argument("--family", default="xxx")
    #parser.add_argument("--mode", default="binary")
    #parser.add_argument("--zero", action="store_true")


def run(args):
    clicsbp = CLICSBP()
    colexifications = clicsbp.dir.read_csv(
            "output/colexifications.tsv",
            delimiter="\t",
            dicts=True)
    relations = clicsbp.dir.read_csv(
            "output/colexification-relations.tsv",
            delimiter="\t",
            dicts=True)
    rels = {}
    for row in relations:
        # change choice() to row["Relation"] !
        rels[row["NodeA"], row["NodeB"]] = choice(["1", "2", "3"])
        rels[row["NodeB"], row["NodeA"]] = rels[row["NodeA"], row["NodeB"]]


    data = defaultdict(lambda : defaultdict(list))
    for row in colexifications:
        data[row["FAMILY"]][row["TAG"]] += [
                (
                            row["CONCEPT"], 
                            row["COMMUNITY"],
                            row["LINKS"].split(";")
                            )
                        ]
    colors = [
        "#a6cee3",
        "#1f78b4",
        "#b2df8a"]
    pies = {}
    for fam in data:
        plt.clf()
        args.log.info("loading {0}".format(fam))
        G = nx.Graph()
        coms = defaultdict(list)
        for con, com, lnks in data[fam]["human body part"]:
            coms[com] += [con]
            if not con in G.nodes:
                G.add_node(con, community=com)
            for lnk in lnks:
                if lnk:
                    conB, weight = lnk.split(":")
                    weight = float(weight)
                    if not conB in G.nodes:
                        G.add_node(con, community=com)
                    G.add_edge(con, conB, weight=weight)
        # get relations
        relidx = {"1": 0, "2": 1, "3": 2}
        this_pie = [0, 0, 0]
        for nodeA, nodeB in G.edges:
            try:
                this_pie[relidx[rels[nodeA, nodeB]]] += 1
            except:
                print(fam, nodeA, nodeB)
        pies[fam] = this_pie
        plt.pie(this_pie, colors=colors)
        plt.savefig(
                clicsbp.dir.joinpath(
                    "output", 
                    "plots",
                    "pie-"+fam+".png")
                )
        plt.clf()
    with open(clicsbp.dir.joinpath(
        "output",
        "pie-chart-data.tsv"), "w") as f:
        for fam, pie in pies.items():
            f.write("{0}\t{1}\t{2}\t{3}\t{4:.2f}\t{5:.2f}\t{6:.2f}\n".format(
                fam,
                pie[0],
                pie[1],
                pie[2],
                pie[0]/len(rels),
                pie[1]/len(rels),
                pie[2]/len(rels)))




