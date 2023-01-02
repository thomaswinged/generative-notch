from generative_notch import get_config
from generative_notch.dfx.dom_element_wrapper import DomElementWrapper
from generative_notch.dfx.layer import Layer
from xml.dom.minidom import Element
import os
import logging


class RenderQueue(DomElementWrapper):
	"""Manager for queueing layers to render."""

	def __init__(self, dom):
		super().__init__(dom)
		self.entries = [RenderQueueItem(element) for element in dom.getElementsByTagName('LayerRenderQueueItem')]
		self.render_settings = get_config()['render_settings']

	def add(self,  layer: Layer, directory: str, filename: str = None, render_settings: dict = None) -> str:
		"""Adds a render queue entry based on passed params

		:param layer: layer to render
		:param directory: f.e. 'D:\output'
		:param filename: f.e. MyBirthdayVideo, if None will use layer's name
		:param render_settings: if not passed, will use DEFAULT_RENDER_SETTINGS
		:returns: filepath of a file that the layer will be rendered to
		"""
		layer_id = layer.get_attribute('guid')

		if not os.path.exists(directory):
			os.mkdir(directory)

		target_filepath = os.path.join(
			directory,
			filename if filename else layer.get_attribute('name')
		)
		target_filepath += '.mp4'

		logging.debug(f"Adding layer {layer.get_attribute('name')} to render queue as {target_filepath}")

		new_entry = RenderQueueItem.from_attributes(
			self._dom,
			layer_id,
			target_filepath,
			**self.render_settings
		)

		self.entries.append(new_entry)

		return target_filepath


class RenderQueueItem(DomElementWrapper):
	"""
	Contains info like target filename, render settings, layer reference

	XML representation of the element:\n
	<LayerRenderQueueItem enabled="1" layerId="..." targetFilename="D:\output\Layer 1.mp4">
	"""

	def __init__(self, dom):
		super().__init__(dom)

		self.render_settings = dom.getElementsByTagName('ExportVideoProfile')[0]

	@classmethod
	def from_attributes(cls, parent: Element, layer_id: str, target_filename: str, **render_settings):
		dom = Element('LayerRenderQueueItem')
		dom.ownerDocument = parent.ownerDocument
		parent.appendChild(dom)

		attribs = {
			'enabled': '1',
			'layerId': layer_id,
			'targetFilename': target_filename
		}

		for key, value in attribs.items():
			dom.setAttribute(key, value)

		render_settings = ExportVideoProfile.from_attributes(dom, **render_settings)

		result = cls(dom)
		result.render_settings = render_settings
		return result


class ExportVideoProfile(DomElementWrapper):
	"""Render settings of a layer.

	Will render using NotchLC codec if render_settings has loop_frames value bigger than 0
	(in order to not lose quality when re-encoding using ffmpeg later).
	Otherwise, will render using H264.

	Codec values reference:
	NotchLC - codec: 875967080, exportType: 0
	H264 - codec: 1852009571, exportType : 6
	"""
	@classmethod
	def from_attributes(cls, parent: Element, width: int, height: int, fps: int, duration_frames: int, preroll_frames: int = 0, loop_frames: int = 0, **kwargs):
		# TODO: IS there any way to make param list shorter?
		dom = Element('ExportVideoProfile')
		dom.ownerDocument = parent.ownerDocument
		parent.appendChild(dom)

		attribs = {
			'name': '',
			'width': str(width),
			'height': str(height),
			'maxFrames': '16777216',
			'fps': str(fps),
			'exportType': '6',
			'codec': '875967080',
			'quality': '100',
			'startTime': str(preroll_frames * 240),
			'endTime': str(duration_frames * 240 + preroll_frames * 240 + loop_frames * 240),
			'alphaEnabled': '0',
			'audioEnabled': '0',
			'audioOffset': '0',
			'motionBlurFrames': '0',
			'simulationRateScale': '1',
			'aaFrames': '1',
			'motionBlurAmount': '0',
			'allowLooping': '1',
			'prerollEnabled': '1' if preroll_frames > 0 else '0',
			'prerollDuration': str(preroll_frames * 240),
			'raytracePasses': '1',
			'upscaleMode': '0',
			'aiUpscale': '0',
			'useViewportRenderer': '0',
			'tileGBuffers': '0'
		}

		for key, value in attribs.items():
			dom.setAttribute(key, value)

		return cls(dom)
