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

from typing import List, Dict

from aixm import cache
from aixm.features import AIXMFeature


def node_from_feature(feature: AIXMFeature):
    return {
        'name': feature.el.name,
        'abbrev': feature.abbrev,
        'id': feature.uuid
    }


def edge_from_features(source: AIXMFeature, target: AIXMFeature):
    return {
        'from': source.uuid,
        'to': target.uuid
    }


def _edge_exists(edges: List[Dict[str, str]], edge: Dict[str, str]):
    reverse_edge = {
        'from': edge['to'],
        'to': edge['from']
    }

    return edge in edges or reverse_edge in edges


def get_graph(feature_name: str):
    nodes = []
    edges = []

    for source in cache.get_aixm_features_by_name(feature_name):

        node = node_from_feature(source)
        if node not in nodes:
            nodes.append(node)

        for xlink in (source.feature_data[0].xlinks + source.feature_data[0].extensions):
            target = cache.get_aixm_features_by_uuid(xlink.uuid)
            if target is not None:
                node = node_from_feature(target)
                if node not in nodes:
                    nodes.append(node)

                edge = edge_from_features(source, target)
                if not _edge_exists(edges, edge):
                    edges.append(edge_from_features(source, target))

    return nodes, edges
