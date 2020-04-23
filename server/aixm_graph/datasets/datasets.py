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

import os
from collections import defaultdict
from functools import partial
from typing import Optional

from lxml import etree

from aixm_graph.datasets.features import AIXMFeatureFactory, AIXMFeature
from aixm_graph.datasets.fields import Extension
from aixm_graph.graph import Graph, Node, Edge


class FeatureTypeStats:
    def __init__(self, name: str):
        self.name = name


class AIXMDataSet:
    feature_factory = AIXMFeatureFactory
    basic_message_tag = 'AIXMBasicMessage'
    sequence_tag = 'hasMember'
    extension_ns = {'mxia': "http://www.aixm.aero/schema/5.1.1/extensions/mxia"}

    def __init__(self, filepath: str) -> None:
        """

        :param filepath:
        """
        self.id = None
        self._feature_type_stats = None
        self._filepath = filepath
        self._features_dict = {}
        self._sequence_ns = ''
        self._ns_map = self.extension_ns
        self._skeleton_filepath = None

    @property
    def name(self):
        """

        :return:
        """
        return os.path.basename(self._filepath)

    @property
    def features(self):
        """
        :return: Generator[FeatureType]
        """
        for _, feature in self._features_dict.items():
            yield feature

    @property
    def feature_type_stats(self):
        """

        :return:
        """
        return self._feature_type_stats

    def _compute_feature_type_stats(self):
        """

        :return:
        """
        self._feature_type_stats = defaultdict(lambda: defaultdict(int))

        for feature in self.features:
            self._feature_type_stats[feature.name]['size'] += 1

            if feature.has_broken_xlinks:
                self._feature_type_stats[feature.name]['features_num_with_broken_xlinks'] += 1

        return self

    def has_feature_name(self, name: str) -> bool:
        for feature in self.features:
            if feature.name == name:
                return True

        return False

    def get_feature_by_id(self, feature_id: str):
        """

        :param feature_id:
        :return:
        """
        return self._features_dict.get(feature_id)

    def filter_features(self, name: str, field_value: Optional[str] = None):
        """

        :param name:
        :param field_value:
        :return:
        """
        features = (feature for feature in self.features if feature.name == name)

        if field_value:
            features = (feature for feature in features if feature.matches_field_value(field_value))

        return features

    def process(self):
        """
        :return: AIXMDataSet
        """
        return self._parse()._create_extensions()._compute_feature_type_stats()

    def _parse(self):
        """
        :return: AIXMDataSet
        """

        kwargs = dict(events=('end', 'start-ns'), remove_comments=True)
        if self.sequence_tag:
            kwargs.update(tag=f'{{*}}{self.sequence_tag}')

        context = etree.iterparse(self._filepath, **kwargs)

        for event, sequence_element in context:
            if event == 'start-ns':
                ns_code, ns_link = sequence_element
                self._ns_map[ns_code] = ns_link
            elif event == 'end':
                if not self._sequence_ns:
                    self._sequence_ns = sequence_element.nsmap[sequence_element.prefix]

                feature = self.feature_factory.feature_from_sequence_element(seq_element=sequence_element)
                self._features_dict[feature.id] = feature

                # clean up obsolete elements
                sequence_element.clear()
                while sequence_element.getprevious() is not None:
                    del sequence_element.getparent()[0]
                del sequence_element

        del context

        return self

    def _create_extensions(self):
        """
        :return: AIXMDataSet
        """
        extension_prefix = list(self.extension_ns.keys())[0]

        for source_feature in self.features:
            for xlink in source_feature.xlinks:
                target_feature = self._features_dict.get(xlink.uuid)
                if target_feature:
                    target_feature.add_extension(
                        Extension.create(name=source_feature.name,
                                         uuid=source_feature.id,
                                         prefix=extension_prefix))
                else:
                    xlink.set_broken()

        return self

    def make_skeleton_path(self):
        """

        :return:
        """
        filename, ext = os.path.splitext(self._filepath)

        return f"{filename}_skeleton{ext}"

    def generate_skeleton(self):
        """

        :return:
        """
        if self._skeleton_filepath:
            return self._skeleton_filepath

        root = etree.Element(f"{{{self._sequence_ns}}}{self.basic_message_tag}", nsmap=self._ns_map)
        for feature in self.features:
            member_el = etree.Element(f'{{{self._sequence_ns}}}{self.sequence_tag}', nsmap=self._ns_map)
            feature_el = feature.to_lxml(self._ns_map)

            member_el.append(feature_el)
            root.append(member_el)

        self._skeleton_filepath = self.make_skeleton_path()
        with open(self._skeleton_filepath, 'w') as f:
            f.write(etree.tostring(root, xml_declaration=True, pretty_print=True).decode('utf-8'))

        return self._skeleton_filepath

    def get_graph_for_feature(self, feature: AIXMFeature) -> Graph:
        """

        :param feature:
        :return:
        """
        graph = Graph()
        graph.add_nodes(Node.from_feature(feature))

        for time_slice_id, time_slice in feature.time_slices.items():
            for association in time_slice.associations:
                target = self._features_dict.get(association.uuid)
                if target is not None:
                    node = Node.from_feature(target)
                    edge = Edge(source=feature.id, target=target.id, name=time_slice_id)
                else:
                    node = Node.from_broken_xlink(association)
                    edge = Edge(source=feature.id, target=association.uuid, name=time_slice_id, broken=True)

                graph.add_nodes(node)
                graph.add_edges(edge)

        return graph

    def get_graph(self, features: [AIXMFeature], offset: int, limit: int) -> Graph:
        """

        :param offset:
        :param limit:
        :return:
        """
        # features = self.filter_features(feature_name, filter_field)
        graph = Graph()
        for i, feature in enumerate(features):
            if i < offset:
                continue
            if limit is not None and i > limit:
                break
            graph += self.get_graph_for_feature(feature=feature)

        return graph
