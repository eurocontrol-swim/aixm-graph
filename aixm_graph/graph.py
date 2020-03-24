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

from aixm_graph import cache
from aixm_graph.features import AIXMFeature, XLinkElement


class Node:

    def __init__(self, id: str, name: str, abbrev: str, keys: List[str]):
        self.id = id
        self.name = name
        self.abbrev = abbrev
        self.keys = keys
        self.keys_concat = False
        self.links_count = 0
        self.is_ghost = False
        self.color = None
        self.shape = None

    def __eq__(self, other):
        return self.id == other.id and self.name == other.name and self.abbrev == other.abbrev

    @classmethod
    def from_feature(cls, feature: AIXMFeature):
        keys = [key for data in feature.feature_data for key in data.keys]
        obj = cls(id=feature.uuid, name=feature.el.name, abbrev=feature.abbrev, keys=keys)
        obj.keys_concat = feature.keys_concat
        obj.links_count = feature.links_count()

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
            'is_ghost': self.is_ghost,
            'links_count': self.links_count
        }


class Edge:

    def __init__(self, source: str, target: str, name: str, broken: Optional[bool] = False):
        self.source = source
        self.target = target
        self.name = name
        self.broken = broken

    def __eq__(self, other):
        return (self.source == other.source and self.target == other.target and self.name == other.name) or \
               (self.source == other.target and self.target == other.source and self.name == other.name)

    def to_json(self):
        return {
            'source': self.source,
            'target': self.target,
            'name': self.name,
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

        for item in items:
            if item not in item_list:
                item_list.append(item)

    def add_nodes(self, nodes: Union[List[Node], Node]):
        self._add_items_to_list(item_list=self.nodes, items=nodes)

    def add_edges(self, edges: Union[List[Edge], Edge]):
        self._add_items_to_list(item_list=self.edges, items=edges)

    def to_json(self):
        return {
            'nodes': [node.to_json() for node in self.nodes],
            'edges': [edge.to_json() for edge in self.edges]
        }


def get_file_feature_graph(file_id: str, feature_id: str) -> Graph:
    file = cache.get_file(file_id)
    feature = file['features'].get(feature_id)

    graph = Graph()
    graph.add_nodes(Node.from_feature(feature))

    for data in feature.feature_data:
        for xlink in (data.xlinks + data.extensions):
            target = file['features'].get(xlink.uuid)
            if target is not None:
                node = Node.from_feature(target)
                edge = Edge(source=feature.uuid, target=target.uuid, name=data.name)
            else:
                node = Node.from_ghost_xlink(xlink)
                edge = Edge(source=feature.uuid, target=xlink.uuid, name=data.name, broken=True)

            graph.add_nodes(node)
            graph.add_edges(edge)

    return graph


def get_file_features_graph(file_id: str, features: List[AIXMFeature], offset: int = 0, limit: Optional[int] = None):

    graph = Graph()
    for i, feature in enumerate(features):
        if i < offset:
            continue
        if limit is not None and i > limit:
            break
        graph += get_file_feature_graph(file_id=file_id, feature_id=feature.uuid)

    return graph
