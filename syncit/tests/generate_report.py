import os
from moviepy.editor import VideoFileClip
import tempfile
from datetime import datetime
import logging
from werkzeug.datastructures import FileStorage
from syncit.delay_checker import DelayChecker
from syncit.constants import TestConstants
from logger_setup import setup_logging

setup_logging()
logger = logging.getLogger(__name__)


def check_delay(video_path, subtitles, subfolder, folder_path):
    t0 = datetime.now()
    for start in range(0, TestConstants.DELAY_CHECKER_SECTIONS_TIME * 10, TestConstants.DELAY_CHECKER_SECTIONS_TIME):
        end = start + TestConstants.DELAY_CHECKER_SECTIONS_TIME

        with tempfile.TemporaryDirectory() as tmpdir:
            logger.debug(f"Temporary folder: {tmpdir}")
            if(start == 0 and end == 200):
                trimmed_video_path = os.path.join(folder_path, 'first.mp4')
            else:
                trimmed_video_path = os.path.join(tmpdir, f'temporary.mp4')
                logger.debug(
                    f"Video Path: {trimmed_video_path}; Start: {start}; End: {end}")
                clip = VideoFileClip(video_path)
                clip.subclip(start, end).write_videofile(
                    trimmed_video_path, threads=4)

                logger.debug("Finished writing video file.")

            video_binary = open(trimmed_video_path, 'rb')
            logger.debug("Finished reading binary.")

            video = FileStorage(video_binary)

            dc = DelayChecker(
                video, start, end, subtitles, video_path[-3:])
            logger.debug("Initialized delay checker. Checking delay...")
            delay = dc.check_delay_in_timespan()
            del dc
            del video
            video_binary.close()
            logger.debug(f"Finished checking delay: {delay}")
            if(delay):
                logger.debug(f"Found Delay! {delay}")
                t1 = datetime.now()
                delta = t1 - t0

                with open(os.path.join(folder_path, 'delay.txt'), 'r') as f:
                    true_delay = float(f.read()) * (-1)
                if(abs(true_delay - delay) < 0.4):
                    is_successful = 'true'
                else:
                    is_successful = 'false'

                return f'{subfolder},{delay},{delta},{start / TestConstants.DELAY_CHECKER_SECTIONS_TIME},{true_delay},{is_successful}\n'

    t1 = datetime.now()
    delta = t1 - t0
    return f'{subfolder},N/A,{delta},N/A\n'


def check():
    report_number = input('Report Number: ')
    logger.debug("Starting from check")
    skip = []
    with open(f'report_{report_number}.csv', 'w') as f:
        f.write('index,delay,delta,iterations_needed,true_delay,is_successful\n')
    for subfolder in os.listdir(TestConstants.SAMPLES_PATH):
        folder_path = os.path.join(TestConstants.SAMPLES_PATH, subfolder)

        if(os.path.isdir(folder_path) is False):
            continue
        
        if(int(subfolder) in skip):
            continue

        logger.debug(f"Folder Path: {folder_path}")
        for file in os.listdir(folder_path):
            if(file.endswith('.srt')):
                subtitles_path = os.path.join(folder_path, file)
            elif((file.endswith('.mkv') or file.endswith('.mp4')) and file != 'first.mp4'):
                video_path = os.path.join(folder_path, file)

        logger.debug(
            f"Subtitles Path: {subtitles_path}. Video Path: {video_path}")
        if(not subtitles_path or not video_path):
            continue

        with open(subtitles_path, 'r') as f:
            subtitles = f.read()

        result = check_delay(video_path, subtitles, subfolder, folder_path)
        with open(f'report_{report_number}.csv', 'a') as f:
            f.write(result)
        logger.debug(f'Results: {result}')
