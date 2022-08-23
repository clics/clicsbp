"""
Calculate colexification network for all data.
"""
from cltoolkit import Wordlist
from pycldf import Dataset
from itertools import combinations
import networkx as nx
from collections import defaultdict
from lingpy.convert.graph import networkx2igraph
import html


from lexibank_clicsbp import Dataset as _CLICS

def register(parser):

    parser.add_argument(
            "--community-method",
            help="community method",
            default="infomap")

    parser.add_argument(
            "--weight",
            help="determine the weight to use",
            default="language_weight")

    parser.add_argument(
            "--normalize",
            help="normalize weights",
            action="store_true"
            )

    
def get_colexifications(wordlist, concepts):
    G = nx.Graph()
    languages = [language for language in wordlist.languages]
    for language in languages:
        cols = defaultdict(list)
        for form in language.forms:
            if form.concept.concepticon_gloss in concepts:
                tform = str(form.form)
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


def run(args):

        CLICS = _CLICS()

        wl = Wordlist(
                [Dataset.from_metadata(CLICS.cldf_dir / "cldf-metadata.json")]
        )
        args.log.info("loaded wordlist")
        concepts = [concept["CONCEPTICON_GLOSS"] for concept in CLICS.concepts if concept[
            "TAG"] == "human body part"]
        args.log.info("loaded concepts")
        

        G = get_colexifications(wl, concepts)
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
            table += [[nA, nB, data["family_weight"], data["language_weight"], clusters[nA], clusters[nB]]]
        with open(CLICS.dir / "output" / "all-data-colexifications.tsv", "w") as f:
            f.write("NodeA\tNodeB\tFamilyWeight\tLanguageWeight\tCommunityA\tCommunityB\n")
            for row in table:
                f.write("\t".join([str(x) for x in row])+"\n")




    


    
