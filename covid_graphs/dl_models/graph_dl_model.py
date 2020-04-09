import pickle
import time

import networkx
import torch
import torch.nn as nn

device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

"""
Experimental : simple deep learning model to infer protein present in a tissue from a
vector of expression.
"""


class PPGCN(nn.Module):
    def __init__(self, accepted_link_value=0.0):
        super(PPGCN, self).__init__()
        self.complete_graph = networkx.read_gpickle("../data/pp_interactions_undirected.gpickle")
        self.tissue_num_mapping = pickle.load(open("../data/tissue_num_mapping.pck", "rb"))
        self.accepted_link_value = accepted_link_value
        self.restrain_graph_by_values()
        self.current_values = {}
        self.new_values = {}
        self.all_layers = None
        self.construct_layers()

    def restrain_graph_by_values(self):
        edges = [
            (x, y)
            for x, y, z in self.complete_graph.edges(data=True)
            if z["score"] > self.accepted_link_value
        ]
        self.complete_graph = self.complete_graph.edge_subgraph(edges)

    def construct_layers(self):
        params = {}
        num_parameters = 0
        for node, neighbors in self.complete_graph.adjacency():
            num_links = len(neighbors.keys())
            if num_links == 0:
                import pdb

                pdb.set_trace()
            params[node] = nn.Sequential(
                nn.Linear(num_links, num_links // 2 + 1, bias=False),
                nn.ReLU(),
                nn.Linear(num_links // 2 + 1, 1, bias=False),
                nn.Sigmoid(),
            )
            params[node] = nn.Sequential(nn.Linear(num_links, 1, bias=False), nn.Sigmoid())
            num_parameters += (num_links * (num_links // 2 + 1)) + num_links // 2 + 1
            # num_parameters += num_links
        print("Number of paramters :", num_parameters)
        self.all_layers = nn.ModuleDict(params).to(device)

    def forward_n_times(self, n_times, requires_grad, init_values=None, tissue=None):
        if tissue is not None:
            self.init_values_from_tissue(tissue)
        if init_values is not None:
            self.init_values_from_data(init_values)

        for _ in range(n_times):
            d = time.time()
            if requires_grad:
                self.forward_once()
            else:
                with torch.no_grad():
                    self.forward_once()
            print(time.time() - d)

        data_out = [self.new_values[node] for node in self.new_values.keys()]
        assert len(data_out) == len(list(self.complete_graph.nodes()))
        data_out = torch.as_tensor(data_out, dtype=torch.float32, device=device)
        return data_out

    def forward_once(self):
        for node, neighbors in self.complete_graph.adjacency():
            vals = []
            for neighbor in neighbors.keys():
                vals.append(self.current_values[neighbor])
            vals = torch.as_tensor(vals, dtype=torch.float32, device=device)
            self.new_values[node] = self.all_layers[node](vals)
        for node in self.new_values.keys():
            self.current_values[node] = self.new_values[node]

    def init_values_from_tissue(self, tissue):
        self.new_values = {}
        num = self.tissue_num_mapping[tissue]
        for node in self.complete_graph.nodes():
            self.new_values[node] = torch.as_tensor([0.0], dtype=torch.float32, device=device)
            self.current_values[node] = torch.as_tensor(
                [self.complete_graph.nodes[node]["expression_data"][num]],
                dtype=torch.float32,
                device=device,
            )

    def init_values_from_data(self, init_values):
        raise NotImplementedError

    def propagate_node(self, node):
        for pred in self.complete_graph.predecessors(node):
            actions = []
            for edge in self.complete_graph[pred][node]:
                link_type = self.complete_graph[pred][node][edge]["link"]
                link_score = self.complete_graph[pred][node][edge]["score"]
                if link_score > self.accepted_link_value and link_type in self.accepted_links:
                    actions.append(link_type)
                    # self.__getattribute__(link_type + "_propagate")(pred, node)
