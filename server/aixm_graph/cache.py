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

import uuid
from typing import List

from aixm_graph.datasets.datasets import AIXMDataSet

CACHE = {
    'datasets': {}
}


def create_dataset(filepath: str) -> AIXMDataSet:
    """

    :param dataset:
    :return:
    """
    global CACHE
    dataset = AIXMDataSet(filepath)
    dataset.id = uuid.uuid4().hex[:6]

    CACHE['datasets'][dataset.id] = dataset

    return CACHE['datasets'][dataset.id]


def get_dataset_by_id(dataset_id: str) -> AIXMDataSet:
    """

    :param dataset_id:
    :return:
    """
    return CACHE['datasets'].get(dataset_id)


def get_dataset_by_name(name: str) -> AIXMDataSet:
    """

    :param name:
    :return:
    """
    for _, dataset in CACHE['datasets'].items():
        if dataset.name == name:
            return dataset


def get_datasets() -> List[AIXMDataSet]:
    """

    :return:
    """
    return list(CACHE['datasets'].values())
