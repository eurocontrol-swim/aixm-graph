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

import pytest
from pkg_resources import resource_filename

from aixm_graph.datasets.datasets import AIXMDataSet

TEST_FILENAME = 'dataset.xml'
SKELETON_FILENAME = 'skeleton.xml'


@pytest.fixture
def test_filepath():
    return resource_filename(__name__, f'../../static/{TEST_FILENAME}')


@pytest.fixture
def test_skeleton_path():
    return resource_filename(__name__, f'../../static/{SKELETON_FILENAME}')


def test_dataset__name(test_filepath):
    dataset = AIXMDataSet(test_filepath)

    assert TEST_FILENAME == dataset.name


def test_dataset__process__features_are_retrieved(test_filepath, test_config):
    dataset = AIXMDataSet(test_filepath)

    dataset.process()

    features = list(dataset.features)

    assert len(features) > 0

    for feature_name in test_config['FEATURES']:
        assert feature_name in [f.name for f in features]


def test_dataset__generate_skeleton(test_filepath, test_skeleton_path, test_config):
    dataset = AIXMDataSet(test_filepath)

    dataset.process()

    skeleton_path = dataset.generate_skeleton()

    assert os.path.exists(skeleton_path)

    with open(skeleton_path, 'r') as skeleton:
        with open(test_skeleton_path, 'r') as test_skeleton:
            assert skeleton.read() == test_skeleton.read()

    os.remove(skeleton_path)
