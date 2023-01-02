from generative_notch.dfx.dom_element_wrapper import DomElementWrapper
from generative_notch.dfx.layer import Layer, LayerNotFound
from generative_notch.dfx.render_queue import RenderQueue


class DemolitionScript(DomElementWrapper):
	"""
	Root of DFX script (Demolition.script) file.\n
	Contains references to Layers and Render Queue.\n

	XML representation of the element:\n
	<Demolition version="1" isCompiledProject="0" build="0.9.23.219 : BASE" timeBase="6000" >
	"""

	def __init__(self, dom):
		super().__init__(dom)

		self.layers = [Layer(element) for element in dom.getElementsByTagName('Layer')]
		self.render_queue = RenderQueue(dom.getElementsByTagName('RenderQueue')[0])

	def layer(self, name_or_id) -> Layer:
		"""Fetches layer by id or name. Use either ID or name.

		:param name_or_id: ID or name of layer
		:return: requested layer
		:raises LayerNotFound: when no layer with requested id/name exists
		:raises ValueError: when passed an unsupported value type
		"""
		if type(name_or_id) == str:
			for layer in self.layers:
				if layer.get_attribute('name') == name_or_id:
					return layer

			raise LayerNotFound(f'Name: {name_or_id}')
		elif type(name_or_id) == int:
			if 0 <= name_or_id < len(self.layers):
				return self.layers[name_or_id]

			raise LayerNotFound(f'ID: {name_or_id}')
		raise ValueError('Invalid type of layer id/name passed!')

