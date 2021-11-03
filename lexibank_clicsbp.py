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


from pylexibank import Concept
import attr


@attr.s
class CustomConcept(Concept):
    Tag = attr.ib(default=None)



class Dataset(BaseDataset):
    dir = pathlib.Path(__file__).parent
    id = "clicsbp"
    concept_class = CustomConcept


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
                    "family"]
                }
        idx = 1
        
        families = [
                "Hmong-Mien", "Uralic", "Indo-European", "Afro-Asiatic",
                "Sino-Tibetan", "Niger-Congo", "Dogon"]
        concepts = {concept["CONCEPTICON_GLOSS"]: concept["TAG"] for concept in
                self.concepts}
        for concept in self.concepts:
            args.writer.add_concept(
                    ID=slug(concept["CONCEPTICON_GLOSS"], lowercase=False),
                    Name=concept["ENGLISH"],
                    Concepticon_ID=concept["CONCEPTICON_ID"],
                    Concepticon_Gloss=concept["CONCEPTICON_GLOSS"],
                    Tag=concept["TAG"]
                    )
        args.log.info("added concepts")


        for language in wl.languages:
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
                                language.family
                                ]
                        idx += 1
        wll = lingpy.Wordlist(D)
        for idx in wll:
            args.writer.add_form_with_segments(
                    Local_ID=wll[idx, "formid"],
                    Parameter_ID=slug(wll[idx, "concept"], lowercase=False),
                    Language_ID=wll[idx, 'doculect'],
                    Value=wll[idx, "value"],
                    Form=wll[idx, "form"],
                    Segments=wll[idx, "tokens"]
                    )






