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

import logging
from typing import Dict, Tuple, List

from lxml import etree

from aixm.features import AIXMFeature, Extension, XLinkElement
from aixm.utils import get_tag_without_ns, timeit
from aixm import cache

_logger = logging.getLogger(__name__)

message_namespaces = ['http://www.aixm.aero/schema/5.1.1/message', 'http://www.aixm.aero/schema/5.1/message']


def get_message_namespace(filepath):
    for event, elem in etree.iterparse(filepath, events=('end',)):
        if event == 'end':
            for ns in message_namespaces:
                if ns in elem.nsmap.values():
                    return ns


def feature_generator(context, config):
    for event, elem in context:
        if event == 'end':
            feature_element = elem[0]
            feature_name = get_tag_without_ns(feature_element)
            feature = AIXMFeature(element=feature_element,
                                  keys=config[feature_name]["keys"],
                                  abbrev=config[feature_name]["abbrev"])

            # clean up obsolete elements
            elem.clear()
            while elem.getprevious() is not None:
                del elem.getparent()[0]
            del elem

            yield feature


def assign_associations(features_dict: Dict[str, AIXMFeature]) -> Dict[str, AIXMFeature]:
    for _, source_feature in features_dict.items():
        for source_data in source_feature.feature_data:
            for xlink in source_data.xlinks:
                target_feature = features_dict.get(xlink.uuid)
                if target_feature:
                    source_extension = Extension(f'the{source_feature.el.name}', source_feature.uuid)
                    for target_data in target_feature.feature_data:
                        target_data.add_extension(source_extension)
                else:
                    source_data.broken_xlinks.append(xlink)

    return features_dict


def process_aixm(filepath, features_config):
    message_ns = get_message_namespace(filepath)

    context = etree.iterparse(filepath, events=('end',), tag=f'{{{message_ns}}}hasMember', remove_comments=True)

    for feature in feature_generator(context, features_config):
        cache.save_aixm_feature(feature)

    del context

    assign_associations(cache.get_aixm_features_dict())
