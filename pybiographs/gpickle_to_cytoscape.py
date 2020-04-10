import json

import networkx


# TODO(Vasakidd): Make sure all the relevant info is included in the documentation.
def convert_to_cytoscape(source_path, target_path):
    """
    Explain what this does here.

    Args:
        source_path: Path of the .gpickle graph
        target_path: Path where the .cyjs graph will be saved.

    Returns:
        None

    """
    graph = networkx.read_gpickle(source_path)
    json_graph = networkx.readwrite.json_graph.cytoscape_data(graph)
    with open(target_path + ".cyjs", "w") as json_file:
        json.dump(json_graph, json_file)
