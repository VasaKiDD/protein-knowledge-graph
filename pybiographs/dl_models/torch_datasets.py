import numpy as np
from torch.utils.data import Dataset
from tqdm import tqdm

from pybiographs.graphs import InteractionGraph


# TODO(Vasakidd): Make sure all the relevant info is included in the documentation.
class PPInteractionDataset(Dataset):
    """
    Extract interaction data from graph an creates a torch dataset.
    """

    def __init__(
        self,
        graph: InteractionGraph,
        score_threshold: float,
        node_attribute: str,
        regression: bool,
        no_interactions_ratio: float = 1.0,
    ):
        """
        Initialize a :class:`PPInteractionDataset`.

        Args:
            graph: Interaction graph that will be transformed to a Dataset.
            score_threshold: Threshold on scores in edges. TODO(vasakidd): give
                             more info about this parameter.
            node_attribute: The type of node label to extract from graph, check
                           :class:`InteractionGraph` for more information on
                           the data available node attributes.
            regression: ``True`` creates a dataset for regression task on edge scores.
                        ``False``  creates a dataset for classification (existing
                        edges will be scored 1.0).
            no_interactions_ratio: TODO(vasakidd): give more info about this parameter.

        """
        if graph.is_directed:
            edges = [
                (x, y, z["link"], z["score"])
                for x, y, z in graph.edges(data=True)
                if z["score"] >= score_threshold
            ]
            data = []
            for prot_a, prot_b, link, score in edges:
                prot_a_data = graph.nodes(data=True)[prot_a][node_attribute]
                prot_b_data = graph.nodes(data=True)[prot_b][node_attribute]
                if regression:
                    data.append((prot_a_data, prot_b_data, link, score))
                else:
                    data.append((prot_a_data, prot_b_data, link, 1.0))
        else:
            edges = [
                (x, y, z["score"])
                for x, y, z in graph.edges(data=True)
                if z["score"] >= score_threshold
            ]
            data = []
            for prot_a, prot_b, score in edges:
                prot_a_data = graph.nodes(data=True)[prot_a][node_attribute]
                prot_b_data = graph.nodes(data=True)[prot_b][node_attribute]
                if regression:
                    data.append((prot_a_data, prot_b_data, score))
                else:
                    data.append((prot_a_data, prot_b_data, 1.0))
        self.data = data
        nodes = list(graph.nodes())
        no_data = []
        sampled = []
        num_no_labels = int(no_interactions_ratio * len(data))
        for _ in tqdm(range(num_no_labels)):
            prot_a = np.random.choice(nodes)
            prot_b = np.random.choice(nodes)
            while (
                (prot_a, prot_b) in graph.edges()
                or (prot_b, prot_a) in graph.edges()
                or (prot_b, prot_a) in sampled
                or (prot_a, prot_b) in sampled
            ):
                prot_a = np.random.choice(nodes)
                prot_b = np.random.choice(nodes)
            prot_a_data = graph.nodes(data=True)[prot_a][node_attribute]
            prot_b_data = graph.nodes(data=True)[prot_b][node_attribute]
            if graph.is_directed:
                no_data.append((prot_a_data, prot_b_data, "not_linked", 0.0))
            else:
                no_data.append((prot_a_data, prot_b_data, 0.0))
            sampled.append((prot_a, prot_b))
        self.data.extend(no_data)

    def __getitem__(self, ix):
        return self.data[ix]

    def __len__(self):
        return len(self.data)
