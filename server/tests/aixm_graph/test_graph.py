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

import pytest

from aixm_graph import XLINK_NS
from aixm_graph.datasets.features import AIXMFeature, AIXMFeatureTimeSlice
from aixm_graph.datasets.fields import Field, XLinkField
from aixm_graph.graph import Node, Edge, Graph


def test_node__from_feature():
    time_slice = AIXMFeatureTimeSlice(name='timeSlice')
    time_slice.data_fields.append(Field(name='field', text='text'))

    feature = AIXMFeature('name')
    feature.identifier = '1'
    feature.time_slices.append(time_slice)
    feature.config = {
        'abbrev': 'AAA',
        'color': 'blue',
        'shape': 'square',
        'fields': {
            'concat': True,
        }
    }

    node = Node.from_feature(feature)

    assert node.id == '1'
    assert node.name == 'name'
    assert node.abbrev == 'AAA'
    assert node.fields == [{'field': 'text'}]
    assert node.color == 'blue'
    assert node.shape == 'square'
    assert node.fields_concat is True
    assert node.is_ghost is False
    assert node.assoc_count == 0


def test_node__from_broken_xlink():
    xlink = XLinkField(name='xlink', attrib={f'{{{XLINK_NS}}}href': 'a1b2c3'})

    node = Node.from_broken_xlink(xlink)

    assert node.id == 'a1b2c3'
    assert node.name == 'xlink'
    assert node.abbrev == 'xlink'
    assert node.is_ghost is True


def test_node__to_json():
    time_slice = AIXMFeatureTimeSlice(name='timeSlice')
    time_slice.data_fields.append(Field(name='field', text='text'))

    feature = AIXMFeature('name')
    feature.identifier = '1'
    feature.time_slices.append(time_slice)
    feature.config = {
        'abbrev': 'AAA',
        'color': 'blue',
        'shape': 'square',
        'fields': {
            'concat': True,
        }
    }

    node = Node.from_feature(feature)
    assert {
        'id': '1',
        'name': 'name',
        'abbrev': 'AAA',
        'fields': [{'field': 'text'}],
        'color': 'blue',
        'shape': 'square',
        'fields_concat': True,
        'is_ghost': False,
        'assoc_count': 0
    } == node.to_json()


@pytest.mark.parametrize('edge, expected_json', [
    (
        Edge(
            source='source',
            target='target',
            name='name',
            is_broken=True
        ),
        {
            'source': 'source',
            'target': 'target',
            'name': 'name',
            'is_broken': True
        }
    )
])
def test_edge__to_json(edge, expected_json):
    assert expected_json == edge.to_json()


def test_graph__to_json():
    time_slice1 = AIXMFeatureTimeSlice(name='timeSlice')
    time_slice1.data_fields.append(Field(name='field', text='text'))

    feature1 = AIXMFeature('name1')
    feature1.identifier = '1'
    feature1.time_slices.append(time_slice1)
    feature1.config = {
        'abbrev': 'AAA',
        'color': 'blue',
        'shape': 'square',
        'fields': {
            'concat': True,
        }
    }

    time_slice2 = AIXMFeatureTimeSlice(name='timeSlice')
    time_slice2.data_fields.append(Field(name='field', text='text'))

    feature2 = AIXMFeature('name2')
    feature2.identifier = '2'
    feature2.time_slices.append(time_slice2)
    feature2.config = {
        'abbrev': 'AAA',
        'color': 'blue',
        'shape': 'square',
        'fields': {
            'concat': True,
        }
    }

    node1 = Node.from_feature(feature1)
    node2 = Node.from_feature(feature2)

    edge = Edge(source='1', target='2', name='name')

    graph = Graph()
    graph.add_nodes([node1, node2])
    graph.add_edges(edge)

    assert {
        'nodes': [
            {
                'id': '1',
                'name': 'name1',
                'abbrev': 'AAA',
                'fields': [{'field': 'text'}],
                'color': 'blue',
                'shape': 'square',
                'fields_concat': True,
                'is_ghost': False,
                'assoc_count': 0
            },
            {
                'id': '2',
                'name': 'name2',
                'abbrev': 'AAA',
                'fields': [{'field': 'text'}],
                'color': 'blue',
                'shape': 'square',
                'fields_concat': True,
                'is_ghost': False,
                'assoc_count': 0
            }
        ],
        'edges': [{
            'source': '1',
            'target': '2',
            'name': 'name',
            'is_broken': False
        }]
    } == graph.to_json()
