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

import re
from typing import Dict


ATTRIBUTES = ('abbrev', 'fields', 'color', 'shape',)
SHAPES = ('dot', 'triangle', 'triangleDown', 'box', 'square', 'diamond', 'hexagon', 'ellipse',
          'image')

COLOR_RE = re.compile('^#[\da-fA-F]{6}$')


def parse_features_config(features_config: Dict) -> Dict:
    for feature, feature_config in features_config.items():
        try:
            parse_feature_config(feature_config)
        except ValueError as e:
            raise ValueError(f'Error while parsing {feature} config: {str(e)}')

    return features_config


def parse_feature_config(feature_config: Dict) -> None:
    """

    :param feature_config:
    :return:
    """

    for name, value in feature_config.items():
        if name not in ATTRIBUTES:
            raise ValueError(f"Invalid config attribute '{name}'")

        if name == 'shape' and value not in SHAPES:
            raise ValueError(f"Invalid shape value: '{value}'")

        if name == 'abbrev' and len(value) != 3:
            raise ValueError('abbrev should be 3 characters long')

        if name == 'color' and COLOR_RE.match(value) is None:
            raise ValueError(f"Invalid color value: '{value}'")

        # assign default values on fields' non-required attributes in case they're omitted
        if name == 'fields':
            value['concat'] = value.get('concat', False)
            value['names'] = value.get('names') or []
