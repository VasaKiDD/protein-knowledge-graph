from collections import namedtuple
import os
import warnings

import pkg_resources

from pybiographs import __name__ as package_name


def get_data_folder() -> str:
    # "../data" means that the package is downloaded from github + pip install -e .
    extension = "data" if pkg_resources.resource_exists(package_name, "data") else "../data"
    pck_path = pkg_resources.resource_filename(package_name, "")
    data_folder = os.path.join(pck_path, extension)
    if not os.path.exists(data_folder):
        warnings.warn("Cannot find package data resources. Creating resource folder")
        os.makedirs(data_folder, exist_ok=True)
    return data_folder


def get_interactions_path():
    data_folder = get_data_folder()
    graphs_folder = os.path.join(data_folder, "graphs")
    os.makedirs(graphs_folder, exist_ok=True)
    interactions_folder = os.path.join(graphs_folder, "interactions")
    os.makedirs(interactions_folder, exist_ok=True)
    return interactions_folder


data_path = get_data_folder()


OntologyFiles = namedtuple(
    "OntologyFiles", "biological_processes cell_components molecular_functions"
)
ontology_path = os.path.join(data_path, "graphs", "ontology")
ontology_files = OntologyFiles(
    biological_processes=os.path.join(ontology_path, "biological_processes.gpickle"),
    cell_components=os.path.join(ontology_path, "cell_components.gpickle"),
    molecular_functions=os.path.join(ontology_path, "molecular_functions.gpickle"),
)

InteractionFileNames = namedtuple("InteractionFilenames", "directed undirected")
interaction_file_names = InteractionFileNames(
    directed="pp_interactions_directed.gpickle", undirected="pp_interactions_undirected.gpickle"
)
InteractionFiles = namedtuple("InteractionFiles", "directed undirected")
interaction_files = InteractionFiles(
    directed=os.path.join(get_interactions_path(), interaction_file_names.directed),
    undirected=os.path.join(get_interactions_path(), interaction_file_names.undirected),
)

covid_path = os.path.join(data_path, "covid")
CovidFiles = namedtuple("CovidFiles", "csv data interacting_nodes")
covid_files = CovidFiles(
    csv=os.path.join(covid_path, "covid19.csv"),
    data=os.path.join(covid_path, "covid_data.pck"),
    interacting_nodes=os.path.join(covid_path, "interacting_nodes.pck"),
)

mappings_path = os.path.join(data_path, "mappings")
MappingFiles = namedtuple(
    "MappingFiles",
    (
        "biological_processes_union "
        "cell_components_union "
        "covid_go_to_name "
        "metabolites_id_to_name "
        "molecular_functions_union "
        "gene_to_proteins "
        "go_to_name "
        "tissue_num_mapping"
    ),
)
mapping_files = MappingFiles(
    biological_processes_union=os.path.join(mappings_path, "biological_processes_union_dict.pck"),
    cell_components_union=os.path.join(mappings_path, "cell_components_union_dict.pck"),
    covid_go_to_name=os.path.join(mappings_path, "covid_go_to_name.pck"),
    metabolites_id_to_name=os.path.join(mappings_path, "metabolites_id_to_name.pck"),
    molecular_functions_union=os.path.join(mappings_path, "molecular_functions_union_dict.pck"),
    gene_to_proteins=os.path.join(mappings_path, "string_gene_to_proteins.pck"),
    go_to_name=os.path.join(mappings_path, "string_go_to_name.pck"),
    tissue_num_mapping=os.path.join(mappings_path, "tissue_num_mapping.pck"),
)
