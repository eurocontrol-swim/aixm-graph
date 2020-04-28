"""
Copyright 2020 EUROCONTROL
==========================================

Redistribution and use in source and binary forms, with or without modification, are permitted
provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this list of conditions
   and the following disclaimer.
2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions
   and the following disclaimer in the documentation and/or other materials provided with the
   distribution.
3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse
   or promote products derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR
IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND
FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER
IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF
THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

==========================================

Editorial note: this license is an instance of the BSD license template as provided by the Open
Source Initiative: http://opensource.org/licenses/BSD-3-Clause

Details on EUROCONTROL: http://www.eurocontrol.int
"""

__author__ = "EUROCONTROL (SWIM)"

from typing import List, Optional, Union, Any, Dict

from aixm_graph.datasets.features import AIXMFeature
from aixm_graph.datasets.fields import XLinkField


class Node:

    def __init__(self,
                 id: str,
                 name: str,
                 abbrev: str,
                 fields: Optional[List[Dict[str, str]]] = None,
                 color: Optional[str] = None,
                 shape: Optional[str] = None,
                 fields_concat: bool = False,
                 assoc_count: int = 0,
                 is_ghost: bool = False
    ):
        """
        Holds information of a feature which will be represented as a node in the graph displayed
        in the frontend.
        :param id:
        :param name:
        :param abbrev:
        :param fields:
        :param color:
        :param shape:
        :param fields_concat:
        :param assoc_count:
        :param is_ghost: indicates whether it's a feature that was supposed to be referenced by
                         another feature but it was not found in the dataset
        """
        self.id = id
        self.name = name
        self.abbrev = abbrev
        self.color = color
        self.shape = shape
        self.fields = fields or []
        self.fields_concat = fields_concat
        self.assoc_count = assoc_count
        self.is_ghost = is_ghost

    def __eq__(self, other):
        return self.id == other.id and self.name == other.name and self.abbrev == other.abbrev

    @classmethod
    def from_feature(cls, feature: AIXMFeature):
        return cls(
            id=feature.id,
            name=feature.name,
            abbrev=feature.config['abbrev'],
            fields=[
                {field.name: field.text}
                for _, slice in feature.time_slices.items()
                for field in slice.data_fields
            ],
            color=feature.config['color'],
            shape=feature.config['shape'],
            fields_concat=feature.config['fields']['concat'],
            assoc_count=len(feature.associations)
        )

    @classmethod
    def from_broken_xlink(cls, xlink: XLinkField):
        return cls(id=xlink.uuid, name=xlink.name, abbrev=xlink.name, is_ghost=True)

    def to_json(self):
        return {
            'id': self.id,
            'name': self.name,
            'abbrev': self.abbrev,
            'fields': self.fields,
            'color': self.color,
            'shape': self.shape,
            'fields_concat': self.fields_concat,
            'is_ghost': self.is_ghost,
            'assoc_count': self.assoc_count
        }


class Edge:

    def __init__(self, source: str, target: str, name: str, is_broken: Optional[bool] = False):
        """
        Holds information about two features where one references to the other

        :param source:
        :param target:
        :param name:
        :param is_broken: indicates whether one of the features is ghost thus i.e. it was not found
                          in the dataset
        """
        self.source = source
        self.target = target
        self.name = name
        self.is_broken = is_broken

    def __eq__(self, other):
        return (self.source == other.source
                and self.target == other.target
                and self.name == other.name) \
               or \
               (self.source == other.target
                and self.target == other.source
                and self.name == other.name)

    def to_json(self):
        return {
            'source': self.source,
            'target': self.target,
            'name': self.name,
            'is_broken': self.is_broken
        }


class Graph:

    def __init__(self, nodes: Optional[List[Node]] = None, edges: Optional[List[Edge]] = None):
        """
        :param nodes:
        :param edges:
        """
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
