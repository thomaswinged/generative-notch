from generative_notch import get_config
from tqdm import tqdm
import subprocess
import os
import logging
from tempfile import TemporaryDirectory


class Renderer:
	def __init__(self, render_list: dict[str, list]):
		self.render_list = render_list
		self.cfg = get_config()
		self.loop_required = self.cfg['render_settings']['loop_frames'] > 0

	def run(self, replace_original: bool = True):
		render_progress = tqdm(self.render_list.keys())
		for dfx_filepath in render_progress:
			render_progress.set_description(f'Rendering [{os.path.basename(dfx_filepath)}]')
			logging.info(f'\nStarting rendering project {dfx_filepath}')
			self.__render_project(dfx_filepath)

			files_to_convert = []
			if self.loop_required:
				loop_progress = tqdm(self.render_list[dfx_filepath])
				for video_filepath in loop_progress:
					loop_progress.set_description(f'\tLooping [{os.path.basename(video_filepath)}]')
					files_to_convert.append(
						self.__loop(video_filepath, replace_original)
					)
			else:
				files_to_convert = self.render_list[dfx_filepath]

			convert_progress = tqdm(files_to_convert)
			for video_filepath in convert_progress:
				convert_progress.set_description(f'\tConverting to H264 [{os.path.basename(video_filepath)}]')
				self.__convert_to_h264(video_filepath, replace_original)

		logging.debug('Finished rendering all projects!')

	def __render_project(self, filepath):
		"""Executes project queue renderer using config

		:param filepath:  DFX to render, f.e. D:\\Projects\\nft_notch\\notch\\dfx\\combinations\\C-0_5.dfx
		"""
		render_project_queue(
			notch_app=self.cfg['notch_app'],
			source_filepath=filepath
		)

	def __loop(self, filepath: str, replace_original: bool = False) -> str:
		"""Loops given video file using config

		:param source_filepath: File to convert, f.e. D:\Projects\nft_notch\notch\output\C_1.mp4
		:param replace_original: if True, after conversion will replace original file with new one (extension may differ)
		:return: filepath of a looped file
		"""
		result = loop_video(
			ffmpeg_path=self.cfg['ffmpeg'],
			source_filepath=filepath,
			duration_frames=self.cfg['render_settings']['duration_frames'],
			loop_frames=self.cfg['render_settings']['loop_frames'],
			fps=self.cfg['render_settings']['fps'],
			replace_original=replace_original
		)
		return result
		
	def __convert_to_h264(self, filepath: str, replace_original: bool = False) -> str:
		"""Converts to H264 given file using config

		:param filepath: File to convert, f.e. D:\\Projects\\nft_notch\\notch\\output\\C_1.mp4
		:param replace_original: if True, after conversion will replace original file with new one (extension may differ)
		:return: filepath of a converted file
		"""
		result = convert_to_h264(
			ffmpeg_path=self.cfg['ffmpeg'],
			source_filepath=filepath,
			duration_seconds=self.cfg['render_settings']['duration_frames'] / self.cfg['render_settings']['fps'],
			replace_original=replace_original,
			target_size=self.cfg['render_settings']['target_size_kb']
		)
		return result


def render_project_queue(notch_app: str, source_filepath: str):
	"""Executes project queue renderer.

	:param notch_app: f.e. C:\\Program Files\\Notch\\NotchApp.exe
	:param source_filepath: f.e. D:\\Projects\\nft_notch\\notch\\output\\C_1.mp4
	:return:
	"""
	logging.info(f'Rendering project queue {source_filepath}')

	cmd = f'"{notch_app}" -renderqueue "{source_filepath}"'
	_run_and_log_process(cmd)

	logging.debug(f'Finished rendering project queue {source_filepath}')


def loop_video(ffmpeg_path: str, source_filepath: str, duration_frames: int, loop_frames: int, fps: int, replace_original: bool = True):
	"""Loops given video file. Output codec is yuv420p.

	:param ffmpeg_path: path to ffmpeg, f.e. C:\\ffmpeg\\bin\\ffmpeg.exe
	:param source_filepath: f.e. D:\\Projects\\nft_notch\\notch\\output\\C_1.mp4
	:param duration_frames: in frames
	:param loop_frames: duration of loop blend in frames
	:param fps: frames per second
	:param replace_original: if True, after conversion will replace original file with new one (extension may differ)
	:return: filepath of a looped file
	"""
	logging.info(f'Looping video {source_filepath}')

	output_filepath = os.path.splitext(source_filepath)[0] + '_loop.mp4'

	# filters
	body_dur = duration_frames / fps
	total_dur = (duration_frames + loop_frames) / fps
	blend_dur = loop_frames / fps
	f_res_div_4 = '[0]pad=ceil(iw/4)*4:ceil(ih/4)*4[o];'  # make resolution dividable by 4 (yuva420p requirement)
	f_split = '[o]split[tran][body];'  # split video into main video part and loop stub part
	f_body_part = f'[body]trim=0:{body_dur},setpts=PTS-STARTPTS,format=yuva420p,fade=d={blend_dur}:alpha=1[jt];'
	f_tran_part = f'[tran]trim={body_dur}:{total_dur},setpts=PTS-STARTPTS[main];'
	f_overlay = '[main][jt]overlay[final];[final]unsharp=3:3:1.5'
	filters = f'{f_res_div_4}{f_split}{f_body_part}{f_tran_part}{f_overlay}'

	cmd = f'"{ffmpeg_path}" -i "{source_filepath}" -filter_complex {filters} -y "{output_filepath}"'
	_run_and_log_process(cmd)

	if replace_original:
		os.remove(source_filepath)
		result = output_filepath.split('_loop')[0] + '.mp4'
		os.rename(output_filepath, result)
	else:
		result = output_filepath

	logging.debug(f'Finished looping {source_filepath}')
	return result


def convert_to_h264(ffmpeg_path: str, source_filepath: str, duration_seconds: float, replace_original: bool = True, *, target_size: int = -1, target_birate: int = 5000) -> str:
	"""Converts given file to h264 targeting either in bitrate or filesize. CRF is not supported now (not needed).
	If provided target size, bitrate will be automatically calculated.
	I am not converting using 2 passes because I get some strange errors when using NotchLC as input.

	:param ffmpeg_path: path to ffmpeg, f.e. C:\\ffmpeg\\bin\\ffmpeg.exe
	:param source_filepath: f.e. D:\\Projects\\nft_notch\\notch\\output\\C_1.mov
	:param duration_seconds: in seconds
	:param replace_original: if True, after conversion will replace original file with new one (extension may differ)
	:param target_size: optional, in kbps, f.e. 5120
	:param target_birate:
	:return: filepath of a converted file
	"""
	logging.info(f'Converting file {source_filepath} to H264...')

	bitrate = target_birate
	if target_size != -1:
		bitrate = calculate_bitrate(target_size, duration_seconds)
	bitrate = str(int(bitrate)) + 'k'

	output_filepath = os.path.splitext(source_filepath)[0] + '_h264.mp4'

	cmd = f'"{ffmpeg_path}" -hwaccel auto -i "{source_filepath}" -c:v libx264 -b:v {bitrate} -strict -2 -passlogfile "{os.path.dirname(output_filepath)}" -pass 2 -y "{output_filepath}"'
	_run_and_log_process(cmd)

	if replace_original:
		os.remove(source_filepath)
		result = output_filepath.split('_h264')[0] + '.mp4'
		os.rename(output_filepath, result)
	else:
		result = output_filepath

	logging.debug(f'Finished converting file {source_filepath}')
	return result


def _run_and_log_process(cmd: str, universal_newlines=True):
	logging.debug(f'Executing command: {cmd}')

	p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=universal_newlines)
	for line in p.stdout:
		logging.debug(line.replace('\n', '') if universal_newlines else line)
	p.stdout.close()


def make_directory_snapshot(directory):
	return os.listdir(directory)


def calculate_bitrate(file_size, duration) -> int:
	"""Calculates bitrate given file size and duration.

	:param file_size: in kbps
	:param duration: in seconds
	:return: calculated bitrate
	"""
	return file_size * 8/duration