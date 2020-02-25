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

_logger = logging.getLogger(__name__)


def load_features(context, config) -> Dict[str, AIXMFeature]:
    features_dict = {}
    for event, elem in context:
        if event == 'end':
            feature_element = elem[0]
            feature_name = get_tag_without_ns(feature_element)
            feature = AIXMFeature(element=feature_element, keys_properties=config[feature_name]["keys"] or [])
            features_dict[feature.uuid] = feature

            # clean up obsolete elements
            elem.clear()
            while elem.getprevious() is not None:
                del elem.getparent()[0]
            del elem

    return features_dict


@timeit
def assign_associations(features_dict: Dict[str, AIXMFeature]) -> Tuple[Dict[str, AIXMFeature], List[XLinkElement]]:
    broker_links = []
    for _, source_feature in features_dict.items():
        for source_data in source_feature.feature_data:
            for xlink in source_data.xlinks:
                target_feature = features_dict.get(xlink.uuid)
                if target_feature:
                    source_extension = Extension(f'the{source_feature.el.name}', source_feature.uuid)
                    for target_data in target_feature.feature_data:
                        target_data.add_extension(source_extension)
                else:
                    broker_links.append(xlink)

    return features_dict, broker_links


def process_aixm(filepath, element_tag, config):
    context = etree.iterparse(filepath, events=('end',), tag=element_tag, remove_comments=True)

    features = load_features(context, config['FEATURES'])

    del context

    assign_associations(features)

    return features
