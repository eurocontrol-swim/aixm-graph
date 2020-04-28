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

import os
from collections import defaultdict
from typing import Optional, Dict, Generator

from lxml import etree

from aixm_graph.datasets.features import AIXMFeatureFactory, AIXMFeature
from aixm_graph.datasets.fields import Extension
from aixm_graph.graph import Graph, Node, Edge


class AIXMDataSet:
    feature_factory = AIXMFeatureFactory
    basic_message_tag = 'AIXMBasicMessage'
    sequence_tag = 'hasMember'
    extension_ns = {'mxia': "http://www.aixm.aero/schema/5.1.1/extensions/mxia"}

    def __init__(self, filepath: str) -> None:
        """
        Holds the dataset data from the parsing point and produces the graph and skeleton file.

        :param filepath:
        """
        """A unique identifier that is acquired upon being saved in cache (memory)"""
        self.id: Optional[int] = None

        """Holds that stat info of the dataset, i.e. the total number of features as well as broken
           xlinks per feature type 
        """
        self._feature_type_stats: Optional[Dict[str, int]] = None

        self._filepath: str = filepath

        """Holds the features of the dataset per id in a hashtable for faster access"""
        self._features_dict: Dict[str, AIXMFeature] = {}

        """Holds the namespace of the sequence element, i.e. `hasMember` to be used in skeleton
           generation
        """
        self._sequence_ns: str = ''

        """Is updated with the namespaces of each element"""
        self._ns_map: Dict[str, str] = self.extension_ns

        self._skeleton_filepath: Optional[str] = None

    @property
    def name(self) -> str:
        """
        :return: The basename of the dataset file
        """
        return os.path.basename(self._filepath)

    @property
    def features(self):
        """
        Enables faster access to the features of the dataset

        :return: Generator[Feature]
        """
        for _, feature in self._features_dict.items():
            yield feature

    @property
    def feature_type_stats(self) -> Dict[str, int]:
        """

        :return:
        """
        return self._feature_type_stats

    def has_feature_type_name(self, name: str) -> bool:
        """

        :param name:
        :return:
        """
        for feature in self.features:
            if feature.name == name:
                return True

        return False

    def get_feature_by_id(self, feature_id: str) -> AIXMFeature:
        """

        :param feature_id:
        :return:
        """
        return self._features_dict.get(feature_id)

    def filter_features(self,
                        name: str,
                        field_value: Optional[str] = None):
        """
        Filters the features per name and/or field value

        :param name:
        :param field_value:
        :return: Generator[AIXMFeature]
        """
        features = (feature for feature in self.features if feature.name == name)

        if field_value:
            features = (feature for feature in features if feature.matches_field_value(field_value))

        return features

    def process(self):
        """
        Performs the processing of the dataset including:
            - parse the dataset file
            - extract features and store their essential data
            - create extensions (bi-directional associations)
            - generate stats to be used in front-end
        :return: AIXMDataSet
        """
        return self._parse()._create_extensions()._compute_feature_type_stats()

    def _parse(self):
        """
        Parse the file using the `etree.iterparse` method in order to handle big files and avoid
        loading them in memory at once.

        The element features are parsed and extracted one by one. Their data are stored and they are
        deleted before proceeding to the next one.

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
        For each xlink reference found in a feature, an extension (xlink) is created to the
        referred featured pointing back to it. If the referred feature is not found then the xlink
        is marked as broken.

        :return: AIXMDataSet
        """
        extension_prefix = list(self.extension_ns.keys())[0]

        for source_feature in self.features:
            for xlink in source_feature.xlinks:
                target_feature = self._features_dict.get(xlink.uuid)
                if target_feature:
                    target_feature.add_extension(
                        Extension.create(name=f'the{source_feature.name}',
                                         uuid=source_feature.id,
                                         prefix=extension_prefix))
                else:
                    xlink.set_broken()

        return self

    def _compute_feature_type_stats(self):
        """
        Generates a few stats to be used in the front-end, i.e. the total number of features as well
        as broken xlinks per feature type.
        :return:
        """
        self._feature_type_stats = defaultdict(lambda: defaultdict(int))

        for feature in self.features:
            self._feature_type_stats[feature.name]['size'] += 1

            if feature.has_broken_xlinks:
                self._feature_type_stats[feature.name]['features_num_with_broken_xlinks'] += 1

        return self

    def make_skeleton_path(self) -> str:
        """

        :return:
        """
        filename, ext = os.path.splitext(self._filepath)

        return f"{filename}_skeleton{ext}"

    def generate_skeleton(self) -> str:
        """
        Skeleton is a subset of the original dataset including only the information that was
        extracted by it plus the created extensions

        :return: the path of the generated skeleton file
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
        Creates a graph (nodes, edges) for the given feature. The nodes will include the feature and
        it's associations while the edges will indicate which is connected with which.

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
                    edge = Edge(source=feature.id, target=association.uuid, name=time_slice_id, is_broken=True)

                graph.add_nodes(node)
                graph.add_edges(edge)

        return graph

    def get_graph(self, features, offset: int, limit: int) -> Graph:
        """
        Creates a graph for a collection of features.

        :param features: Generator[AIXMFeature]
        :param offset:
        :param limit:
        :return:
        """
        # features = self.filter_features(feature_name, filter_field)
        graph = Graph()
        for i, feature in enumerate(features):
            if i < offset:
                continue

            if i > limit:
                break

            graph += self.get_graph_for_feature(feature=feature)

        return graph
