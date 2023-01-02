from generative_notch.dfx.dom_element_wrapper import DomElementWrapper
from generative_notch.dfx.node import Node, NodeNotFound


class LayerNotFound(Exception):
	"""Raised when layer element was not found"""
	pass


class Layer(DomElementWrapper):
	"""
	Allow manipulation of Layer elements.\n
	Contains references to child nodes.\n

	XML representation of the element:\n
	<Layer name="Layer 1" expanded="0" visible="1" solo="1" guid="..." colour="8881538">
	"""
	def __init__(self, dom):
		super().__init__(dom)

		self.nodes = [Node(element) for element in dom.getElementsByTagName('Effect')]

	def node(self, name) -> Node:
		"""Fetches node by name. If more than one node found, will return first occurrence.

		:param name: name of node
		:return: requested node if found
		:raises NodeNotFound: if found no node with given name
		"""
		for node in self.nodes:
			if node.get_attribute('name') == name:
				return node

		raise NodeNotFound(name)
