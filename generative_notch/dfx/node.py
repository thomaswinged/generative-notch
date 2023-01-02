from generative_notch.dfx.dom_element_wrapper import DomElementWrapper
from xml.dom.minidom import Element
import logging


class NodePropertyGroupNotFound(Exception):
	"""Raised when property group of a node was not found"""
	pass


class NodePropertyNotFound(Exception):
	"""Raised when property name of a node was not found"""
	pass


class NodeProperty:
	"""Property of a node (Effect), operates only on 'value' attribute.\n

	XML representation of the element:\n
	<PRP name="Backdrop Glow" propertyType="1" numChannels="1" locked="0" groupVisible="0" value="0.000000"></PRP>
	"""
	def __init__(self, prop: Element):
		self._dom = prop

	def set(self, value):
		"""Sets the value of a property in a safe way (converts to string).

		:param value: Value to be set
		"""
		parent_node_name = self.__get_parent_node().getAttribute('name')
		property_name = f"{self.__get_group().getAttribute('name')}: {self._dom.getAttribute('name')}"
		logging.debug(f"Setting node's [{parent_node_name}] property [{property_name}] value to {str(value)}")

		self._dom.attributes['value'].value = str(value)

	def get(self) -> str:
		"""Gets the value of the property

		:return: property's value
		"""
		return self._dom.attributes['value'].value

	def __get_parent_node(self) -> Element:
		return self._dom.parentNode.parentNode.parentNode

	def __get_group(self) -> Element:
		return self._dom.parentNode

class NodeNotFound(Exception):
	"""Raised when node (Effect) element was not found"""
	pass


class Node(DomElementWrapper):
	"""
	Allows manipulation of Effect elements.\n
	I am calling this class Node (common speech), but in fact it's called Effect inside Demolition.script\n

	XML representation of the element:\n
	<Effect classId="..." expanded="0" thumbExpanded="0" visible="1" name="$F_Envelope1" guid="..."
	displayGroupKey="0" rect="1280 512 1410 534" colour="48127" keyframeColour="48127" barMinimised="0" >
	"""

	def __init__(self, dom):
		super().__init__(dom)

	def property(self, group_name: str, prop_name: str) -> NodeProperty:
		"""Fetches property of a node.

		:param group_name: name of a group of properties (f.e. Transform)
		:param prop_name: name of a property (f.e. Position X)
		:return: requested property if found
		:raises PropertyGroupNotFound: if property group was not found
		:raises PropertyNotFound: if property name was not found
		"""
		group_found = False
		for group in self._dom.getElementsByTagName('PropertyManager')[0].getElementsByTagName('GRP'):
			if group.attributes['name'].value == group_name:
				group_found = True
				for prop in group.getElementsByTagName('PRP'):
					if prop.attributes['name'].value == prop_name:
						return NodeProperty(prop)

		if not group_found:
			raise NodePropertyGroupNotFound(group_name)
		raise NodePropertyNotFound(prop_name)
