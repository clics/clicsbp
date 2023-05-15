# CLDF dataset on Body Part Colexifications

## How to cite

If you use these data please cite
this dataset using the DOI of the [particular released version](../../releases/) you were using

## Description


This dataset is licensed under a CC-BY-4.0 license

## Notes

# Workflow Instructions

To run the code, you need to follow specific workflow instructions

## 1 Install Packages

- glottolog
- concepticon
- clts

## 2 Download Data

## 3 Create CLICS4 Dataset

```
cldfbench lexibank.makecldf --glottolog-repos=Path2Glottolog --concepticon-repos=Path2Concepticon --clts-repos=Path2Clics --glottolog-version=v4.6 --concepticon-version=v2.6.0 --clts-version=v2.2.0 lexibank_clicsbp.py
```

## 4 Compute Colexifications

Make sure to install pyclics, download via git, checkout branch `colexifications`, and then install the package.

```
cldfbench clicsbp.colexifications
cldfbench clicsbp.colexify_all_data
```

## 5 Compute Statistics

### 5.1 Compute Pie-Charts

```
cldfbench clicspb.piecharts --weight=Language_Count_Weighted
```

### 5.2 Compute ARI

### 5.3 Plot Networks

```
cldfbench clicsbp.plotgraphs --weight=Cognate_Count_Weighted --tag="human body part"
```



## Statistics


![Glottolog: 100%](https://img.shields.io/badge/Glottolog-100%25-brightgreen.svg "Glottolog: 100%")
![Concepticon: 100%](https://img.shields.io/badge/Concepticon-100%25-brightgreen.svg "Concepticon: 100%")
![Source: 0%](https://img.shields.io/badge/Source-0%25-red.svg "Source: 0%")
![BIPA: 100%](https://img.shields.io/badge/BIPA-100%25-brightgreen.svg "BIPA: 100%")
![CLTS SoundClass: 100%](https://img.shields.io/badge/CLTS%20SoundClass-100%25-brightgreen.svg "CLTS SoundClass: 100%")

- **Varieties:** 1,033
- **Concepts:** 1,500
- **Lexemes:** 695,697
- **Sources:** 0
- **Synonymy:** 1.14
- **Invalid lexemes:** 0
- **Tokens:** 4,077,058
- **Segments:** 1,389 (0 BIPA errors, 0 CLTS sound class errors, 1381 CLTS modified)
- **Inventory size (avg):** 44.37

## Possible Improvements:

- Languages linked to [bookkeeping languoids in Glottolog](http://glottolog.org/glottolog/glottologinformation#bookkeepinglanguoids):
  - Rawngtu Weilong [wela1234](http://glottolog.org/resource/languoid/id/wela1234)
  - Sanapaná (Angaité) [sana1281](http://glottolog.org/resource/languoid/id/sana1281)


- Entries missing sources: 695697/695697 (100.00%)

## CLDF Datasets

The following CLDF datasets are available in [cldf](cldf):

- CLDF [Wordlist](https://github.com/cldf/cldf/tree/master/modules/Wordlist) at [cldf/Wordlist-metadata.json](cldf/Wordlist-metadata.json)