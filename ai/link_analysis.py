import json
import networkx as nx
from collections import Counter


class LinkAnalyzer:
    def __init__(self):
        self.graph = nx.Graph()

    def build_graph(self, nodes, edges):
        self.graph = nx.Graph()
        for node in nodes:
            self.graph.add_node(node['id'], **node)

        for edge in edges:
            self.graph.add_edge(edge['source'], edge['target'], **edge.get('attributes', {}))

        return self.graph

    def analyze(self, nodes, edges):
        self.build_graph(nodes, edges)

        if len(self.graph.nodes()) == 0:
            return {
                'nodes_count': 0,
                'edges_count': 0,
                'central_nodes': [],
                'communities': [],
                'graph_data': json.dumps({'nodes': [], 'edges': []})
            }

        degree_centrality = nx.degree_centrality(self.graph)
        betweenness_centrality = nx.betweenness_centrality(self.graph)
        closeness_centrality = nx.closeness_centrality(self.graph)
        eigenvector_centrality = nx.eigenvector_centrality(self.graph, max_iter=1000)

        central_nodes = []
        for node_id in self.graph.nodes():
            central_nodes.append({
                'id': node_id,
                'degree': degree_centrality.get(node_id, 0),
                'betweenness': betweenness_centrality.get(node_id, 0),
                'closeness': closeness_centrality.get(node_id, 0),
                'eigenvector': eigenvector_centrality.get(node_id, 0)
            })

        central_nodes.sort(key=lambda x: x['degree'] + x['betweenness'], reverse=True)

        communities = []
        try:
            communities_found = nx.community.greedy_modularity_communities(self.graph)
            for idx, community in enumerate(communities_found):
                communities.append({
                    'id': idx,
                    'members': list(community),
                    'size': len(community)
                })
        except Exception:
            pass

        graph_data = {
            'nodes': [
                {
                    'id': node_id,
                    'label': self.graph.nodes[node_id].get('label', node_id),
                    'type': self.graph.nodes[node_id].get('type', 'unknown'),
                    'size': 10 + degree_centrality.get(node_id, 0) * 50
                }
                for node_id in self.graph.nodes()
            ],
            'edges': [
                {
                    'source': u,
                    'target': v,
                    'weight': self.graph[u][v].get('weight', 1)
                }
                for u, v in self.graph.edges()
            ]
        }

        return {
            'nodes_count': len(self.graph.nodes()),
            'edges_count': len(self.graph.edges()),
            'central_nodes': central_nodes[:10],
            'communities': communities,
            'graph_data': json.dumps(graph_data)
        }

    def find_shortest_path(self, source, target):
        try:
            return nx.shortest_path(self.graph, source=source, target=target)
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            return None

    def find_connected_components(self):
        return list(nx.connected_components(self.graph))

    def detect_communities(self):
        try:
            return list(nx.community.greedy_modularity_communities(self.graph))
        except Exception:
            return []

    def get_degree_distribution(self):
        degrees = [d for _, d in self.graph.degree()]
        return Counter(degrees)