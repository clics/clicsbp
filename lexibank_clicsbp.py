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
from pathlib import Path


from pylexibank import Concept, Lexeme, progressbar
import attr
from csvw.dsv import UnicodeWriter
import json


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
        
        if self.raw_dir.joinpath("norare-data").exists():
            pass
        else:
            args.log.info("downloading norare data")
            repo = Repo.clone_from(
                    "https://github.com/concepticon/norare-data.git",
                    self.raw_dir / "norare-data")



    def cmd_makecldf(self, args):

        datasets = [pycldf.Dataset.from_metadata(
            self.raw_dir / ds["ID"] / "cldf/cldf-metadata.json") for ds in
            self.etc_dir.read_csv("datasets.tsv", delimiter="\t", dicts=True) if ds["CLTS"] == "1"]
        args.log.info("loaded datasets")
        wl = Wordlist(datasets, ts=args.clts.api.bipa)

        # sort the concepts by number of unique glottocodes
        all_concepts = sorted(
                wl.concepts,
                key=lambda x: len(set([form.language.glottocode for form in
                    x.forms_with_sounds])),
                reverse=True)
        selected_concepts = [concept.id for concept in all_concepts[:1000]]

        # get valid languages
        valid_languages = []
        visited = set()
        for language in sorted(
                wl.languages,
                key=lambda x: len([c for c in x.concepts if c.id in
                    selected_concepts]),
                reverse=True):
            if language.glottocode in visited:
                pass
            else:
                visited.add(language.glottocode)
                valid_languages.append(language.id)

        args.log.info("found {0} valid languages".format(len(valid_languages)))

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
            if concept["CONCEPTICON_GLOSS"] in selected_concepts:
                args.writer.add_concept(
                        ID=slug(concept["CONCEPTICON_GLOSS"], lowercase=False),
                        Name=concept["ENGLISH"],
                        Concepticon_ID=concept["CONCEPTICON_ID"],
                        Concepticon_Gloss=concept["CONCEPTICON_GLOSS"],
                        Tag=concept["TAG"]
                        )
        args.log.info("added concepts")
        
        new_concepts = {}

        for language in wl.languages:
            if (language.family in families and language.glottocode and
                    language.id in valid_languages):
                args.writer.add_language(
                        ID=language.id,
                        Name=language.name,
                        Family=language.family,
                        Latitude=language.latitude,
                        Longitude=language.longitude,
                        Glottocode=language.glottocode)
                args.log.info("Processing {0}".format(language.id))
                for form in language.forms_with_sounds:
                    if (form.concept and form.concept.concepticon_gloss in
                            concepts and form.concept.concepticon_gloss in
                            selected_concepts):
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
                    elif (form.concept and form.concept.concepticon_gloss in
                            unmerge):
                        for gloss in unmerge[form.concept.concepticon_gloss]:
                            if gloss in selected_concepts:
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
                    elif (form.concept and form.concept.concepticon_gloss in
                            selected_concepts):
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
                        if form.concept.name not in new_concepts:
                            new_concepts[form.concept.name] = form.concept

        # add remaining concepts
        for concept in new_concepts.values():
            args.writer.add_concept(
                    ID=slug(concept.concepticon_gloss, lowercase=False),
                    Name=concept.name,
                    Concepticon_ID=concept.concepticon_id,
                    Concepticon_Gloss=concept.concepticon_gloss,
                    Tag=""
                    )
            concepts[concept.concepticon_gloss] = ""
        args.log.info("added remaining concepts")

        wll = lingpy.Wordlist(D)
        for idx in progressbar(wll, desc="adding forms"):
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
        poweran = {concept: {language: 0 for language in wll.cols} for concept
                in wll.rows}
        for idx, concept, language, family in wll.iter_rows(
                "concept", "doculect", "family"):
            coverage[concept][language] = family
            perfamily[concept][family] += [language]
            poweran[concept][language] = 1

        with open(self.dir / "output" / "power_analysis.tsv", "w") as f:
            for concept in wll.rows:
                for language in wll.cols:
                    f.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(
                        concept,
                        concepts.get(concept, ""),
                        wl.languages[language].family,
                        language,
                        poweran[concept][language]))

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







