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

import uuid
from typing import Dict, Optional

from aixm_graph.features import AIXMFeature

DATABASE = {
    'features_config': {},
    'files': {}
}


def save_features_config(config: Dict):
    DATABASE['features_config'] = config


def get_features_config():
    return DATABASE['features_config']


def save_file(filepath: str) -> str:
    _id = uuid.uuid4().hex[:6]
    file = {
        'path': filepath,
        'message_ns': "",
        'nsmap': {},
        'features': {},
        'stats': {}
    }
    DATABASE['files'][_id] = file

    return _id


def get_file(file_id: str):
    return DATABASE['files'][file_id]


def get_file_nsmap(file_id: str):
    return DATABASE['files'][file_id]['nsmap']


def update_file_nsmap(file_id: str, ns_code: str, ns_link: str):
    DATABASE['files'][file_id]['nsmap'][ns_code] = ns_link


def save_file_message_ns(file_id: str, message_ns: str):
    DATABASE['files'][file_id]['message_ns'] = message_ns


def get_file_message_ns(file_id: str):
    return DATABASE['files'][file_id]['message_ns']


def save_file_feature(file_id: str,  feature: AIXMFeature):
    DATABASE['files'][file_id]['features'][feature.uuid] = feature


def get_file_feature(file_id: str, uuid: str):
    feature = DATABASE['files'][file_id]['features'].get(uuid)

    if feature is None:
        raise ValueError("Feature not found")

    return feature


def get_file_features_dict(file_id: str):
    return DATABASE['files'][file_id]['features']


def get_file_features_gen(file_id: str):
    return (feature for _, feature in DATABASE['files'][file_id]['features'].items())


def filter_file_features(file_id: str, name: str, key: Optional[str] = None):
    features = (feature for feature in get_file_features_gen(file_id) if feature.el.name == name)

    if key:
        features = (feature for feature in features if feature.filter_by_key(key))

    return features


def save_file_stats(file_id, stats: Dict):
    DATABASE['files'][file_id]['stats'] = stats
