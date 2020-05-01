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

from copy import deepcopy
from typing import Dict, Optional

from lxml import etree
from lxml.etree import QName

from aixm_graph.utils import get_attrib_value, make_attrib, element_without_namespace
from aixm_graph import XLINK_NS, GML_NS


class Field:

    def __init__(self,
                 name: str,
                 text: Optional[str] = None,
                 attrib: Optional[Dict[str, str]] = None,
                 prefix: Optional[str] = None) -> None:
        """
        The purpose of this class is to keep the essential information of an `etree.Element`.
        The namespace information is discarded because it is repeated in all the `etree.Element`
        instances of a parsed file, thus not redundant memory is used.

        Additionally the `attrib` attribute is deep copied (below) in order to avoid keeping
        reference to it and consequently to the parent element. All those elements are supposed to
        be deleted by the parser `server.datasets.AIXMDataSet.parse` after having been read in order
        to avoid memory overflow in case of huge files with thousands of elements.

        :param name:
        :param text:
        :param attrib:
        :param prefix:
        """
        self.name = name
        self.text = text or ""
        self.attrib = deepcopy(attrib) if attrib else {}
        self.prefix = prefix or ""

    @classmethod
    def from_lxml(cls, element: etree.Element):
        """

        :param element:
        :return: Field
        """
        return cls(name=QName(element).localname,
                   text=element.text,
                   attrib=element.attrib,
                   prefix=element.prefix)

    def to_lxml(self, nsmap: Dict[str, str], **kwargs) -> etree.Element:
        """

        :param nsmap: the nsmap of the dataset
        :return:
        """
        ns = nsmap.get(self.prefix)
        ns = f"{{{ns}}}" if ns else ""

        tag = f'{ns}{self.name}'
        el = etree.Element(tag, attrib=self.attrib, nsmap=nsmap)
        el.text = self.text

        return el


class XLinkField(Field):
    prefixes = ('urn:uuid:', 'urn:uuid.', 'uuid.', '#',)

    def __init__(self, **kwargs) -> None:
        """
        Holds info for elements with xlink:href attributes
        :param kwargs:
        """
        super().__init__(**kwargs)
        self._href = None
        self._title = None
        self._broken = False

    @property
    def is_broken(self):
        return self._broken

    def set_broken(self) -> None:
        self._broken = True

    @property
    def href(self) -> str:
        if self._href is None:
            self._href = get_attrib_value(
                self.attrib, name='href', ns=XLINK_NS, value_prefixes=self.prefixes)

        return self._href

    @property
    def title(self) -> str:
        if self._title is None:
            self._title = get_attrib_value(
                self.attrib, name='title', ns=XLINK_NS)

        return self._title or ''


class Extension(Field):

    @classmethod
    def create(cls, name: str, href: str, prefix: str):
        """

        :param name:
        :param href:
        :param prefix:
        :return: Extension
        """
        extension = cls(name=name,
                        attrib=make_attrib(name='href', value=f"urn:uuid:{href}", ns=XLINK_NS),
                        prefix=prefix)
        extension.href = href

        return extension
