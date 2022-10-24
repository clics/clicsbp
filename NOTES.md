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

```
cldfbench clicsbp.colexifications
cldfbench clicsbp.colexify_all_data
```

## 5 Compute Statistics

### 5.1 Compute Pie-Charts

```
cldfbench clicspb.piecharts
```

### 5.2 Compute ARI

### 5.3 Plot Networks

```
cldfbench clicsbp.plotgraphs
```
