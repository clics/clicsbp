"""
Plot graphs to file.
"""

import networkx as nx
from lexibank_clicsbp import Dataset as CLICSBP
from collections import defaultdict
from matplotlib import pyplot as plt

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
        "#b2df8a",
        "#33a02c",
        "#fb9a99",
        "#e31a1c",
        "#fdbf6f",
        "#ff7f00",
        "#cab2d6",
        "#6a3d9a",
        "#ffff99",
        "#b15928",
            ]
    for fam in data:
        for tag in ["human body part", "emotion", "color"]:
            plt.clf()
            args.log.info("loading {0} {1}".format(fam, tag))
            G = nx.Graph()
            coms = defaultdict(list)
            for con, com, lnks in data[fam][tag]:
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
            pos = nx.nx_agraph.graphviz_layout(G)
            for nA, nB, data_ in G.edges(data=True):
                nx.draw_networkx_edges(G, pos, width=2*data_["weight"],
                        #alpha=2*data_["weight"] if data_["weight"] < 1 else 1, 
                        edgelist=[(nA, nB)],
                        edge_color="lightgray")
            all_coms = sorted([c for c in coms if c != "0"])
            for i, com in enumerate(all_coms):
                nodes = coms[com]
                color = colors[i] if i < len(colors) else "black"
                nx.draw_networkx_nodes(G, pos, 
                        node_size=30, 
                        alpha=0.5,
                        nodelist=nodes,
                        node_color=color)
            if "0" in coms:
                nx.draw_networkx_nodes(
                        G,
                        pos,
                        node_size=20,
                        alpha=0.25,
                        nodelist=coms["0"],
                        node_color="white"
                        )

            #nx.draw_networkx_nodes(G, pos, node_size=10)
            #nx.draw_networkx_edges(G, pos, width=2)
            nx.draw_networkx_labels(G, pos, font_size=6)
            plt.axis("off")
            plt.savefig(clicsbp.dir.joinpath("output", "plots",
                "{0}-{1}.pdf".format(fam, tag)).as_posix())




