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

from unittest import mock

import pytest

from aixm_graph.config import parse_feature_config, parse_features_config


@pytest.fixture(scope='function')
def feature_config():
    return {
        "abbrev": "AGL",
        "color": "#efdecd",
        "shape": "square",
        "fields": {
            "names": [
                "type",
                "name"
            ]
        }
    }


def test_parse_feature_config__invalid_attribute(feature_config):
    invalid_attr = 'invalid'
    feature_config[invalid_attr] = {}

    with pytest.raises(ValueError) as e:
        parse_feature_config(feature_config)

    assert f"Invalid config attribute '{invalid_attr}'" == str(e.value)


def test_parse_feature_config__invalid_shape(feature_config):
    feature_config['shape'] = 'invalid_shape'

    with pytest.raises(ValueError) as e:
        parse_feature_config(feature_config)

    assert f"Invalid shape value: 'invalid_shape'" == str(e.value)


@pytest.mark.parametrize('abbrev', [
    'A', 'AA', 'AAAA',
])
def test_parse_feature_config__invalid_abbrev_length(feature_config, abbrev):
    feature_config['abbrev'] = abbrev

    with pytest.raises(ValueError) as e:
        parse_feature_config(feature_config)

    assert f"abbrev should be 3 characters long" == str(e.value)


@pytest.mark.parametrize('color', [
    '#',
    '#a',
    '#a2',
    '#a2e',
    '#a2e7',
    '#a2e7c',
    '#1a2a3r',
    '@a2b3d4',
])
def test_parse_feature_config__invalid_abbrev_length(feature_config, color):
    feature_config['color'] = color

    with pytest.raises(ValueError) as e:
        parse_feature_config(feature_config)

    assert f"Invalid color value: '{color}'" == str(e.value)


@pytest.mark.parametrize('incomplete_fields, expected_fields', [
    ({}, {'concat': False, 'names': []}),
    ({'concat': True}, {'concat': True, 'names': []}),
    ({'names': ['name']}, {'concat': False, 'names': ['name']}),
])
def test_parse_feature_config__incomplete_fields_attr_is_completed(
        feature_config, incomplete_fields, expected_fields):
    feature_config['fields'] = incomplete_fields

    parse_feature_config(feature_config)

    assert expected_fields == feature_config['fields']


@mock.patch('aixm_graph.config.parse_feature_config')
def test_parse_features_config__parsing_error_raises_valueerror(
        mock_parse_feature_config, test_features_config):

    mock_parse_feature_config.side_effect = ValueError('error')

    with pytest.raises(ValueError):
        parse_features_config(test_features_config)


def test_parse_features_config__no_errors(test_features_config):
    assert test_features_config == parse_features_config(test_features_config)
