import pathlib
import zipfile
import itertools
import collections

import pycldf
from cldfbench import CLDFSpec
from pylexibank import Dataset as BaseDataset
from cltoolkit import Wordlist
from cltoolkit.features import FEATURES
from cldfzenodo import oai_lexibank
from pyclts import CLTS
from git import Repo, GitCommandError
from csvw.dsv import reader
import lingpy
from clldutils.misc import slug
from tabulate import tabulate


from pylexibank import Concept, Lexeme, progressbar
import attr


@attr.s
class CustomConcept(Concept):
    Tag = attr.ib(default=None)


@attr.s
class CustomLexeme(Lexeme):
    ConceptInSource = attr.ib(default=None)


class Dataset(BaseDataset):
    dir = pathlib.Path(__file__).parent
    id = "clicsbp"
    concept_class = CustomConcept
    lexeme_class = CustomLexeme

    def cmd_download(self, args):
        for dataset in self.etc_dir.read_csv(
                "datasets.tsv", delimiter="\t",
                dicts=True):
            if self.raw_dir.joinpath(
                    dataset["ID"], "cldf", "cldf-metadata.json").exists():
                args.log.info("skipping {0}".format(dataset["ID"]))
            else:
                args.log.info("cloning {0} to raw/{0}".format(dataset["ID"]))
                repo = Repo.clone_from(
                        "https://github.com/"+
                        dataset["Organisation"]+"/"+
                        dataset["Repository"]+'.git',
                        self.raw_dir / dataset["ID"])


    def cmd_makecldf(self, args):

        datasets = [pycldf.Dataset.from_metadata(
            self.raw_dir / ds["ID"] / "cldf/cldf-metadata.json") for ds in
            self.etc_dir.read_csv("datasets.tsv", delimiter="\t", dicts=True) \
                    ]
        args.log.info("loaded datasets")
        wl = Wordlist(datasets, ts=args.clts.api.bipa)
        D = {
                0: [
                    "doculect", "formid", "concept", "value", "form", "tokens", 
                    "family", "conceptinsource"]
                }
        idx = 1
        
        families = [k["Family"] for k in self.etc_dir.read_csv("families.tsv",
            delimiter="\t", dicts=True)]
        concepts = {concept["CONCEPTICON_GLOSS"]: concept["TAG"] for concept in
                self.concepts}
        unmerge = collections.defaultdict(set)
        for concept in self.concepts:
            for gloss in concept["BROADER_CONCEPT"].split(" // "):
                unmerge[gloss].add(concept["CONCEPTICON_GLOSS"])
                
        for concept in self.concepts:
            args.writer.add_concept(
                    ID=slug(concept["CONCEPTICON_GLOSS"], lowercase=False),
                    Name=concept["ENGLISH"],
                    Concepticon_ID=concept["CONCEPTICON_ID"],
                    Concepticon_Gloss=concept["CONCEPTICON_GLOSS"],
                    Tag=concept["TAG"]
                    )
        args.log.info("added concepts")


        for language in progressbar(wl.languages, desc="adding forms"):
            if language.family in families:
                args.writer.add_language(
                        ID=language.id,
                        Name=language.name,
                        Family=language.family,
                        Latitude=language.latitude,
                        Longitude=language.longitude,
                        Glottocode=language.glottocode)
                args.log.info("Processing {0}".format(language.id))
                for form in language.forms_with_sounds:
                    if form.concept and form.concept.concepticon_gloss in concepts:
                        D[idx] = [
                                language.id,
                                form.id,
                                form.concept.id,
                                form.value,
                                form.form,
                                form.sounds,
                                language.family,
                                ""
                                ]
                        idx += 1
                    elif form.concept and form.concept.concepticon_gloss in unmerge:
                        for gloss in unmerge[form.concept.concepticon_gloss]:
                            D[idx] = [
                                    language.id,
                                    form.id,
                                    gloss,
                                    form.value,
                                    form.form,
                                    form.sounds,
                                    language.family,
                                    form.concept.id]
                            idx += 1

        wll = lingpy.Wordlist(D)
        for idx in wll:
            args.writer.add_form_with_segments(
                    Local_ID=wll[idx, "formid"],
                    Parameter_ID=slug(wll[idx, "concept"], lowercase=False),
                    Language_ID=wll[idx, 'doculect'],
                    Value=wll[idx, "value"],
                    Form=wll[idx, "form"],
                    Segments=wll[idx, "tokens"],
                    ConceptInSource=wll[idx, "conceptinsource"]
                    )

        # add info on coverage
        coverage = collections.defaultdict(dict)
        perfamily = collections.defaultdict(lambda :
                collections.defaultdict(list))
        for idx, concept, language, family in wll.iter_rows(
                "concept", "doculect", "family"):
            coverage[concept][language] = family
            perfamily[concept][family] += [language] 
        with open(self.dir / "output" / "coverage.tsv", "w") as f:
            f.write("Concept\tTag\tLanguages\tFamilies\n")
            for k, vals in coverage.items():
                f.write("{0}\t{1}\t{2}\t{3}\n".format(
                    k, concepts[k], len(vals), len(set(vals.values()))))

        # make big coverage map 
        with open(self.dir / "output" / "coverage-per-family.tsv", "w") as f:
            f.write("Concept\tTag")
            for fam in sorted(families):
                f.write("\t"+fam)
            f.write("\n")
            for concept in perfamily:
                f.write("{0}\t{1}".format(concept, concepts[concept]))
                for fam in families:
                    f.write("\t{0}".format(len(set(perfamily[concept][fam]))))
                f.write("\n")







