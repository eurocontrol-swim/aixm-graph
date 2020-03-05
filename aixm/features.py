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

from abc import ABC, abstractmethod
from copy import deepcopy
from typing import Optional, Dict, List

from lxml import etree
from lxml.etree import QName

from aixm.utils import get_attrib_value, get_tag_without_ns, make_attrib


class XMLSerializable(ABC):
    prefix = None

    @abstractmethod
    def to_lxml(self, nsmap: Dict[str, str]):
        pass


class Element(XMLSerializable):

    def __init__(self,
                 name: str,
                 text: Optional[str] = None,
                 attrib: Optional[Dict[str, str]] = None,
                 prefix: Optional[str] = None) -> None:
        self.name = name
        self.text = text or ""
        self.attrib = deepcopy(attrib) if attrib else {}
        self.prefix = prefix or ""

    @staticmethod
    def parse_element(element: etree.Element) -> Dict:
        q = QName(element)

        return dict(name=q.localname, text=element.text, attrib=element.attrib, prefix=element.prefix)

    @classmethod
    def from_lxml(cls, element: etree.Element):
        return cls(**cls.parse_element(element))

    def to_lxml(self, nsmap: Dict[str, str]) -> etree.Element:
        ns = nsmap.get(self.prefix)
        ns = f"{{{ns}}}" if ns else ""

        tag = f'{ns}{self.name}'
        el = etree.Element(tag, attrib=self.attrib, nsmap=nsmap)
        el.text = self.text

        return el


class Link:

    def __init__(self, uuid: str, name: str):
        pass


class XLinkElement(Element):

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.uuid = None

    @classmethod
    def from_lxml(cls, element: etree.Element):
        obj = cls(**cls.parse_element(element))
        obj.uuid = get_attrib_value(element.attrib,
                                    name='href',
                                    ns=element.nsmap["xlink"],
                                    value_prefixes=['urn:uuid:', 'urn:uuid.', 'uuid.'])

        return obj


class Extension(XMLSerializable):
    prefix = 'mxia'

    def __init__(self, name: str, uuid: str):
        self.name = name
        self.uuid = uuid

    def to_lxml(self, nsmap: Dict[str, str]):
        ns = nsmap.get(self.prefix)
        ns = f"{{{ns}}}" if ns else ""

        attrib = make_attrib(name='href', value=f"urn:uuid:{self.uuid}", ns=nsmap['xlink'])

        tag = f'{ns}{self.name}'
        el = etree.Element(tag, attrib=attrib, nsmap=nsmap)

        return el


class FeatureData:

    def __init__(self, element: etree.Element, keys: List):
        self.el = Element.from_lxml(element)

        self.key_elements: List[Element] = self._retrieve_keys(element, keys)
        self.xlinks: List[XLinkElement] = self._retrieve_xlinks(element)
        self.broken_xlinks: List[XLinkElement] = []
        self.extensions: List[Extension] = []

    @property
    def keys(self):
        return [{key.name: key.text} for key in self.key_elements]

    def links(self):
        return self.xlinks + self.extensions

    def props(self):
        return self.key_elements + self.links()

    def has_broken_xlinks(self):
        return len(self.broken_xlinks) > 0

    @staticmethod
    def _retrieve_keys(element: etree.Element, keys: List[str]) -> List[Element]:
        return [Element.from_lxml(child) for child in element if get_tag_without_ns(child) in keys]

    def _retrieve_xlinks(self, element: etree.Element) -> List[XLinkElement]:
        xlinks = element.findall('.//*[@xlink:href]', namespaces=element.nsmap)

        return [XLinkElement.from_lxml(self.process_xlink_element(xlink, element)) for xlink in xlinks]

    def process_xlink_element(self, xlink: etree.Element, root: Optional[etree.Element] = None) -> etree.Element:
        return xlink

    def add_extension(self, extension: Extension):
        self.extensions.append(extension)

    def to_lxml(self, nsmap: Dict[str, str]) -> etree.Element:
        root = self.el.to_lxml(nsmap)
        for prop in self.props():
            root.append(prop.to_lxml(nsmap))

        return root


class Feature:

    def __init__(self, element: etree.Element, keys: Dict, abbrev: str):
        self.el = Element.from_lxml(element)

        self.keys_concat = keys.get('concat', False)
        self.uuid: str = element.find('./gml:identifier', element.nsmap).text
        self.id: str = get_attrib_value(element.attrib, name='id', ns=element.nsmap["gml"], value_prefixes=['uuid.'])
        self.abbrev = abbrev

        feature_data_elements = element.findall(self.get_feature_data_xpath(), namespaces=element.nsmap)

        self.feature_data = [
            self.get_feature_data_class()(element=feature_data_element, keys=keys['properties'] or [])
            for feature_data_element in feature_data_elements
        ]

    def has_broken_xlinks(self):
        return any([data.has_broken_xlinks() for data in self.feature_data])

    def get_feature_data_xpath(self):
        return ""

    def get_feature_data_class(self):
        return FeatureData

    def __hash__(self):
        return hash(self.uuid)


class AIXMFeatureData(FeatureData):

    def __init__(self, element: etree.Element, keys: List):
        self.sequence_number = element.find('./aixm:sequenceNumber', namespaces=element.nsmap).text
        try:
            self.correction_number = element.find('./aixm:correctionNumber', namespaces=element.nsmap).text
        except AttributeError:
            self.correction_number = ""

        super().__init__(element, keys)

    @property
    def name(self):
        return ",".join([self.sequence_number, self.correction_number]) if self.correction_number \
            else self.sequence_number

    def process_xlink_element(self, xlink: etree.Element, root: Optional[etree.Element] = None) -> etree.Element:

        if xlink.getparent() != root:
            xlink = self.process_nested_xlink_element(xlink)

        return xlink

    def process_nested_xlink_element(self, xlink: etree.Element):
        if get_tag_without_ns(xlink).startswith('the'):
            xlink = self.process_associated_xlink(xlink)

        return xlink

    @staticmethod
    def process_associated_xlink(xlink: etree.Element) -> etree.Element:
        tags = [xlink.getparent().getparent().tag]

        tags.extend([el.text for el in xlink.getparent() if el != xlink and len(el) == 0])

        return etree.Element("_".join(tags), attrib=xlink.attrib, nsmap=xlink.nsmap)


class AIXMFeature(Feature):

    def get_feature_data_xpath(self):
        return f'./aixm:timeSlice/aixm:{self.el.name}TimeSlice'

    def get_feature_data_class(self):
        return AIXMFeatureData
