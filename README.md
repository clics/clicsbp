# CLDF dataset on Body Part Colexifications

## How to cite

If you use these data please cite
this dataset using the DOI of the [particular released version](../../releases/) you were using

## Description

This dataset is licensed under a CC-BY-4.0 license.

## Notes

The repository includes:

- data in [CLDF](/cldf)
- [commands](/clicsbpcommands) to compile the colexifications
- [inventory](/etc) of concepts, Lexibank datasets, and language families 
- table with [forms](/examples/clicsbp.tsv)
- [output](/output) including graphs, plots, and degrees
- [raw](/raw) data folder for local clones of the Lexibank repositories
- [scripts](/scripts) for the analyses of ARI and degree values


# Installation

To run the code, you need to install the following. We recommend to use a fresh virtual environment.

Clone the GitHub repository in a local folder:

```
$ git clone https://github.com/clics/clicsbp.git
```

Change the directory to `clicsbp` and run:

```
$ pip install -e .
```

Check if everything worked by typing `cldfbench -h`. If you see commands starting with `clicsbp.`, you will be able to run the following code.

In addition, you need the packages from our other reference catalogs ([Glottolog](https://pypi.org/project/pyglottolog/), [Concepticon](https://pypi.org/project/pyconcepticon/), [CLTS](https://pypi.org/project/pyclts/)) and the `pyclics` package. Make sure to install `pyclics` by downloading the [GitHub repository](https://github.com/clics/pyclics), checking out the branch `colexifications`, and then installing the package with `pip install -e .`.


# Download the Lexibank datasets

This command downloads the Lexibank datasets in the local `raw` folder. 

```
$ cldfbench download lexibank_clicsbp.py
```


# Create CLDF Dataset

To create the CLDF dataset with the colexifications aggregated from the Lexibank word lists, use:

```
$ cldfbench lexibank.makecldf lexibank_clicsbp.py --concepticon-version=v3.1.0 --clts-version=v2.2.0 --glottolog-version=v4.8
```

Note that the versions of the reference catalogs change and might need to be adapted in the future.


# Colexifications and Analyses

Now,you are able to compute the colexifications and perform the analysis. First, run:

```
$ cldfbench clicsbp.colexifications
$ cldfbench clicsbp.colexify_all_data
```

## Compute Coverage

Calculate the coverage of the data with:

```
$ cldfbench clicsbp.coverage
```

## Compute ARI, AMI, and BCubes Statistics

The values can be created for each of the semantic domains by typing:

```
$ cldfbench clicsbp.ari --tag "human body part"
$ cldfbench clicsbp.ari --tag "emotion"
$ cldfbench clicsbp.ari --tag "color"
```

## Compute Degrees

Examine the degree distributions across, for example, language weight with:

```
$ cldfbench clicsbp.degrees --weight "language"
```

## Plot Graphs

To create images of the networks with body part colexifications for each of the 20 language families, use:

```
$ cldfbench clicsbp.plotgraphs --weight=Cognate_Count_Weighted --tag="human body part"
```

## Plot Pie-Charts

The cognitive relations associated with body part colexifications can be explored by creating pie-charts of the data.

```
$ cldfbench clicsbp.piecharts --weight=Language_Count_Weighted
```



## Statistics


![Glottolog: 100%](https://img.shields.io/badge/Glottolog-100%25-brightgreen.svg "Glottolog: 100%")
![Concepticon: 100%](https://img.shields.io/badge/Concepticon-100%25-brightgreen.svg "Concepticon: 100%")
![Source: 0%](https://img.shields.io/badge/Source-0%25-red.svg "Source: 0%")
![BIPA: 100%](https://img.shields.io/badge/BIPA-100%25-brightgreen.svg "BIPA: 100%")
![CLTS SoundClass: 100%](https://img.shields.io/badge/CLTS%20SoundClass-100%25-brightgreen.svg "CLTS SoundClass: 100%")

- **Varieties:** 1,028
- **Concepts:** 1,500
- **Lexemes:** 662,159
- **Sources:** 0
- **Synonymy:** 1.13
- **Invalid lexemes:** 0
- **Tokens:** 3,861,880
- **Segments:** 1,390 (0 BIPA errors, 0 CLTS sound class errors, 1382 CLTS modified)
- **Inventory size (avg):** 44.04

## Possible Improvements:

- Languages linked to [bookkeeping languoids in Glottolog](http://glottolog.org/glottolog/glottologinformation#bookkeepinglanguoids):
  - Rawngtu Weilong [wela1234](http://glottolog.org/resource/languoid/id/wela1234)
  - Sanapaná (Angaité) [sana1281](http://glottolog.org/resource/languoid/id/sana1281)


- Entries missing sources: 662159/662159 (100.00%)

## CLDF Datasets

The following CLDF datasets are available in [cldf](cldf):

- CLDF [Wordlist](https://github.com/cldf/cldf/tree/master/modules/Wordlist) at [cldf/cldf-metadata.json](cldf/cldf-metadata.json)