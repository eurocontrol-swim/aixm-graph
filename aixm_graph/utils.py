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

import math
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Tuple, Union, List

import yaml
from lxml import etree
from lxml.builder import ElementMaker
from lxml.etree import QName


def get_current_dir() -> str:
    return Path(__file__).parent.as_posix()


def get_samples_filepath(filename):
    samples_dir = Path(__file__).parent.parent.joinpath('samples').as_posix()

    return Path(samples_dir).joinpath(filename).absolute().as_posix()


def parse_element_tag(element: etree.Element) -> Tuple[str, str]:
    q = QName(element)

    return q.localname, q.namespace


def get_tag_without_ns(element: etree.Element):
    tag, _ = parse_element_tag(element)

    return tag


def get_attrib_value(attribs: Dict[str, str], name: str, ns: str, value_prefixes: Optional[List[str]] = None):
    value_prefixes = value_prefixes or []
    result = attribs[f'{{{ns}}}{name}']

    for value_prefix in value_prefixes:

        if result.startswith(value_prefix):
            result = result[len(value_prefix):]
            break

    return result


def parse_element(element: etree.Element) -> Dict[str, str]:
    tag, ns = parse_element_tag(element)

    return dict(name=tag, value=element.text, attrib=element.attrib, ns=ns)


mxiaElementMaker = ElementMaker(namespace="http://www.aixm.aero/schema/5.1.1/extensions/mxia",
                                nsmap={
                                    "mxia": "http://www.aixm.aero/schema/5.1.1/extensions/mxia",
                                    "xlink": "http://www.w3.org/1999/xlink",
                                    "gml": "http://www.opengis.net/gml/3.2",
                                })


def make_attrib(name, value, ns):
    return {f'{{{ns}}}{name}': value}


def timeit(func):
    def decorator(*args, **kwargs):
        s = datetime.now()
        result = func(*args, **kwargs)
        e = datetime.now()
        print(e - s)
        return result
    return decorator


def load_config(filename: str):

    with open(filename) as f:
        obj = yaml.load(f, Loader=yaml.FullLoader)

    return obj or None


def convert_size(size_bytes):
   if size_bytes == 0:
       return "0B"
   size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
   i = int(math.floor(math.log(size_bytes, 1024)))
   p = math.pow(1024, i)
   s = round(size_bytes / p, 2)
   return "%s %s" % (s, size_name[i])
