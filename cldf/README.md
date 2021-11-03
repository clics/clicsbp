<a name="ds-cldfmetadatajson"> </a>

# Wordlist Language Islands

**CLDF Metadata**: [cldf-metadata.json](./cldf-metadata.json)

property | value
 --- | ---
[dc:conformsTo](http://purl.org/dc/terms/conformsTo) | [CLDF Wordlist](http://cldf.clld.org/v1.0/terms.rdf#Wordlist)
[dc:license](http://purl.org/dc/terms/license) | https://creativecommons.org/licenses/by/4.0/
[dcat:accessURL](http://www.w3.org/ns/dcat#accessURL) | https://github.com/clics/clicsbp
[prov:wasDerivedFrom](http://www.w3.org/ns/prov#wasDerivedFrom) | <ol><li><a href="https://github.com/clics/clicsbp/tree/b279c7b">clics/clicsbp b279c7b</a></li><li><a href="https://github.com/glottolog/glottolog/tree/v4.4">Glottolog v4.4</a></li><li><a href="https://github.com/concepticon/concepticon-data/tree/v2.5.0">Concepticon v2.5.0</a></li><li><a href="https://github.com/cldf-clts/clts//tree/b12a7df">CLTS v2.1.0-26-gb12a7df</a></li><li><a href="https://github.com/lexibank/hantganbangime/tree/v1.0">lexibank/hantganbangime v1.0</a></li><li><a href="https://github.com/lexibank/northeuralex/tree/7767d83">lexibank/northeuralex v4.0-4-g7767d83</a></li><li><a href="https://github.com/lexibank/chenhmongmien/tree/v3.0">lexibank/chenhmongmien v3.0</a></li><li><a href="https://github.com/lexibank/kraftchadic/tree/v4.0.1">lexibank/kraftchadic v4.0.1</a></li><li><a href="https://github.com/lexibank/abrahammonpa/tree/v3.0">lexibank/abrahammonpa v3.0</a></li><li><a href="https://github.com/lexibank/allenbai/tree/v4.0">lexibank/allenbai v4.0</a></li><li><a href="https://github.com/lexibank/bantubvd/tree/v4.0">lexibank/bantubvd v4.0</a></li><li><a href="https://github.com/lexibank/beidasinitic/tree/v5.0.1">lexibank/beidasinitic v5.0.1</a></li><li><a href="https://github.com/lexibank/bowernpny/tree/v4.0.1">lexibank/bowernpny v4.0.1</a></li><li><a href="https://github.com/lexibank/castrosui/tree/v3.0.1">lexibank/castrosui v3.0.1</a></li><li><a href="https://github.com/lexibank/castroyi/tree/v1.0.1">lexibank/castroyi v1.0.1</a></li><li><a href="https://github.com/lexibank/castrozhuang/tree/v1.0.1">lexibank/castrozhuang v1.0.1</a></li><li><a href="https://github.com/lexibank/chindialectsurvey/tree/v1.0">lexibank/chindialectsurvey v1.0</a></li><li><a href="https://github.com/lexibank/gerarditupi/tree/v2.0">lexibank/gerarditupi v2.0</a></li><li><a href="https://github.com/lexibank/hubercolumbian/tree/v4.0.1">lexibank/hubercolumbian v4.0.1</a></li><li><a href="https://github.com/lexibank/johanssonsoundsymbolic/tree/v1.0">lexibank/johanssonsoundsymbolic v1.0</a></li><li><a href="https://github.com/lexibank/marrisonnaga/tree/v3.0">lexibank/marrisonnaga v3.0</a></li><li><a href="https://github.com/lexibank/savelyevturkic/tree/v2.0">lexibank/savelyevturkic v2.0</a></li><li><a href="https://github.com/lexibank/suntb/tree/v4.0">lexibank/suntb v4.0</a></li><li><a href="https://github.com/lexibank/walworthpolynesian/tree/573a291">lexibank/walworthpolynesian v1.0-5-g573a291</a></li><li><a href="https://github.com/lexibank/wold/tree/v4.0">lexibank/wold v4.0</a></li><li><a href="https://github.com/lexibank/yanglalo//tree/v3.0">lexibank/yanglalo/ v3.0</a></li><li><a href="https://github.com/lexibank/yangyi/tree/v1.1">lexibank/yangyi v1.1</a></li></ol>
[prov:wasGeneratedBy](http://www.w3.org/ns/prov#wasGeneratedBy) | <ol><li><strong>lingpy-rcParams</strong>: <a href="./lingpy-rcParams.json">lingpy-rcParams.json</a></li><li><strong>python</strong>: 3.9.6</li><li><strong>python-packages</strong>: <a href="./requirements.txt">requirements.txt</a></li></ol>
[rdf:ID](http://www.w3.org/1999/02/22-rdf-syntax-ns#ID) | clicsbp
[rdf:type](http://www.w3.org/1999/02/22-rdf-syntax-ns#type) | http://www.w3.org/ns/dcat#Distribution


## <a name="table-formscsv"></a>Table [forms.csv](./forms.csv)


Raw lexical data item as it can be pulled out of the original datasets.

This is the basis for creating rows in CLDF representations of the data by
- splitting the lexical item into forms
- cleaning the forms
- potentially tokenizing the form


property | value
 --- | ---
[dc:conformsTo](http://purl.org/dc/terms/conformsTo) | [CLDF FormTable](http://cldf.clld.org/v1.0/terms.rdf#FormTable)
[dc:extent](http://purl.org/dc/terms/extent) | 22018


### Columns

Name/Property | Datatype | Description
 --- | --- | --- 
[ID](http://cldf.clld.org/v1.0/terms.rdf#id) | `string` | Primary key
[Local_ID](http://purl.org/dc/terms/identifier) | `string` | 
[Language_ID](http://cldf.clld.org/v1.0/terms.rdf#languageReference) | `string` | References [languages.csv::ID](#table-languagescsv)
[Parameter_ID](http://cldf.clld.org/v1.0/terms.rdf#parameterReference) | `string` | References [parameters.csv::ID](#table-parameterscsv)
[Value](http://cldf.clld.org/v1.0/terms.rdf#value) | `string` | 
[Form](http://cldf.clld.org/v1.0/terms.rdf#form) | `string` | 
[Segments](http://cldf.clld.org/v1.0/terms.rdf#segments) | list of `string` (separated by ` `) | 
[Comment](http://cldf.clld.org/v1.0/terms.rdf#comment) | `string` | 
[Source](http://cldf.clld.org/v1.0/terms.rdf#source) | list of `string` (separated by `;`) | 
`Cognacy` | `string` | 
`Loan` | `boolean` | 
`Graphemes` | `string` | 
`Profile` | `string` | 

## <a name="table-languagescsv"></a>Table [languages.csv](./languages.csv)

property | value
 --- | ---
[dc:conformsTo](http://purl.org/dc/terms/conformsTo) | [CLDF LanguageTable](http://cldf.clld.org/v1.0/terms.rdf#LanguageTable)
[dc:extent](http://purl.org/dc/terms/extent) | 454


### Columns

Name/Property | Datatype | Description
 --- | --- | --- 
[ID](http://cldf.clld.org/v1.0/terms.rdf#id) | `string` | Primary key
[Name](http://cldf.clld.org/v1.0/terms.rdf#name) | `string` | 
[Glottocode](http://cldf.clld.org/v1.0/terms.rdf#glottocode) | `string` | 
`Glottolog_Name` | `string` | 
[ISO639P3code](http://cldf.clld.org/v1.0/terms.rdf#iso639P3code) | `string` | 
[Macroarea](http://cldf.clld.org/v1.0/terms.rdf#macroarea) | `string` | 
[Latitude](http://cldf.clld.org/v1.0/terms.rdf#latitude) | `decimal` | 
[Longitude](http://cldf.clld.org/v1.0/terms.rdf#longitude) | `decimal` | 
`Family` | `string` | 

## <a name="table-parameterscsv"></a>Table [parameters.csv](./parameters.csv)

property | value
 --- | ---
[dc:conformsTo](http://purl.org/dc/terms/conformsTo) | [CLDF ParameterTable](http://cldf.clld.org/v1.0/terms.rdf#ParameterTable)
[dc:extent](http://purl.org/dc/terms/extent) | 120


### Columns

Name/Property | Datatype | Description
 --- | --- | --- 
[ID](http://cldf.clld.org/v1.0/terms.rdf#id) | `string` | Primary key
[Name](http://cldf.clld.org/v1.0/terms.rdf#name) | `string` | 
[Concepticon_ID](http://cldf.clld.org/v1.0/terms.rdf#concepticonReference) | `string` | 
`Concepticon_Gloss` | `string` | 
`Tag` | `string` | 

