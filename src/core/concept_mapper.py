# ========== Imports ==========
from collections import defaultdict
import re

class ConceptMapper:
    """
    ConceptMapper helps create concept graphs and topic hierarchies
    from a list of topics and the main text content.

    - Concept graph: Shows how topics are related (nodes and edges)
    - Hierarchy: Shows main topics and their sub-topics in a tree structure
    """

    def __init__(self):
        # No special setup needed for now
        pass

    def create_concept_graph(self, topics, text):
        """
        Create a concept graph showing relationships between topics.

        Args:
            topics (list): List of key topics (strings)
            text (str): The main text content for context

        Returns:
            dict: Graph structure with nodes, edges, and metadata
        """
        # If there are no topics, return an empty graph
        if not topics or len(topics) == 0:
            return {
                'nodes': [],
                'edges': [],
                'metadata': {
                    'total_nodes': 0,
                    'total_edges': 0
                }
            }

        # Create nodes for each topic
        nodes = self._create_nodes(topics)
        # Create edges showing relationships between topics
        edges = self._create_edges(topics, text)

        # Build the final graph dictionary
        graph = {
            'nodes': nodes,
            'edges': edges,
            'metadata': {
                'total_nodes': len(nodes),
                'total_edges': len(edges)
            }
        }

        return graph

    def _create_nodes(self, topics):
        """
        Create nodes for each topic.

        - First 5 topics are main topics (green color)
        - Next 10 topics are sub-topics (blue color)

        Args:
            topics (list): List of topics

        Returns:
            list: List of node dictionaries
        """
        nodes = []

        # Make sure topics is a list
        if not isinstance(topics, list):
            topics = list(topics)

        # Main topics (top 5)
        for i, topic in enumerate(topics[:5]):
            nodes.append({
                'id': f"node_{i}",
                'label': str(topic)[:30],  # Limit label length for display
                'level': 0,
                'type': 'main',
                'color': '#4CAF50'  # Green
            })

        # Sub-topics (next 10)
        for i, topic in enumerate(topics[5:15], start=5):
            nodes.append({
                'id': f"node_{i}",
                'label': str(topic)[:30],
                'level': 1,
                'type': 'sub',
                'color': '#2196F3'  # Blue
            })

        return nodes

    def _create_edges(self, topics, text):
        """
        Create edges showing relationships between topics.

        - If two topics appear together in a sentence, create an edge.
        - If no edges found, connect first few topics in order.

        Args:
            topics (list): List of topics
            text (str): Main text content

        Returns:
            list: List of edge dictionaries
        """
        edges = []

        # Split text into sentences for analysis
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 10]

        # Check for co-occurrence of topics in sentences
        for i, topic1 in enumerate(topics[:10]):
            for j, topic2 in enumerate(topics[:10]):
                if i < j:
                    co_occurrence = 0
                    for sentence in sentences:
                        sentence_lower = sentence.lower()
                        topic1_lower = str(topic1).lower()
                        topic2_lower = str(topic2).lower()
                        # If both topics appear in the same sentence
                        if topic1_lower in sentence_lower and topic2_lower in sentence_lower:
                            co_occurrence += 1
                    # If found, create an edge (limit weight to 5)
                    if co_occurrence > 0:
                        edges.append({
                            'source': f"node_{i}",
                            'target': f"node_{j}",
                            'weight': min(co_occurrence, 5),
                            'type': 'related'
                        })

        # If no edges found, connect first few topics in sequence
        if len(edges) == 0 and len(topics) >= 2:
            for i in range(min(3, len(topics) - 1)):
                edges.append({
                    'source': f"node_{i}",
                    'target': f"node_{i+1}",
                    'weight': 1,
                    'type': 'related'
                })

        return edges

    def create_hierarchy(self, topics):
        """
        Create a hierarchical (tree) structure of topics.

        - First 3 topics are main nodes.
        - Each main node gets 2 sub-topics (if available).

        Args:
            topics (list): List of topics

        Returns:
            dict: Hierarchy tree structure
        """
        if not topics or len(topics) == 0:
            return {'root': {'name': 'No Topics', 'children': []}}

        hierarchy = {
            'root': {
                'name': 'Main Concepts',
                'children': []
            }
        }

        # Add main topics and their sub-topics
        for i, topic in enumerate(topics[:3]):
            main_node = {
                'name': str(topic),
                'level': 1,
                'children': []
            }
            # Add up to 2 sub-topics for each main topic
            start_idx = 3 + (i * 2)
            end_idx = start_idx + 2
            for sub_topic in topics[start_idx:end_idx]:
                main_node['children'].append({
                    'name': str(sub_topic),
                    'level': 2
                })
            hierarchy['root']['children'].append(main_node)

        return hierarchy