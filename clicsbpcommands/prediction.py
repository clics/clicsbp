"""
Prediction study.
"""

from lexibank_clicsbp import Dataset as CLICSBP
from pynorare import NoRaRe
from collections import defaultdict
from itertools import combinations
from clldutils.clilib import Table, add_format
from cldfbench.cli_util import add_catalog_spec
from pylexibank import progressbar
from sklearn.inspection import permutation_importance
from sklearn import svm, naive_bayes
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, f1_score
from sklearn.linear_model import LogisticRegression



def register(parser):
    """
    """
    add_catalog_spec(parser, 'concepticon')
    add_format(parser, default="simple")
    parser.add_argument("--domain", default="emotion")
    parser.add_argument("--family", default="xxx")
    parser.add_argument("--mode", default="binary")
    parser.add_argument("--zero", action="store_true")


def run(args):
    clicsbp = CLICSBP()
    colexifications = clicsbp.dir.read_csv(
            "output/colexifications.tsv",
            delimiter="\t",
            dicts=True)
    # get concepticon id from concepticon gloss
    cgl2id = {
            c.gloss: c.id for c in args.concepticon.api.conceptsets.values()}

    args.log.info("preparing test data")
    nor = NoRaRe(clicsbp.raw_dir.joinpath("norare-data"))
    # load norms by jackson
    jackson = nor.datasets["Jackson-2019-24"]
    
    # we load only emotion concepts now
    features = [
            "valence", "activation", "dominance", "certainty",
            "approach_avoidance", "sociality"]
    data = defaultdict(list)
    for row in colexifications:
        if row["TAG"] == args.domain:
            cid = int(cgl2id[row["CONCEPT"]])
            if cid in jackson.concepts and jackson.concepts[cid][features[0]]:
                scores = [jackson.concepts[cid][f] or 0 for f in features]
                data[row["FAMILY"]] += [
                        (
                            cid, row["CONCEPT"], row["COMMUNITY"], scores
                            )
                        ]
    args.log.info("assembled data for "+args.domain)

    # now we can make our test and training data
    comps = {k: [] for k in data.keys()}
    tests = {k: [] for k in data.keys()}
    results = {k: [] for k in data.keys()}

    # iterate over families

    for family, forms in progressbar(data.items()):
        #print(family, forms)
        com_idx = max([int(x[2]) for x in forms])+1
        if args.mode != "binary":
            for cid, con, com, scores in forms:
                if com != "0" or args.zero:
                    if args.zero and com == "0":
                        com = com_idx
                        com_idx += 1
                    comps[family] += [con]
                    tests[family] += [scores]
                    results[family] += [int(com)]
        else:
            for (cidA, conA, comA, scoresA), (cidB, conB, comB, scoresB) in combinations(forms, r=2):
                scoresAB = [a-b if a > b else b-a for a, b in zip(scoresA, scoresB)]
                if (comA == "0" or comB == "0") and not args.zero:
                    pass
                else:
                    comps[family] += [conA, conB]
                    tests[family] += [scoresAB]
                    if comA != comB or "0" in (comA, comB):
                        results[family] += [0]
                    else:
                        results[family] += [1]
    args.log.info("computed test and results")
    for family, X in tests.items():
        args.log.info("fitting data for {0}".format(family))
        Y = results[family]
        tabs = []
        if len(set(Y)) > 1:
            scaler = StandardScaler().fit(X)
            XS = scaler.transform(X)

            for i in range(len(features)):
                XSN = []
                for row in XS:
                    new_row = []
                    for j in range(len(features)):
                        if j != i:
                            new_row += [row[j]]
                    XSN += [new_row]
                clf = svm.SVC(kernel="linear")
                clf.fit(XSN, Y)
                y_pred = []
                for row in XSN:
                    y_p = clf.predict([row])
                    y_pred.append(y_p[0])
                acc = accuracy_score(Y, y_pred, normalize=True)
                tabs += [[features[i], acc]]
            clf = svm.SVC(kernel="linear")
            clf = naive_bayes.GaussianNB()
            clf = RandomForestRegressor()
            clf = LinearRegression(random_state=0, multiclass="multinomial")
            clf.fit(XS, Y)
            r = permutation_importance(clf, XS, Y, n_repeats=100, random_state=0)
            #r = clf.feature_importances_
            print("# {0} ({1})".format(family, len(Y)))
            ff = features + features
            with Table("feature", "importance", "std") as table:
                #for a, b in tabs:
                #    table.append([a, b, 0])
                for i in range(len(features)):
                    table.append(
                            [
                                features[i], 
                                r.importances_mean[i], 
                                0, #r.importances_std[i]
                                ]
                            )
        else:
            print("# Skipping family {0}".format(family))

        input()
    
