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
    parser.add_argument("--weight", default="Language_Count_Weighted")
    parser.add_argument("--factor", default=2, type=int)
    parser.add_argument("--tag", default="human body part")
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
        data[row["Family"]][row["Tag"]] += [
                (
                            row["Concept"], 
                            row["Random_Walk_Community"],
                            row[args.weight].split(";"),
                            row["Random_Walk_Links"].split(";")
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
        plt.clf()
        args.log.info("loading {0}".format(fam))
        G = nx.Graph()
        coms = defaultdict(list)
        for con, com, lnks, rwlnks in data[fam][args.tag]:
            coms[com] += [con]
            if not con in G.nodes:
                G.add_node(con, community=com)
            
            for lnk in rwlnks:
                if lnk:
                    conB, weight = lnk.split(":")
                    weight = float(weight)
                    if not conB in G.nodes:
                        G.add_node(con, community=com)
                    G.add_edge(con, conB, weight=weight, rw=1)
            for lnk in lnks:
                if lnk:
                    conB, weight = lnk.split(":")
                    weight = float(weight)
                    if not conB in G.nodes:
                        G.add_node(con, community=com)
                    G.add_edge(con, conB, weight=weight, rw=0)

        # TODO hook in the new positions
        pos = nx.nx_agraph.graphviz_layout(G)
        for nA, nB, data_ in G.edges(data=True):
            if data_["rw"] == 0:
                alpha = 1
                color = "red"
                width=10*data_["weight"]
            else:
                alpha = 0.5
                color = "lightgray"
                width=2.5*data_["weight"]
            nx.draw_networkx_edges(
                    G, 
                    pos, 
                    width=width, 
                    alpha=alpha, 
                    edgelist=[(nA, nB)],
                    edge_color=color
                    )
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
                    node_size=30,
                    alpha=0.25,
                    nodelist=coms["0"],
                    node_color="white"
                    )

        #nx.draw_networkx_nodes(G, pos, node_size=10)
        #nx.draw_networkx_edges(G, pos, width=2)
        nx.draw_networkx_labels(G, pos, font_size=12)
        plt.axis("off")
        plt.savefig(clicsbp.dir.joinpath("output", "plots",
            "{0}-{1}-{2}.png".format(fam, args.tag.replace(" ", "_"), args.weight.lower())).as_posix())




