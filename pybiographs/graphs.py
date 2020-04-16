import os
import re
from typing import Union
import warnings

import networkx
import numpy as np

from pybiographs.download_data import download_interactions_graph
from pybiographs.mappings import Mappings
from pybiographs.resources import interaction_files, ontology_files

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
        self._maps = Mappings()
        self.graph = self._load_graph()

    def __getattr__(self, item):
        return getattr(self.graph, item)

    @property
    def maps(self):
        return self._maps

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

    def recurrent_ontology_query(self, sub_search, nodes):
        """
        test recursively queries in request for ontology and return result as list

        Args:
            sub_search: the list request.
            nodes: nodes to be searched.

        Returns:
            a list containing proteins satisfying results.

        """
        res = []
        if len(sub_search) > 1:
            assert (
                sub_search[0] == "and" or sub_search[0] == "or" or sub_search[0] == "not"
            ), "wrong operator in query: and/or/not"
            for i in range(1, len(sub_search)):
                if isinstance(sub_search[i], list):
                    sub_res = self.recurrent_ontology_query(sub_search[i], nodes)
                elif isinstance(sub_search[i], str):
                    sub_res = []
                    if sub_search[i] in self.maps.biological_processes_union.keys():
                        sub_res = list(self.maps.biological_processes_union[sub_search[i]])
                    if sub_search[i] in self.maps.molecular_functions_union.keys():
                        sub_res = list(self.maps.molecular_functions_union[sub_search[i]])
                    if sub_search[i] in self.maps.cell_components_union.keys():
                        sub_res = list(self.maps.cell_components_union[sub_search[i]])
                    sub_res = list(set(nodes).intersection(set(sub_res)))
                if i == 1:
                    if sub_search[0] == "not":
                        res = list(set(nodes).difference(set(sub_res)))
                    else:
                        res = list(set(sub_res))
                if sub_search[0] == "and":
                    res = list(set(res).intersection(set(sub_res)))
                elif sub_search[0] == "or":
                    res = list(set(res).union(set(sub_res)))
                elif sub_search[0] == "not":
                    res = list(set(res).difference(set(sub_res)))
            return res
        else:
            assert isinstance(sub_search[0], str), "something wrong with request"
            sub_res = []
            if sub_search[0] in self.maps.biological_processes_union.keys():
                sub_res = list(self.maps.biological_processes_union[sub_search[0]])
            if sub_search[0] in self.maps.molecular_functions_union.keys():
                sub_res = list(self.maps.molecular_functions_union[sub_search[0]])
            if sub_search[0] in self.maps.cell_components_union.keys():
                sub_res = list(self.maps.cell_components_union[sub_search[0]])
            sub_res = list(set(nodes).intersection(set(sub_res)))
            return list(set(sub_res))

    def restrict_by_tissue_threshold(self, nodes, tissue, threshold):
        """
        Remove all nodes from entry nodes that does'nt have an expression superior to a threshold

        Args:
            nodes: list of nodes.
            tissue: a string key for tissue.
            threshold: float between 0 and 1.

        Returns:
            new list containing nodes that satisfy threshold properties.

        """
        new_nodes = []
        for node in nodes:
            if (
                node in self.nodes()
                and self.nodes[node]["expression_data"][self.maps.tissue_num_mapping[tissue]]
                > threshold
            ):
                new_nodes.append(node)
        return list(set(new_nodes))

    def remove_edges_by_threshold(self, graph, score_threshold=0.0):
        """
        Remove from graph all edges that have a score inferior to threshold.
        Considering removing edges can do new orphan nodes (with no edges),
        those node are removed also from graph.

        Args:
            graph: graph to clean edges.
            score_threshold: attribute score threshold, should be between 0 and 1.
            as edge scores are.

        Returns:
            cleaned graph.

        """
        to_remove = []
        for x, y, z in graph.edges(data=True):
            if z["score"] <= score_threshold:
                to_remove.append((x, y))
        graph.remove_edges_from(to_remove)
        to_remove = []
        for node in graph.nodes():
            if graph.degree(node) == 0:
                to_remove.append(node)
        graph.remove_nodes_from(to_remove)
        return graph

    def info_sequence_regex(self, res, reg, attribute):
        """
        Depending on node attribute "info" or "sequence", search regex in all node
        attributes and return an union between query node results and nodes that
        have a match.

        Args:
            res: entry node list corresponding to query result so far.
            reg: regex to be search as a string.
            attribute: "info" or "sequence".

        Returns:
            union list of matching nodes and res.

        """
        sub_res = []
        for x, y in self.nodes(data=True):
            r = re.search(reg, y[attribute])
            if r:
                sub_res.append(x)
        return list(set(res).union(set(sub_res)))

    def pathway_regex(self, res, reg):
        """
        Search a regex in "pathways" attribute of nodes in graph and return union of arg res
        with matching nodes.

        Args:
            res: entry node list corresponding to query results so far.
            reg: regex to be search as a string.

        Returns:
            union list of matching nodes and res.

        """
        sub_res = []
        for x, y in self.nodes(data=True):
            p_string = ""
            for pathway in y["pathways"]:
                p_string += pathway + " "
            r = re.search(reg, p_string)
            if r:
                sub_res.append(x)
        return list(set(res).union(set(sub_res)))

    def ontology_regex(self, res, reg):
        """
        Search a regex in all ontological attributes of nodes in graph ("cellular_components",
        "biological_processes", "cellular_components") and return an union of matching results
        with query results so far.

        Args:
            res: entry node list corresponding to query results so far.
            reg: regex to be search as a string.

        Returns:
            union list of matching nodes and res.

        """
        sub_res = []
        nodes = list(self.nodes())
        for ontology in self.maps.biological_processes_union.keys():
            r = re.search(reg, self.maps.go_to_name[ontology])
            if r:
                sub_res.extend(
                    list(
                        set(nodes).intersection(
                            set(self.maps.biological_processes_union[ontology])
                        )
                    )
                )
        for ontology in self.maps.cell_components_union.keys():
            r = re.search(reg, self.maps.go_to_name[ontology])
            if r:
                sub_res.extend(
                    list(set(nodes).intersection(set(self.maps.cell_components_union[ontology])))
                )
        for ontology in self.maps.molecular_functions_union.keys():
            r = re.search(reg, self.maps.go_to_name[ontology])
            if r:
                sub_res.extend(
                    list(
                        set(nodes).intersection(set(self.maps.molecular_functions_union[ontology]))
                    )
                )
        return list(set(res).union(set(sub_res)))

    def metabolites_regex(self, res, reg):
        """
        Search a regex in metabolites names in graph node attributes and return an union
        of matching results with query results so far.

        Args:
            res: entry node list corresponding to query results so far.
            reg: regex to be search as a string.

        Returns:
            union list of matching nodes and res.

        """
        sub_res = []
        for x, y in self.nodes(data=True):
            p_string = ""
            for metabolite in y["metabolites"]:
                p_string += self.maps.metabolites_id_to_name[metabolite] + " "
            r = re.search(reg, p_string)
            if r:
                sub_res.append(x)
        return list(set(res).union(set(sub_res)))

    def sub_graph_by_node_regex_search(
        self, regex, spec="i_p_m_o", tissue=None, score_threshold=0.0, expression_threshold=0.0
    ):
        """
        This is the public method that need to be used to query for a subgraph of
        the graph by searching a regex in the node attribute.
        Step 1 : search nodes with matching regex in attributes.
        Step 2 : removes nodes that are inferior to expression threshold.
        Step 3 : create subragph from parent graph and removes edges inferior to score threshold.

        Args:
            regex: regex to be searched in node attributes.
            spec: a string to specify where to search for, a combination of "i" (for info),
            "p" (for pathways), "m" (for metabolites), "o" (for ontologies), separated by
            underscore "_". As a split is applied, the order is not important.
            tissue: restrict the search by tissue (exemple "lung"). Default None and ignored.
            score_threshold: threshold to apply to edges in subgraph, between 0 and 1 as
            the scores.
            expression_threshold: threshold to apply to expression score in tissue.
            Ignored if tissue is None.

        Returns:
            New sub graph.

        """
        spec = spec.split("_")
        node_results = []
        if "i" in spec:
            node_results = self.info_sequence_regex(node_results, regex, "info")
        if "p" in spec:
            node_results = self.pathway_regex(node_results, regex)
        if "m" in spec:
            node_results = self.metabolites_regex(node_results, regex)
        if "o" in spec:
            node_results = self.ontology_regex(node_results, regex)

        if tissue:
            node_results = self.restrict_by_tissue_threshold(
                node_results, tissue, expression_threshold
            )

        new_graph = self.subgraph(node_results).copy()

        return self.remove_edges_by_threshold(new_graph, score_threshold)

    def sub_graph_by_node_ontology_search(
        self, ontology_query=None, tissue=None, score_threshold=0.0, expression_threshold=0.0
    ):
        """
        This is the public method that need to be used to query for a subgraph by searching for
        a set expression query in ontology. As for method above, returns a sub graph cleaned by
        threshold.
        ontology query language:
        simple query: "goid" -> returns subgraph with nodes in goid
        basic query : ["and", "goid1", "goid2", ...] -> returns subgraph with nodes in goid1
        and goid2 and ...
        basic query : ["not", "goid1", ...] -> returns subgraph with nodes not in goid1, ...
        basic query : ["or", "goid1", "goid2"] -> returns subgraph with nodes in goid1 or goid2
        or ...
        complex query : ["and", ["or", "g1", "g2", ["and", "g3", "g4"]], ["not", "g5"], "g6"] :
        -> return subgraph with nodes satisfying  (g1 or g2 or (g3 and g4)) and (not g5) and g6
        Args:
            ontology_query: the query list
            tissue: restrict the search by tissue (exemple "lung"). Default None and ignored.
            score_threshold: threshold to apply to edges in subgraph, between 0 and 1 as the scores
            expression_threshold: threshold to apply to expression score in tissue.
            Ignored if tissue is None.

        Returns:
            New sub graph.

        """

        node_results = []
        if ontology_query:
            node_results = self.recurrent_ontology_query(ontology_query, list(self.nodes()))
        if tissue:
            node_results = self.restrict_by_tissue_threshold(
                node_results, tissue, expression_threshold
            )
        new_graph = self.subgraph(node_results).copy()
        return self.remove_edges_by_threshold(new_graph, score_threshold)

    def get_nodes_by_sequence_regex(self, sequence_regex):
        """
        Search a regex in amino acid sequences stored in nodes and returns matching node results.
        Args:
            sequence_regex: regex to search in sequences

        Returns:
            a list of nodes (uniprot ids).

        """
        node_results = []
        node_results = self.info_sequence_regex(node_results, sequence_regex, "info")
        return list(set(node_results))

    def propagate_node(self, node, diameter):
        """
        Recursive part of sub_graph_from_node_propagation
        Args:
            node: node to propagate
            diameter: diameter that still need to be propagated

        Returns:
            node results.

        """

        if node not in self.nodes():
            return []

        node_results = [node]
        if diameter == 0:
            return node_results
        else:
            if self.is_directed:
                # adjacents = list(set(self.successors(node)).union(self.predecessors(node)))
                adjacents = list(set(self.successors(node)))
            else:
                adjacents = list(set(self.neighbors(node)))
            for adj in adjacents:
                node_results.extend(self.propagate_node(adj, diameter - 1))
            return node_results

    def sub_graph_from_node_propagation(
        self, nodes, diameter=1, tissue=None, score_threshold=0.0, expression_threshold=0.0
    ):
        """
        Takes nodes and returns sub graph generated by neighbor propagation up to a diameter.
        Will start recursively to take all neighbors of entry nodes, then neighbors of neighbors,
        etc...The method will return subgraph thresholded eventually by tissue and scores on edges.

        Args:
            nodes: nodes to propagate
            diameter: diameter of the resulting sub graph around the node.
            tissue: restrict the search by tissue (exemple "lung"). Default None and ignored.
            score_threshold: threshold to apply to edges in subgraph, between 0 and 1 as the scores
            expression_threshold: threshold to apply to expression score in tissue.
            Ignored if tissue is None.

        Returns:
            New graph with results.

        """

        node_res = []
        for node in nodes:
            node_res.extend(self.propagate_node(node, diameter))

        if tissue:
            node_res = self.restrict_by_tissue_threshold(node_res, tissue, expression_threshold)

        new_graph = self.subgraph(node_res).copy()

        return self.remove_edges_by_threshold(new_graph, score_threshold)

    def print_sub_graph_nodes(self, graph, print_spec="i_o_p_m", limit=30):
        """
        Print nodes in graph up to a limit with specs similar to sub_graph_by_node_regex_search.

        Args:
            graph: graph where to print nodes
            print_spec: a string to specify what to print, a combination of "i" (for info),
            "p" (for pathways), "m" (for metabolites), "o" (for ontologies),
            separated by underscore "_". As a split is applied, the order is not important.
            limit: limit to the number of prints.

        Returns:
            None.

        """
        print_spec = print_spec.split("_")
        cpt = 0
        for x, y in graph.nodes(data=True):
            if cpt == limit:
                break
            print(x, " : ", y["node_type"])
            if "i" in print_spec:
                print("info :", y["info"])
            if "o" in print_spec:
                print("cellular components : ")
                for cc in y["cellular_components"]:
                    print("\t" + self.maps.go_to_name[cc])
                print("molecular functions :")
                for cc in y["molecular_functions"]:
                    print("\t" + self.maps.go_to_name[cc])
                print("biological processes :")
                for cc in y["biological_processes"]:
                    print("\t" + self.maps.go_to_name[cc])
            if "m" in print_spec:
                print("associated metabolites :")
                for metabolite in y["metabolites"]:
                    print("\t" + self.maps.metabolites_id_to_name[metabolite])
            if "p" in print_spec:
                print("associated pathways :")
                for pathway in y["pathways"]:
                    print("\t" + pathway)
            print("\n")
            cpt += 1

    def classify_tissue_by_node_expression(self, nodes, limit=30):
        """
        Takes a list of nodes, then print tissues where the set of nodes is the most expressed.

        Args:
            nodes: nodes to be searched for.
            limit: limit to print.

        Returns:
            None.

        """
        t_n = self.maps.tissue_num_mapping
        n_t = {t_n[t]: t for t in t_n.keys()}
        expr_data = []
        for node in nodes:
            if node in self.nodes():
                expr_data.append(self.nodes[node]["expression_data"])
        expr_data = np.array(expr_data)
        # expr_data += 1e-14
        # expr_data = -1.0 * expr_data * np.log(expr_data)
        expr_data = expr_data.mean(axis=0)

        cpt = 0
        for ix in np.argsort(-expr_data):
            if cpt == limit:
                break
            if expr_data[ix] > 0.0:
                print(n_t[ix], " : ", expr_data[ix])
            cpt += 1

    def most_present_biological_processes(self, graph, tissue, bp_size_thresh=0, limit=10):
        """
        After sub_graph_from_node_propagation, this function can be used to
        print most affected biological processes.

        Args:
            graph: sub graph to print most affected components.
            tissue: string, the tissue where to analyze the biological processes.
            bp_size_thresh : a threshold on size on number proteins in biological processes
            limit: limit to print.

        Returns:
            None.

        """
        nodes = set(graph.nodes())
        ontologies = []
        res_vector = []
        for ontology in self.maps.biological_processes_union.keys():
            ontology_prots = set(self.maps.biological_processes_union[ontology])
            if len(ontology_prots) > bp_size_thresh:
                common = nodes.intersection(ontology_prots)
                res = 0.0
                for prot in common:
                    res += graph.nodes[prot]["expression_data"][
                        self.maps.tissue_num_mapping[tissue]
                    ]
                ontologies.append(self.maps.go_to_name[ontology])
                res_vector.append(float(res / len(ontology_prots)))
        res_vector = np.array(res_vector)
        cpt = 0
        print("Most affected biological processes :")
        for ix in np.argsort(-res_vector):
            if cpt == limit:
                break
            print("\t", ontologies[ix])
            cpt += 1

    def most_present_cellular_components(self, graph, tissue, cc_size_thresh=0, limit=10):
        """
        Similar to most_affected_biological_processes; but for cellular components.

        Args:
            graph: sub graph to print most affected cellular components.
            tissue: string, the tissue where to analyze the biological processes.
            cc_size_thresh : a threshold on size on number proteins in molecular function.
            limit: limit to print.

        Returns:
            None.

        """
        nodes = set(graph.nodes())
        ontologies = []
        res_vector = []
        for ontology in self.maps.cell_components_union.keys():
            ontology_prots = set(self.maps.cell_components_union[ontology])
            if len(ontology_prots) > cc_size_thresh:
                common = nodes.intersection(ontology_prots)
                res = 0.0
                for prot in common:
                    res += graph.nodes[prot]["expression_data"][
                        self.maps.tissue_num_mapping[tissue]
                    ]
                ontologies.append(self.maps.go_to_name[ontology])
                res_vector.append(float(res / len(ontology_prots)))
        res_vector = np.array(res_vector)
        cpt = 0
        print("Most affected cellular_components :")
        for ix in np.argsort(-res_vector):
            if cpt == limit:
                break
            print("\t", ontologies[ix])
            cpt += 1


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
