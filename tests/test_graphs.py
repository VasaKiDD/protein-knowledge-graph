import networkx
import pytest

from covid_graphs import InteractionGraph, OntologyGraph, ontologies, ontology_aliases


@pytest.fixture(scope="class", params=(True, False))
def interaction_graph(request):
    return InteractionGraph(directed=request.param)


class TestInteractionGraph:
    def test_load_data(self, interaction_graph: InteractionGraph):
        if interaction_graph.is_directed:
            assert isinstance(interaction_graph.graph, networkx.DiGraph)
        else:
            assert isinstance(interaction_graph.graph, networkx.Graph)


class TestOntologyGraph:
    @pytest.mark.parametrize("name", tuple(ontologies))
    def test_init_no_aliases(self, name):
        graph = OntologyGraph(name=name)
        assert isinstance(graph.graph, networkx.Graph)
