# covid19-knowledge-ml-python
[![Travis build status](https://travis-ci.com/Synergetic-ai/Bio-knowledge-graph-python.svg)](https://travis-ci.com/Synergetic-ai/Bio-knowledge-graph-python)
[![Documentation Status](https://readthedocs.org/projects/bio-knowledge-graph-python/badge/?version=latest)](https://bio-knowledge-graph-python.readthedocs.io/en/latest/?badge=latest)
[![Code coverage](https://codecov.io/github/Synergetic-ai/Bio-knowledge-graph-python/coverage.svg)](https://codecov.io/github/Synergetic-ai/Bio-knowledge-graph-python)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)


This repository provides a human protein-protein interaction graph in the form of the networkX graph and additional data about the COVID-19 virus to study virus-human interactions at the protein level. It is intended for Data Scientist and Machine Learning researchers who want to contribute with AI Research to medical discoveries during the pandemic. 

The protein-protein interaction graph not only stores interaction but also several informations about the type of interaction and protein involved (see nodes in graph).

We gathered data from several sources:

* Uniprot protein database : https://www.uniprot.org/
* Gene ontology database QuickGO : https://www.ebi.ac.uk/QuickGO/
* Geene expression database Bgee : https://bgee.org/
* Human metabolome database HMDB : https://hmdb.ca/
* Protein-protein intaraction database STRING : https://string-db.org/
* Small molecule pathway database SMPD : https://smpdb.ca/
* Covid-data:
  * https://covid-19.uniprot.org/uniprotkb?query=*
  * https://www.ebi.ac.uk/ena/pathogens/covid-19

## Installation

```python
pip install pybiographs
```

## Usage

```python
import subprocess
subprocess.Popen(["python3","-m","http.server"])
from pybiographs import InteractionGraph, OntologyGraph, Mappings, CovidData
directed_graph = InteractionGraph(directed=True)
undirected_graph = InteractionGraph(directed=False)
bp_ontology = OntologyGraph('biological_processes')
mf_ontology = OntologyGraph('molecular_functions')
cc_ontology = OntologyGraph('cell_components')
maps = Mappings()
print(directed_graph.maps.names)
covid_data = CovidData()
```

## Documentation

https://bio-knowledge-graph-python.readthedocs.io/en/latest/?badge=latest

## Infos abouts protein-protein interaction graphs

InteractionGraph(directed=False) returns a networkX nx.Graph() wrapped with other methods to study graph (see docs/files)
InteractionGraph(directed=True) returns a netorkx nx.MultiDiGraph() wrapped with other methods to study graph (see docs/file)

See https://networkx.github.io/documentation/stable/reference/classes/index.html for more info about the class

#### Node attributes

* string label : uniprot_id from uniprot (https://www.uniprot.org/)
* string node_type : metabolome_graph (with pathway and metabolites associated) or other_protein (not referenced as metabolome proteins : no metabolites and no pathway on smpd : https://smpdb.ca/)
* string info : small text explaining the products of the mRNA that codes the protein from STRING database : https://string-db.org/)
* list cellular_components : list of Go Id cellular components the protein is belonging to in QuickGO (see gene ontology : https://www.ebi.ac.uk/QuickGO/). The dict go_to_name maps GoId to names.
* list molecular_dunctions : list of Go Id as above but for molecular functions.
* list biological_processes : list of Go Id as above but for biological processes.
* list expression_data : vector of float of size 308 corresponding to expression ranks of intial RNAm coding the protein renormalized from 0 to 1 in 308 tissues (see https://bgee.org/). index_tissue is a dict mapping index in vector to string tissue name.
* list metabolites : list of HMDB ID metabolites associated to protein if it is a metabolome_protein (see https://hmdb.ca/). metabolite_id_to_name is a dict mapping id to metabolite name.
* list pathways : list of pathway names the metabolome_protein is belonging to. for more information on a pathway, search it on smpd (might not be referenced).
* string sequence : amino acid sequence for the protein

#### Edge attributes for undirected graph

* float score : a score between 0 and 1 representing the strength of the interaction(see https://string-db.org/)

#### Edge attributes for directed graph

* string link : type of edge between 2 proteins with possible values :
  * binding_activation : directed binding activation
  * binding_inhibition : directed binding inhibition
  * binding : directed binding without further information
  * activation : directed protein activation
  * inhibition : directed protein inhibition
  * reaction : the product of first protein is involved in reactants or products of target protein
  * catalysis : first protein product catalysis target protein's reaction/function
  * ptmod : first protein modifies second protein post-translationally
  * expression : first protein increases expression of target protein (exemple : transcription factor)
  * expression_inhibition : first protein inhibates target protein (exemple : transcription factor)
* float score : a score between 0 and 1 from String database representing the confidence/strength of connexion

## Info about ontology graphs (or trees)

OntologyGraph('cell_components') : returns a wrapped networkX directed nx.DiGraph() of cellular component ontology from QuickGo linked by "is_a" relation.
OntologyGraph('molecular_functions') : returns a wrapped networkX directed nx.DiGraph() of molecular function ontology from QuickGo linked by "is_a" relation.
OntologyGraph('biological_processes') : returns a wrapped networkX directed nx.DiGraph() of biological process ontology from QuickGo linked by "is_a" relation.

#### Node attributes

* string node_type : string node type with values:
  * metabolome_protein : protein involved in metabolic processes
  * other_protein : other protein not involved or not referenced in metabolic processes
  * cellular_component : Go Id from QuickGo of cellular component (for cc_ontology graph)
  * biological_process : Go Id from QuickGo of biological process (for bp_ontology graph)
  * molecular_function : Go Id from QuickGo of molecular function (for mf_ontology graph)
  
#### Edge attributes

* string link : type of edge in ontology :
  * is_a : is a ontology (child category is_a parent category)
  * part_of : part of ontology (protein part of category)
  
## Covid19 data

* covid_data.dict : dict containing data about proteins involved in covid-19 from https://covid-19.uniprot.org/uniprotkb?query=*:
  * key human : homo sapiens protein or not
  * key sequance : amino acid sequence of the protein
  * key molecular_functions : same as for nodes of protein-protein interaction graph
  * key cellular_components : same as for nodes of protein-protein interaction graph
  * key biological_processes : same as for nodes of protein-protein interaction graph
  * key info : info from publications about the protein
* Mappings.covid_go_to_name : dict mapping go_id from covi-19 to names
* data/covid/covid_interacting_nodes.pck : a list of nodes (proteins) that the proteins from covid-19 is interacting with. The purpose of this list is to use it as a test set for edge regression/classification machine learning models. The proteins has been extracted from https://www.biorxiv.org/content/10.1101/2020.03.22.002386v1
  
## Supplementary data

* dict Mappings.gene_to_proteins : mapping of genes to proteins products
* dict Mappings.cell_components_union : mapping cellular_component GoId to all proteins included in the category
* dict Mappings.molecular_functions_union : mapping molecular function GoId to all proteins included in the category
* dict Mappings.biological_processes_union : mapping biological processes GoId to all proteins included in the category
* dict Mappings.go_to_name : Go Id to name to the category
* dict Mappings.metabolite_id_to_name : HMDB ID to name of metabolite
* dict Mappings.tissue_num_mapping : tissue name to index in expression vector

## Bonus : create a pytorch Dataset from graphs

The class PPInteraction_dataset in utils extracts edges from a protein-protein interaction graph and returns a torch DataSet. The constructor takes as argument:

* nx graph : the directed or undirected graph to create the data from
* bool directed : True if directed else False
* float score_threshold: a value between 0 an 1 representing score attribute in edges. the constructor will extract edges that have a score superior to this threshold.
* string node_attribute : the type of node attribute to extract from graph (ex "sequence", "cellular_components", "info"...)
* bool regression : True if regression task (keep scores) or False in classification (existing edge will be 1.0)
float no_interactions_ratio : a value between 0 and 1. The constructor will create edges with proteins that are not in the graph and label them with 0.0

The method getitem(ix) will return :
* (node_attribute_protein_a, node_attribute_protein_b, link_type, label) if directed, with label between 0 and 1 if edge regression task else 0 or 1)
* (node_attribute_protein_a, node_attribute_protein_b, label) if undirected, with label between 0 and 1 if edge regression task else 0 or 1)

Note: to create the classification dataset, the constructor creates labels with 0.0 by selecting edges that are not in the graph. For creating a balanced classification dataset, you should put a ratio of 1.0 to create as much 0.0 labels as 1.0 labels. You can play with the score_threshold to restrict the size of existing edges.

Example :

```python
from pybiographs.dl_models.torch_datasets import PPInteractionDataset
edge_dataset = PPInteractionDataset(InteractionGraph(directed=False), score_threshold = 0.9, node_attribute = "sequence", regression = False, no_interactions_ratio = 1.0)
```

