import pathlib
import collections

import pycldf
from pylexibank.dataset import CLDFSpec
from pylexibank.cldf import LexibankWriter
from pylexibank import Dataset as BaseDataset
from cltoolkit import Wordlist
from git import Repo
from clldutils.misc import slug
from csvw.dsv import UnicodeWriter

from pylexibank import Concept, Lexeme, Language, progressbar
import attr

LANGUAGES = 250

@attr.s
class CustomConcept(Concept):
    Tag = attr.ib(default=None)


@attr.s
class CustomLexeme(Lexeme):
    ConceptInSource = attr.ib(default=None)

@attr.s
class CustomLanguage(Language):
    Concept_Count = attr.ib(default=None, metadata={"format": "integer"})
    Form_Count = attr.ib(default=None, metadata={"format": "integer"})


class Dataset(BaseDataset):
    dir = pathlib.Path(__file__).parent
    id = "clicsbp"
    concept_class = CustomConcept
    lexeme_class = CustomLexeme
    language_class = CustomLanguage

    @property
    def output(self):
        return self.dir / 'output'

    def read_etc(self, what):
        return self.etc_dir.read_csv('{}.tsv'.format(what), delimiter="\t", dicts=True)

    def cldf_specs(self):  # A dataset must declare all CLDF sets it creates.
        res = BaseDataset.cldf_specs(self)
        res.zipped = ['FormTable']
        return res

    def cmd_download(self, args):
        for dataset in self.read_etc("datasets"):
            if self.raw_dir.joinpath(dataset["ID"], "cldf", "cldf-metadata.json").exists():
                args.log.info("skipping {0}".format(dataset["ID"]))
            else:
                args.log.info("cloning {0} to raw/{0}".format(dataset["ID"]))
                Repo.clone_from(
                    "https://github.com/{}/{}.git".format(
                        dataset["Organisation"], dataset["Repository"]),
                    self.raw_dir / dataset["ID"])

    def cmd_makecldf(self, args):
        datasets = [
            pycldf.Dataset.from_metadata(self.raw_dir / ds["ID"] / "cldf/cldf-metadata.json")
            for ds in self.read_etc("datasets")]
        args.log.info("loaded datasets")
        wl = Wordlist(datasets, ts=args.clts.api.bipa)

        # sort the concepts by number of unique glottocodes
        all_concepts = sorted(
            wl.concepts,
            key=lambda x: len(set([form.language.glottocode for form in x.forms_with_sounds])),
            reverse=True)
        unmerge = collections.defaultdict(set)
        for concept in self.concepts:
            for gloss in concept["BROADER_CONCEPT"].split(" // "):
                unmerge[gloss].add(concept["CONCEPTICON_GLOSS"])

        #
        # FIXME: Why this somewhat magic cutoff at 1500 concepts?
        #
        selected_concepts = [
            concept.id for concept in all_concepts if concept.id not in unmerge][:1500]

        # get valid languages
        valid_languages = []
        valid_glottocodes = set()
        for language in sorted(
                wl.languages,
                key=lambda x: len([c for c in x.concepts if c.id in selected_concepts]),
                reverse=True):
            if language.glottocode not in valid_glottocodes:
                cov = sum([
                    len(unmerge.get(c.id, [""])) for c in language.concepts
                    if c.id in unmerge or c.id in selected_concepts])
                if language.latitude and cov >= LANGUAGES:
                    valid_glottocodes.add(language.glottocode)
                    valid_languages.append(language.id)

        args.log.info("found {0} valid languages".format(len(valid_languages)))

        concepts = {concept["CONCEPTICON_GLOSS"]: concept["TAG"] for concept in self.concepts}
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
        clics = []
        accepted_languages = []
        for language in wl.languages:
            if (language.glottocode and language.id in valid_languages):
                args.log.info("Processing {0}".format(language.id))
                #
                # FIXME: Why do we have two counters which count exactly the same things?
                #
                cnc_count, frm_count = 0, 0
                for form in language.forms_with_sounds:
                    if (form.concept and form.concept.concepticon_gloss in
                            concepts and form.concept.concepticon_gloss in
                            selected_concepts):
                        clics.append([
                            language.id,
                            form.id,
                            form.concept.id,
                            form.value,
                            form.form,
                            form.sounds,
                            language.family,
                            ""
                        ])
                        cnc_count += 1
                        frm_count += 1
                    elif (form.concept and form.concept.concepticon_gloss in unmerge):
                        for gloss in unmerge[form.concept.concepticon_gloss]:
                            if gloss in selected_concepts:
                                clics.append([
                                    language.id,
                                    form.id,
                                    gloss,
                                    form.value,
                                    form.form,
                                    form.sounds,
                                    language.family,
                                    form.concept.id])
                                cnc_count += 1
                                frm_count += 1
                    elif (form.concept and form.concept.concepticon_gloss in selected_concepts):
                        clics.append([
                            language.id,
                            form.id,
                            form.concept.id,
                            form.value,
                            form.form,
                            form.sounds,
                            language.family,
                            ""
                        ])
                        cnc_count += 1
                        frm_count += 1
                        if form.concept.name not in new_concepts:
                            new_concepts[form.concept.name] = form.concept
                args.writer.add_language(
                    ID=language.id,
                    Name=language.name,
                    Family=language.family,
                    Latitude=language.latitude,
                    Longitude=language.longitude,
                    Glottocode=language.glottocode,
                    Concept_Count=cnc_count,
                    Form_Count=frm_count
                )
                accepted_languages += [language.id]
                args.log.info("... added {0} with {1} concepts".format(language.id, cnc_count))

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

        for lng_id, frm_id, cnc_id, frm_val, frm_frm, frm_snd, _, cnc_is in progressbar(
                clics, desc="adding forms"):
            args.writer.add_form_with_segments(
                Local_ID=frm_id,
                Parameter_ID=slug(cnc_id, lowercase=False),
                Language_ID=lng_id,
                Value=frm_val,
                Form=frm_frm,
                Segments=frm_snd,
                ConceptInSource=cnc_is
            )

        # add info on coverage
        coverage = collections.defaultdict(dict)
        perfamily = collections.defaultdict(lambda: collections.defaultdict(list))
        poweran = {
            concept.id: {language: 0 for language in accepted_languages}
            for concept in all_concepts}
        families = set()
        for language, _, concept, _, _, _, family, _ in clics:
            coverage[concept][language] = family
            perfamily[concept][family] += [language]
            poweran[concept][language] = 1
            families.add(family)

        with UnicodeWriter(self.dir / "output" / "power_analysis.tsv", delimiter='\t') as f:
            for concept in coverage:
                for language in coverage[concept]:
                    f.writerow([
                        concept,
                        concepts.get(concept, ""),
                        wl.languages[language].family,
                        language,
                        poweran[concept][language]])

        with UnicodeWriter(self.dir / "output" / "coverage.tsv", delimiter='\t') as f:
            f.writerow("Concept Tag Languages Families".split())
            for k, vals in coverage.items():
                f.writerow([k, concepts[k], len(vals), len(set(vals.values()))])

        # make big coverage map 
        with UnicodeWriter(self.dir / "output" / "coverage-per-family.tsv", delimiter='\t') as f:
            f.writerow(["Concept", "Tag"] + sorted(families))
            for concept in perfamily:
                f.writerow(
                    [concept, concepts[concept]] +
                    [len(set(perfamily[concept][fam])) for fam in sorted(families)])
