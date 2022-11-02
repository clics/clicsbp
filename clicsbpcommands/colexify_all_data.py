"""
Calculate colexification network for all data.
"""
from cltoolkit import Wordlist
from pycldf import Dataset
from itertools import combinations
import networkx as nx
from collections import defaultdict
from lingpy.convert.graph import networkx2igraph
from pyclics.colexifications import get_colexifications
import html
from pyclts import CLTS


from lexibank_clicsbp import Dataset as _CLICS

def register(parser):

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
            action="store_true"
            )

    



def run(args):

        CLICS = _CLICS()
        
        clts = CLTS()
        wl = Wordlist(
                [Dataset.from_metadata(CLICS.cldf_dir / "Wordlist-metadata.json")],
                ts=clts.bipa
        )
        args.log.info("loaded wordlist")
        concepts = [concept["CONCEPTICON_GLOSS"] for concept in CLICS.concepts if concept[
            "TAG"] == "human body part"]
        args.log.info("loaded concepts")
        

        G = get_colexifications(wl, family=None, concepts=concepts)
        IG = networkx2igraph(G)
        if args.community_method == "infomap":
            comms = IG.community_infomap(edge_weights=args.weight, vertex_weights=args.weight)
        else:
            args.log.info("only infomap implemented so far")
            raise ValueError

        clusters = {}
        for i, nodes in enumerate(comms):
            for node in nodes:
                clusters[IG.vs[node]["Name"]] = i+1
                G.nodes[IG.vs[node]["Name"]]["community"] = str(i+1)
        table = []
        for nA, nB, data in sorted(G.edges(data=True), key=lambda x: x[2][args.weight], reverse=True):
            table += [[nA, nB, data["family_count"], data["language_count"], clusters[nA], clusters[nB]]]
        with open(CLICS.dir / "output" / "colexifications-global.tsv", "w") as f:
            f.write("Concept_A\tConcept_B\tFamily_Count\tLanguage_Count\tCommunity_A\tCommunity_B\n")
            for row in table:
                f.write("\t".join([str(x) for x in row])+"\n")
        with open(CLICS.dir / "output" / "graph.gml", "w") as f:
            for line in nx.generate_gml(G):
                f.write(html.unescape(line)+"\n")


    


    
