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

from typing import Optional, Dict, List

import yaml


def get_attrib_value(attribs: Dict[str, str], name: str, ns: str, value_prefixes: Optional[List[str]] = None):
    value_prefixes = value_prefixes or []
    result = attribs[f'{{{ns}}}{name}']

    for value_prefix in value_prefixes:
        if result.startswith(value_prefix):
            result = result[len(value_prefix):]
            break

    return result


def make_attrib(name, value, ns):
    return {f'{{{ns}}}{name}': value}


def load_config(filename: str):

    with open(filename) as f:
        obj = yaml.load(f, Loader=yaml.FullLoader)

    return obj or None


def get_next_offset(offset, limit, size):
    """

    :param offset:
    :param limit:
    :param size:
    :return:
    """
    next_offset = offset + limit
    if next_offset >= size or size <= limit :
        return

    return next_offset


def get_prev_offset(offset, limit, size):
    """

    :param offset:
    :param limit:
    :param size:
    :return:
    """
    pref_offset = offset - limit

    if pref_offset >= 0:
        return pref_offset


def validate_file_form(file_form: Dict):
    """

    :param file_form:
    :return:
    """
    if 'file' not in file_form:
        raise ValueError('No file part')

    file = file_form['file']
    if file.filename == '' or file.filename is None:
        raise ValueError('No selected file')

    if not filename_is_valid(file.filename):
        raise ValueError('File is not allowed')

    return file


def filename_is_valid(filename):
    """

    :param filename:
    :return:
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() == 'xml'
