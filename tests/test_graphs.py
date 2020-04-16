import networkx
import pytest

from pybiographs import InteractionGraph, OntologyGraph, ontologies, ontology_aliases


@pytest.fixture(scope="class", params=(True, False))
def interaction_graph(request):
    return InteractionGraph(directed=request.param)


class TestInteractionGraph:
    def test_load_data(self, interaction_graph: InteractionGraph):
        if interaction_graph.is_directed:
            assert isinstance(interaction_graph.graph, networkx.DiGraph)
        else:
            assert isinstance(interaction_graph.graph, networkx.Graph)

        interaction_graph.sub_graph_by_node_regex_search(
            regex="serotonin.*signaling|signaling.*serotonin",
            tissue="brain",
            score_threshold=0.0,
            expression_threshold=0.0,
        )
        interaction_graph.get_nodes_by_sequence_regex(sequence_regex="AG")
        interaction_graph.sub_graph_by_node_ontology_search(
            ontology_query=["or", ["and", "GO:0006836", "GO:0097060"], "GO:0043083"]
        )
        sub_graph = interaction_graph.sub_graph_from_node_propagation(
            nodes=["Q9BYF1"],
            diameter=1,
            tissue="lung",
            score_threshold=0.9,
            expression_threshold=0.0,
        )
        interaction_graph.print_sub_graph_nodes(sub_graph, print_spec="i_o_p_m", limit=10)
        interaction_graph.classify_tissue_by_node_expression(["Q9BYF1"])
        interaction_graph.most_present_biological_processes(
            sub_graph, bp_size_thresh=500, tissue="lung", limit=20
        )
        interaction_graph.most_present_cellular_components(
            sub_graph, cc_size_thresh=500, tissue="lung", limit=20
        )
        interaction_graph.most_present_cellular_components(sub_graph, "lung", limit=20)


class TestOntologyGraph:
    @pytest.mark.parametrize("name", tuple(ontologies))
    def test_init_no_aliases(self, name):
        graph = OntologyGraph(name=name)
        assert isinstance(graph.graph, networkx.Graph)
