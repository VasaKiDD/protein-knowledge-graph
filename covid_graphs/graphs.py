import os
from typing import Union
import warnings

import networkx

from covid_graphs.download_data import download_interactions_graph
from covid_graphs.resources import interaction_files, ontology_files


ontologies = {"biological_processes", "cell_components", "molecular_functions"}

ontology_aliases = {
    "biological_processes": "bp",
    "cell_components": "cc",
    "molecular_functions": "mf",
}

aliases_to_ontology = {v: k for k, v in ontology_aliases.values()}


# TODO(Vasakidd): Make sure all the relevant info is included in the documentation.
class InteractionGraph:
    """
    Represents a graph of protein-protein interactions.

    It can load a directed or undirected graph, and wraps the corresponding networkx
    graph. If it represents a directed graph it behaves as a :class:`networkx.Digraph`.
    Otherwise it behaves as a :class:`networkx.Graph`.

    Node attributes:
       * label : uniprot_id from uniprot (https://www.uniprot.org/)
       * string node_type : metabolome_graph (with pathway and metabolites associated)
                            or other_protein (not referenced as metabolome proteins:
                            no metabolites and no pathway on smpd : https://smpdb.ca/)
       * string info : Text explaining the products of the mRNA that codes
                       the protein from STRING database : https://string-db.org/).
       * list cellular_components : list of Go Id cellular components the protein
                                    is belonging to in QuickGO (see gene ontology :
                                    https://www.ebi.ac.uk/QuickGO/).
                                    :class:`Mappings```.go_to_name`` maps GoId to names.
       * list molecular_functions : list of Go Id as above but for molecular functions.
       * list biological_processes : list of Go Id as above but for biological processes.
       * list expression_data : Vector of float of size 308 corresponding to expression
                                ranks of intial RNAm coding the protein renormalized
                                from 0 to 1 in 308 tissues (see https://bgee.org/).
                                index_tissue is a dict mapping index in vector to
                                string tissue name.
       * list metabolites : list of HMDB ID metabolites associated to protein if
                            it is a metabolome_protein (see https://hmdb.ca/).
                            :class:`Mappings```.metabolite_id_to_name`` contains the
                             mapping from id to metabolite name.
       * list pathways : list of pathway of names the belonging to the metabolome_protein.
                         for more information on a pathway, search it on smpd
                         (might not be referenced).
       * string sequence : Amino acid sequence for the protein.

    Directed edge attributes:

    Undirected edge attributes:

    """

    def __init__(self, directed: bool = False):
        """
        Initialize a :class:`InteractionGraph`.

        Args:
            directed: If ``True`` the instance will represent a directed graph of
                     interactions. If ``False`` the instance will represent an
                     undirected graph of interactions.

        """
        self._is_directed = directed
        self.graph = self._load_graph()

    def __getattr__(self, item):
        return getattr(self.graph, item)

    @property
    def is_directed(self) -> bool:
        """Return ``True`` if it represents a directed graph. Otherwise return ``False``."""
        return self._is_directed

    def _load_graph(self) -> Union[networkx.Graph, networkx.DiGraph]:
        graph_path = (
            interaction_files.directed if self.is_directed else interaction_files.undirected
        )
        if not os.path.exists(graph_path) or not os.path.isfile(graph_path):
            warnings.warn("Graph file is not present. Downloading graph file")
            download_interactions_graph(directed=self.is_directed)
        graph = networkx.read_gpickle(graph_path)
        return graph


class OntologyGraph:
    def __init__(self, name: str):
        if name not in ontologies and name not in aliases_to_ontology:
            raise ValueError("name needs to be one of %s. Got %s instead" % (ontologies, name))
        self._name = name if name in ontologies else aliases_to_ontology[name]
        self.graph = self._load_graph()

    def __getattr__(self, item):
        return getattr(self.graph, item)

    @property
    def name(self) -> str:
        return self._name

    def _load_graph(self) -> networkx.Graph:
        graph_file = getattr(ontology_files, self.name)
        return networkx.read_gpickle(graph_file)
