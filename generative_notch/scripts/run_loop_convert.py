import logging
import os
from argparse import ArgumentParser
from generative_notch._deprecated.render import loop_video, convert_to_h264

if __name__ == '__main__':
    os.chdir(os.path.dirname(__file__))
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    logging.basicConfig(format=' %(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    parser = ArgumentParser()
    parser.add_argument('input', type=str)
    args = parser.parse_args()

    looped_filepath = loop_video(
        ffmpeg_path="C:\\ffmpeg\\bin\\ffmpeg.exe",
        source_filepath=args.input,
        duration_frames=250,
        loop_frames=124,
        fps=25,
        replace_original=True
    )
    convert_to_h264(
        ffmpeg_path="C:\\ffmpeg\\bin\\ffmpeg.exe",
        source_filepath=looped_filepath,
        duration_seconds=10,
        replace_original=True,
        target_size=10240
    )
