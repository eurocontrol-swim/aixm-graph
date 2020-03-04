"""
Copyright 2020 EUROCONTROL
==========================================

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the
following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following
   disclaimer.
2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following
   disclaimer in the documentation and/or other materials provided with the distribution.
3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products
   derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE
USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

==========================================

Editorial note: this license is an instance of the BSD license template as provided by the Open Source Initiative:
http://opensource.org/licenses/BSD-3-Clause

Details on EUROCONTROL: http://www.eurocontrol.int
"""

__author__ = "EUROCONTROL (SWIM)"

from typing import List, Optional, Union, Any

from aixm import cache
from aixm.features import AIXMFeature, XLinkElement


class Node:

    def __init__(self, id: str, name: str, abbrev: str, keys: List[str]):
        self.id = id
        self.name = name
        self.abbrev = abbrev
        self.keys = keys
        self.keys_concat = False
        self.is_ghost = False

    def __eq__(self, other):
        return self.id == other.id and self.name == other.name and self.abbrev == other.abbrev

    @classmethod
    def from_feature(cls, feature: AIXMFeature):
        keys = [key for data in feature.feature_data for key in data.keys]
        obj = cls(id=feature.uuid, name=feature.el.name, abbrev=feature.abbrev, keys=keys)
        obj.keys_concat = feature.keys_concat

        return obj

    @classmethod
    def from_ghost_xlink(cls, xlink: XLinkElement):
        obj = cls(id=xlink.uuid, name=xlink.name, abbrev=xlink.name, keys=[])
        obj.is_ghost = True

        return obj

    def to_json(self):
        return {
            'id': self.id,
            'name': self.name,
            'abbrev': self.abbrev,
            'keys': self.keys,
            'keys_concat': self.keys_concat,
            'is_ghost': self.is_ghost
        }


class Edge:

    def __init__(self, source: str, target: str, broken: Optional[bool] = False):
        self.source = source
        self.target = target
        self.broken = broken

    def __eq__(self, other):
        return (self.source == other.source and self.target == other.target) or \
               (self.source == other.target and self.target == other.source)

    @classmethod
    def from_features(cls, source: AIXMFeature, target: AIXMFeature):
        return cls(source=source.uuid, target=target.uuid)

    def to_json(self):
        return {
            'source': self.source,
            'target': self.target,
            'is_broken': self.broken
        }


class Graph:

    def __init__(self, nodes: Optional[List[Node]] = None, edges: Optional[List[Edge]] = None):
        self.nodes = nodes or []
        self.edges = edges or []

    def __add__(self, other):
        self.add_nodes(other.nodes)
        self.add_edges(other.edges)

        return self

    @staticmethod
    def _add_items_to_list(item_list: List[Any], items: Any):
        if not isinstance(items, list):
            items = [items]

        for node in items:
            if node not in item_list:
                item_list.append(node)

    def add_nodes(self, nodes: Union[List[Node], Node]):
        self._add_items_to_list(self.nodes, nodes)

    def add_edges(self, edges: Union[List[Edge], Edge]):
        self._add_items_to_list(self.edges, edges)

    def to_json(self):
        return {
            'nodes': [node.to_json() for node in self.nodes],
            'edges': [edge.to_json() for edge in self.edges]
        }


def get_feature_graph(feature: AIXMFeature) -> Graph:
    graph = Graph()

    graph.add_nodes(Node.from_feature(feature))

    for data in feature.feature_data:
        for xlink in (data.xlinks + data.extensions):
            target = cache.get_aixm_feature_by_uuid(xlink.uuid)
            if target is not None:
                node = Node.from_feature(target)
                edge = Edge.from_features(feature, target)
            else:
                node = Node.from_ghost_xlink(xlink)
                edge = Edge(source=feature.uuid, target=xlink.uuid, broken=True)

            graph.add_nodes(node)
            graph.add_edges(edge)

    return graph


def get_graph(feature_name: Optional[str] = None) -> Graph:
    graph = Graph()

    features = cache.get_features() if feature_name is None else cache.get_aixm_features_by_name(feature_name)

    for feature in features:
        graph += get_feature_graph(feature)

    return graph
