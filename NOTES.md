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


# Create CLICS4 Dataset

To create the CLDF dataset with the colexifications aggregated from the Lexibank word lists, use:

```
$ cldfbench lexibank.makecldf lexibank_clicsbp.py --concepticon-version=v3.1.0 --clts-version=v2.2.0 --glottolog-version=v4.7
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
$ cldfbench clicspb.piecharts --weight=Language_Count_Weighted
```
