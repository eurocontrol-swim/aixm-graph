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

import io
from typing import Optional, Dict, List, Any, Iterable

import yaml
from lxml import etree


def get_attrib_value(attribs: Dict[str, str],
                     name: str,
                     ns: str,
                     value_prefixes: Optional[Iterable[str]] = None) -> Optional[str]:
    """
    Retrieves the value of an attribute from a dict of `etree.Element` attributes based on its name
    and namespace. The value could be prefixed by any string so it has to be provided in order to
    not be considered in the returned value.

    :param attribs:
    :param name:
    :param ns: namespace
    :param value_prefixes:
    :return:
    """
    value_prefixes = value_prefixes or []
    result = attribs.get(f'{{{ns}}}{name}')

    if result is None:
        return

    for value_prefix in value_prefixes:
        if result.startswith(value_prefix):
            result = result[len(value_prefix):]
            break

    return result


def make_attrib(name: str, value: str, ns: str) -> Dict[str, str]:
    """
    Creates a dict entry to be added im the attribs of a `etree.Element`
    :param name:
    :param value:
    :param ns:
    :return:
    """
    return {f'{{{ns}}}{name}': value}


def load_config(filename: str) -> Dict[str, Any]:
    """
    Parses a YAML file and returns a dict of its content
    :param filename:
    :return:
    """
    with open(filename) as f:
        obj = yaml.load(f, Loader=yaml.FullLoader)

    return obj or None


def get_next_offset(offset, limit, size):
    """
    Calculates the next offset value provided the current one as well as the page limit and the
    total size of the items
    :param offset:
    :param limit:
    :param size:
    :return:
    """
    next_offset = offset + limit
    if next_offset >= size or size <= limit :
        return

    return next_offset


def get_prev_offset(offset, limit):
    """
    Calculates the previous offset value provided the current one and the page limit

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


def element_without_namespace(element: etree.Element) -> etree.Element:
    """
    http://wiki.tei-c.org/index.php/Remove-Namespaces.xsl

    :param element:
    """
    xslt = b'''<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <xsl:output method="xml" indent="no"/>

    <xsl:template match="/|comment()|processing-instruction()">
        <xsl:copy>
          <xsl:apply-templates/>
        </xsl:copy>
    </xsl:template>

    <xsl:template match="*">
        <xsl:element name="{local-name()}">
          <xsl:apply-templates select="@*|node()"/>
        </xsl:element>
    </xsl:template>

    <xsl:template match="@*">
        <xsl:attribute name="{local-name()}">
          <xsl:value-of select="."/>
        </xsl:attribute>
    </xsl:template>
    </xsl:stylesheet>
    '''

    xslt_doc = etree.parse(io.BytesIO(xslt))
    transform = etree.XSLT(xslt_doc)

    return transform(element)
