from xml.dom.minidom import Element
import logging


class AttributeNotFount(Exception):
	"""Raised when attribute is not found"""
	pass


class DomElementWrapper:
	"""Minimal wrapped for DOM Element needed to easily modify DFX script"""
	def __init__(self, dom: Element):
		self._dom = dom

	def get_attribute(self, name: str) -> str:
		"""Returns attribute value

		Attribute in case of DFX script is f.e. name, expanded, visible in XML element:\n
		<Layer name="Layer 1" expanded="0" visible="1" solo="1" guid="..." colour="8881538">

		:param name: name of the attribute
		:raises AttributeNotFount:
		:return: value of the attribute
		"""
		try:
			return self._dom.getAttribute(name)
		except KeyError:
			raise AttributeNotFount(name)

	def set_attribute(self, name: str, value):
		"""Sets value of an attribute

		Attribute in case of DFX script is f.e. name, expanded, visible in XML element:\n
		<Layer name="Layer 1" expanded="0" visible="1" solo="1" guid="..." colour="8881538">

		:param name: name of the attribute
		:param value: value to set, will be converted to string
		:raises AttributeNotFount:
		"""
		if not self._dom.hasAttribute(name):
			raise AttributeNotFount(name)

		logging.debug(f'Setting attribute [{self._dom.tagName}: {name}] value to {str(value)}')
		self._dom.setAttribute(name, str(value))
