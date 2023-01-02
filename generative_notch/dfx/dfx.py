import os
import logging
import zipfile
from xml.dom import minidom
import tempfile
from generative_notch.dfx.demolition_script import DemolitionScript

DEMOLITION_FILENAME = 'Demolition.script'


class Dfx:
	"""Manipulator for DFX files that makes life easier.

	Using this class I can do::
		>>> dfx = Dfx('path_to_dfx_file')
		>>> dfx.script.layer(0).node('$F_Envelope1').property('Attributes', 'Value').set(3)

	Instead of doing::
		>>> dfx = Dfx('path_to_dfx_file')
		>>> dfx.script._dom.getElementsByTagName('Layer')[0].getElementsByTagName('Effect')[1].getElementsByTagName('PropertyManager')[0].getElementsByTagName('GRP')[0].getElementsByTagName('PRP')[1].attributes['value'].value = 3
	"""

	def __init__(self, filepath):
		self.script = self._load(filepath)

	def __repr__(self):
		return f'Dfx("{self._dfx_filepath}")'

	def _load(self, filepath: str, skip_log: bool = False) -> DemolitionScript:
		"""
		Extracts script file from DFX file and prepares it for changes. No need to call it since it's called in __init__

		:param filepath: full path to .dfx file
		:return: DemolitionScript object
		"""
		if not skip_log:
			logging.info("Loading DFX file: [%s]", filepath)

		try:
			self._dfx_filepath = filepath

			with zipfile.ZipFile(filepath, 'r') as archive:
				tmpdir = tempfile.mkdtemp()
				self._script_intermediate_filepath = archive.extract(DEMOLITION_FILENAME, tmpdir)
				try:
					self._script_content = minidom.parse(self._script_intermediate_filepath)
				except Exception as e:
					logging.error("Cannot parse properly script file: [%s]", self._script_intermediate_filepath)
					logging.exception(e)
		except FileNotFoundError as e:
			logging.exception(e)

		logging.debug("DFX file loaded!")
		return DemolitionScript(self._script_content)

	def save(self, directory: str = None, filename: str = None, override: bool = False) -> str:
		"""Saves DFX file.

		:param directory: directory to save in, f.e. 'D:\\projects', if None will override source file
		:param filename: filename to use, f.e. 'MyProject', if none, will use source file name
		:param override: enable overriding file?
		:returns: filepath of output dfx file
		"""
		if self._script_content:
			out_filepath = self.__filepath_from_directory_filename(directory, filename)
			logging.info(f"Saving DFX to: {out_filepath}")

			if os.path.exists(out_filepath) and not override:
				logging.warning("Skipping, file exists, override is disabled!")
				return ''

			self.__update_intermediate_script_with_changes()

			handle, temp_filepath = tempfile.mkstemp(dir=os.path.dirname(self._dfx_filepath))
			os.close(handle)

			self.__copy_original_assets_to(temp_filepath)

			if os.path.exists(out_filepath) and override:
				logging.debug("Overriding file")
				os.remove(out_filepath)
			os.rename(temp_filepath, out_filepath)

			self.__insert_intermediate_script_into(out_filepath)

			logging.debug('Successfully saved!')
			return out_filepath
		else:
			logging.error("Content of script file is invalid, unable to save DFX!")

	def __filepath_from_directory_filename(self, directory: str, filename: str) -> str:
		"""Generate output filepath based on input directory and filename values"""

		out_dir = directory if directory else os.path.dirname(self._dfx_filepath)
		if not os.path.exists(out_dir):
			os.mkdir(out_dir)
		out_filename = filename if filename else os.path.basename(self._dfx_filepath).split('.')[0]

		return out_dir + '\\' + out_filename + '.dfx'

	def __update_intermediate_script_with_changes(self):
		""" Write xml back to temp script file"""
		logging.debug('Applying changes to temporary Demolition.script file')

		with open(self._script_intermediate_filepath, "w") as script_intermediate_file:
			self._script_content.writexml(script_intermediate_file)
		self.__apply_xml_to_dfx_fix()

	def __apply_xml_to_dfx_fix(self):
		""" XML parser creates some bugs, fix them here"""
		logging.debug("Adapting XML to DFX format")

		try:
			lines = []
			with open(self._script_intermediate_filepath, 'r') as file:
				while True:
					line = file.readline()

					# remove xml declaration appended by parser
					line = line.replace('<?xml version="1.0" ?>', '')

					# fix line: IntPLink nodeId=&quot;2bbb3f58-9585-11ec-bdc4-0002c95af100&quot; subNodeId=&quot;&quot;/&gt;
					# to      : IntPLink nodeId="2bbb3f58-9585-11ec-bdc4-0002c95af100" subNodeId=""/>
					line = line.replace('&quot;', '"')
					line = line.replace('&gt;', '>')

					lines.append(line)

					if not line:
						break

			with open(self._script_intermediate_filepath, 'w') as file:
				file.truncate(0)
				file.seek(0)
				file.writelines(lines)
		except FileNotFoundError as e:
			logging.exception(e)

	def __copy_original_assets_to(self, target_dfx_filepath):
		"""Copy original assets from old DFX to new one"""
		logging.debug('Replicating original DFX file with original assets')

		try:
			# create a temp copy of the dfx without script file
			with zipfile.ZipFile(self._dfx_filepath, 'r') as dfx_in:
				with zipfile.ZipFile(target_dfx_filepath, 'w') as dfx_out:
					dfx_out.comment = dfx_in.comment

					# copy all files except original script file
					for item in dfx_in.infolist():
						if item.filename != DEMOLITION_FILENAME:
							dfx_out.writestr(item, dfx_in.read(item.filename))
		except FileNotFoundError as e:
			logging.error("Error while saving DFX file, input file changed!")
			logging.exception(e)

	def __insert_intermediate_script_into(self, target_dfx_filepath):
		"""Insert modified Demolition.script file into new DFX file"""
		logging.debug('Inserting modified script file')

		with open(self._script_intermediate_filepath, "r") as script_intermediate_file:
			with zipfile.ZipFile(target_dfx_filepath, mode='a', compression=zipfile.ZIP_DEFLATED) as zf:
				zf.writestr(DEMOLITION_FILENAME, script_intermediate_file.read())

	def reset(self, force_reload: bool = False):
		"""Reverts all changes made to script file"""
		logging.debug('Reverting script to initial state')

		if force_reload:
			self.script = self._load(self._dfx_filepath, True)
