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
    props = {
            "Adjacency": 0,
            "Shape": 0,
            "Function": 0
            }
    for row in relations:
        # change choice() to row["Relation"] !
        if row["NodeA"] != row["NodeB"]:
            rels[row["NodeA"], row["NodeB"]] = (
                    int(row["Adjacency"]),
                    int(row["Shape"]),
                    int(row["Function"])
                    )
            props["Adjacency"] += int(row["Adjacency"])
            props["Shape"] += int(row["Shape"])
            props["Function"] += int(row["Function"])
            rels[row["NodeB"], row["NodeA"]] = rels[row["NodeA"], row["NodeB"]]

    
    #props["Adjacency"] = props["Adjacency"] / sum(props.values())
    #props["Shape"] = props["Shape"] / sum(props.values())
    #props["Function"] = props["Function"] / sum(props.values())

    data = defaultdict(lambda : defaultdict(list))
    for row in colexifications:
        data[row["FAMILY"]][row["TAG"]] += [
                (
                            row["CONCEPT"], 
                            row["COMMUNITY"],
                            row["COLEXIFICATIONS"].split(";")
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
                    if not con == conB:
                        G.add_edge(con, conB, weight=weight)
        # get relations
        this_pie = [0, 0, 0]
        for nodeA, nodeB in G.edges:
            try:
                this_pie[0] += rels[nodeA, nodeB][0]
                this_pie[1] += rels[nodeA, nodeB][1]
                this_pie[2] += rels[nodeA, nodeB][2]
            except:
                print(fam, nodeA, nodeB)
        prop_pie = [
                this_pie[0] / props["Adjacency"],
                this_pie[1] / props["Shape"],
                this_pie[2] / props["Function"]
                ]

        pies[fam] = (this_pie, prop_pie, len(G), len(G.edges))
        fig, (ax1, ax2) = plt.subplots(1, 2, sharey=True)
        ax1.pie(this_pie, colors=colors, labels=["Adjacency", "Shape", "Function"])
        ax1.set_title("Raw Scores")
        ax2.pie(prop_pie, colors=colors, labels=["Adjacency", "Shape", "Function"])
        ax2.set_title("Weighted by Proportions")
        fig.suptitle("Family {0} / {1} edges".format(fam, len(G.edges)))
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
        for fam, (pie, pieprop, leng, lengedges) in pies.items():
            f.write("{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6:.2f}\t{7:.2f}\t{8:.2f}\n".format(
                fam,
                str(leng),
                str(lengedges),
                pie[0],
                pie[1],
                pie[2],
                pieprop[0],
                pieprop[1],
                pieprop[2])
                )




