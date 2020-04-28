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

from typing import Dict, Tuple, List, Type, TypeVar

from lxml import etree
from lxml.etree import QName

from aixm_graph.datasets.fields import Field, XLinkField, Extension
from aixm_graph.utils import get_attrib_value, make_attrib


class Feature(Field):
    config = {}

    def __init__(self, *args, **kwargs):
        """
        Feature holds the information found in a single version (time slice for AIXM) feature
        element.
        :param args:
        :param kwargs:
        """
        super().__init__(*args, **kwargs)

        self.id = None

        self._data_fields: List[Field] = []
        self._xlinks: List[XLinkField] = []
        self._extensions: List[Extension] = []

    def add_extension(self, extension: Extension):
        """

        :param extension:
        """
        self._extensions.append(extension)

    @property
    def data_fields(self) -> List[Field]:
        return self._data_fields

    @property
    def xlinks(self) -> List[XLinkField]:
        return self._xlinks

    @property
    def extensions(self) -> List[Extension]:
        return self._extensions

    @property
    def associations(self) -> List[Field]:
        return self.xlinks + self.extensions

    @property
    def has_broken_xlinks(self) -> bool:
        return any(xlink.is_broken for xlink in self._xlinks)

    def matches_field_value(self, filter_key: str) -> bool:
        return any(filter_key.lower() in field.text.lower() for field in self.data_fields)


class AIXMFeature(Feature):

    def __init__(self, *args, **kwargs):
        """
        Represents a feature element as it is found in an AIXM dataset. The information is
        encaptulated in one or more time slices which serve as different versions of the feature.
        """
        super().__init__(*args, **kwargs)

        # the time slice of an AIXM feature is treated as a feature version of it, thus a feature
        # keeps all its versions in a dict
        self.time_slices: Dict[str, Feature] = {}
        self.gml_identifier = None

    @property
    def data_fields(self) -> List[Field]:
        return [field for ts in self.time_slices.values() for field in ts.data_fields]

    @property
    def xlinks(self) -> List[XLinkField]:
        return [xlink for ts in self.time_slices.values() for xlink in ts.xlinks]

    @property
    def extensions(self) -> List[Extension]:
        return [extension for ts in self.time_slices.values() for extension in ts.extensions]

    @property
    def has_broken_xlinks(self) -> bool:
        return any(ts.has_broken_xlinks for _, ts in self.time_slices.items())

    def add_extension(self, extension: Extension):
        """
        Adds the extension to all the versions (time slices) of self
        :param extension:
        """
        for _, ts in self.time_slices.items():
            ts.add_extension(extension)

    def matches_field_value(self, filter_key: str) -> bool:
        return any(ts.matches_field_value(filter_key) for _, ts in self.time_slices.items())

    def to_lxml(self, nsmap: Dict[str, str]) -> etree.Element:
        """

        :param nsmap:
        :return:
        """
        root = etree.Element(f"{{{nsmap[self.prefix]}}}{self.name}",
                             attrib=make_attrib(name='id',
                                                value=f"urn:uuid:{self.id}",
                                                ns=nsmap['gml']),
                             nsmap=nsmap)

        identifier = etree.Element(f"{{{nsmap['gml']}}}identifier",
                                   attrib=make_attrib(name='codeSpace', value="urn:uuid:", ns=""),
                                   nsmap=nsmap)

        identifier.text = self.gml_identifier
        root.append(identifier)

        for ts in self.time_slices.values():
            ts_root = ts.to_lxml(nsmap)

            for field in (ts.data_fields + ts.xlinks):
                ts_root.append(field.to_lxml(nsmap))

            for extension in ts.extensions:
                inner_el = extension.to_lxml(nsmap)
                outer_el = etree.Element(f"{{{nsmap[extension.prefix]}}}{self.name}Extension")
                wrapper = etree.Element(f"{{{nsmap[self.prefix]}}}extension")

                outer_el.append(inner_el)
                wrapper.append(outer_el)
                ts_root.append(wrapper)

            time_slice_container = etree.Element(f"{{{nsmap[ts.prefix]}}}timeSlice", nsmap=nsmap)
            time_slice_container.append(ts_root)

            root.append(time_slice_container)

        return root


FeatureType = TypeVar('FeatureType', bound=Feature)


class AIXMFeatureFactory:

    @staticmethod
    def feature_from_sequence_element(seq_element: etree.Element) -> AIXMFeature:
        """
        Creates an AIXMFeature from a sequence element as it is read from the parser.

        :param seq_element: For AIXM datasets the sequence element is `hasMember`
        """

        # in AIXM files the feature is the first child of the <hasMember> sequence element
        feature_element = seq_element[0]

        feature_class = AIXMFeatureClassRegistry.get_feature_class(QName(feature_element).localname)

        feature = feature_class.from_lxml(feature_element)

        feature.id = feature_element.find('./gml:identifier', feature_element.nsmap).text
        feature.gml_identifier = get_attrib_value(feature_element.attrib,
                                                  name='id',
                                                  ns=feature_element.nsmap["gml"],
                                                  value_prefixes=['uuid.'])

        time_slice_elements = feature_element.findall(AIXMFeatureFactory.get_time_slice_xpath(feature),
                                                      namespaces=feature_element.nsmap)

        for element in time_slice_elements:
            version, time_slice = AIXMFeatureFactory.time_slice_from_element(
                element=element, field_names=feature.config['fields']['names'])
            feature.time_slices[version] = time_slice

        return feature

    @staticmethod
    def time_slice_from_element(element: etree.Element,
                                field_names: List[str]) -> Tuple[str, Feature]:
        """

        :param field_names:
        :param element:
        :return:
        """
        time_slice = Feature.from_lxml(element)

        time_slice._data_fields = [
            Field.from_lxml(child)
            for child in element
            if QName(child).localname in field_names
        ]

        time_slice._xlinks = [
            XLinkField.from_lxml(
                AIXMFeatureFactory.process_xlink_element(xlink=xlink, ts_element=element)
            )
            for xlink in element.findall('.//*[@xlink:href]', namespaces=element.nsmap)
        ]

        version = AIXMFeatureFactory.get_time_slice_element_version(element, time_slice.prefix)

        return version, time_slice

    @staticmethod
    def get_time_slice_xpath(feature: AIXMFeature) -> str:
        """

        :param feature:
        :return:
        """
        return f'./{feature.prefix}:timeSlice/{feature.prefix}:{feature.name}TimeSlice'

    @staticmethod
    def get_time_slice_element_version(element: etree.Element, prefix: str) -> str:
        """
        The version name of the element if composed by the value of the `sequenceNumber` and/or
        the value of the `correctionNumber`

        :param element:
        :param prefix:
        :return:
        """
        sequence_number = element.find(f'./{prefix}:sequenceNumber', namespaces=element.nsmap).text

        try:
            correction_number = element.find(f'./{prefix}:correctionNumber',
                                             namespaces=element.nsmap).text
        except AttributeError:
            correction_number = ""

        return ",".join([sequence_number, correction_number]) if correction_number \
            else sequence_number

    @staticmethod
    def process_xlink_element(xlink: etree.Element, ts_element: etree.Element) -> etree.Element:
        """
        Applies custom processing to elements with xlink:href attribute.

        :param xlink:
        :param ts_element: The timeSlice element where the element with xlink:href attribute was
                           found
        :return:
        """
        if xlink.getparent() != ts_element:
            xlink = AIXMFeatureFactory.process_nested_xlink_element(xlink)

        return xlink

    @staticmethod
    def process_nested_xlink_element(xlink: etree.Element):
        """
        Applies custom processing to elements with xlink:href attribute that were found deeper in a
        timeSlice.
        :param xlink:
        :return:
        """
        if QName(xlink).localname.startswith('the'):
            xlink = AIXMFeatureFactory.process_associated_xlink(xlink)

        return xlink

    @staticmethod
    def process_associated_xlink(xlink: etree.Element) -> etree.Element:
        """
        Applies custom processing for elements with xlink:href attributes that are considered as
        associated i.e. their name starts with `the`

        Example:

        The below original element has a nested element (theNavaidEquipment) with xlink:href
        attribute which is associated. After processing the element's name will be appended with the
        text values of its parent's siblings and this is how it will be kept and later generated in
        the skeleton file.

        Original:

        <aixm:navaidEquipment>
            <aixm:NavaidComponent gml:id="N-a8e60416">
                <aixm:collocationGroup>1</aixm:collocationGroup>
                <aixm:theNavaidEquipment
                    xlink:href="urn:uuid:13fe226f-271c-4d36-9f42-190563a963de"/>
            </aixm:NavaidComponent>
        </aixm:navaidEquipment>

        In skeleton after processing:

        <aixm:navaidEquipment_1 xlink:href="urn:uuid:13fe226f-271c-4d36-9f42-190563a963de"/>

        :param xlink:
        :return:
        """
        tags = [xlink.getparent().getparent().tag]

        tags.extend([el.text or "" for el in xlink.getparent() if el != xlink and len(el) == 0])

        return etree.Element("_".join(tags), attrib=xlink.attrib, nsmap=xlink.nsmap)


class AIXMFeatureClassRegistry:
    """It parses the config file and creates classes for each feature type encapsulating the values
       of the config file for later use.
    """
    feature_config_attrs = ('abbrev', 'fields', 'color', 'shape',)
    feature_classes: Dict[str, FeatureType] = {}

    @classmethod
    def load_feature_classes(cls, config: Dict) -> None:
        """

        :param config:
        """
        for feature_name, config_data in config.items():
            try:
                data = {
                    'config': cls.validate_config(config_data),
                }
                feature_class = type(feature_name, (AIXMFeature,), data)
                cls.feature_classes[feature_class.__name__] = feature_class
            except ValueError as e:
                raise ValueError(f"Config validation error for {feature_name}: {str(e)} ")

    @classmethod
    def validate_config(cls, config: Dict) -> Dict:
        """

        :param config:
        :return:
        """
        for name, value in config.items():
            if name not in cls.feature_config_attrs:
                raise ValueError(f"Missing config attribute '{name}'")

            # assign default values on fields' non-required attributes in case they're omitted
            if name == 'fields':
                value['concat'] = value.get('concat', False)
                value['names'] = value.get('names') or []

        return config

    @classmethod
    def get_feature_class(cls, feature_name: str) -> Type[AIXMFeature]:
        """

        :param feature_name:
        :return:
        """
        return cls.feature_classes.get(feature_name)
