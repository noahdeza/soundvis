# Python imports
import os
import time
from glob import glob

# soundvis information
SV_INFO = {
    'author':'Noah Dezaire',
    'version':'0.0.1',
}

# Logging imports
import logging
import dezlibs.logger.Logger as Logger

# Create logger
LOGGER_LVL = logging.DEBUG
logger = Logger.createLogger(lvl=LOGGER_LVL, mode='w')
logger.setLevel(logging.DEBUG)

logger.info(f'Author: {SV_INFO["author"]}')
logger.info(f'Starting soundvis v{SV_INFO["version"]}...')
logger.info('Importing libraries...')
start_import_libraries = time.time()

# 3rd party imports
import numpy as np
import pandas as pd

# Visual related imports
from PIL import Image, ImageFont, ImageDraw
import librosa
import dezlibs.imageeditor.main as imge

end_import_libraries = time.time() - start_import_libraries
logger.info(f'Libraries imported in {end_import_libraries}')


# Declare starting variables
PI = 3.141592653589793
FPS = 30
VIDEO_LENGTH = 2 # SECONDS
TOTAL_FRAMES = FPS * VIDEO_LENGTH

logger.debug('Importing functions...')
# Declare functions
def calculateCommonIntervalSrFps(sr, fps, len_amps):
    '''
    # Input
    #   sr = samplerate of audio file
    #   fps = frames per second of GIF
    #   len_amps = length of "list(amps)"
    #
    # Output
    #   indexes = list of indexes of list() "amps" that should be
    #       used for the generation of the GIF
    '''
    indexes = list()
    ratio_sr_fps = sr / fps
    len_gif = round((len_amps / sr), 1) # seconds

    for i in range(0, int(len_gif * fps), 1):
        indexes.append(i * ratio_sr_fps)

    return indexes


if __name__ == '__main__':
    logger.info('Loading image paths...')
    image_files = glob('data/img/*.png')
    logger.info('Loaded image paths')

    # Make user select image
    print('Select image:')
    counter = 1
    for i in image_files:
        print(f'{counter}: {i}')
        counter += 1
    
    while True:
        try:
            selected_image_int = int(input('Enter number: '))
            selected_image_file = image_files[selected_image_int - 1]
            break
        except ValueError:
            print('Try again!')

    logger.info('Loading audio file paths...')
    audio_files = glob('data/audio/*.wav')
    logger.info('Loaded audio file paths')
    for i in audio_files:
        logger.debug(i)

    # Make user select audio file
    print('Select audio file:')
    counter = 1
    for i in audio_files:
        print(f'{counter}: {i}')
        counter += 1
    
    while True:
        try:
            selected_audio_int = int(input('Enter number: '))
            selected_audio_file = audio_files[selected_audio_int - 1]
            break
        except ValueError:
            print('Try again')

    # Load selected audio file
    logger.debug(f'File {selected_audio_file} selected')
    amps, samplerate = librosa.load(selected_audio_file, sr=None)
    logger.info('Audio file loaded')

    logger.debug('Information about audio file:')
    logger.debug(f'amplitude: {amps[10:]}...{amps[:10]}')
    logger.debug(f'shape amplitude: {amps.shape}')
    logger.debug(f'sample rate: {samplerate}')
    logger.debug(f'amplitude max: {np.max(amps)}')
    logger.debug(f'amplitude min: {np.min(amps)}')
    logger.debug(f'amplitude median: {np.median(amps)}')

    # Perform beat track
    logger.info('Performing beat tracking...')
    bpm, beats = librosa.beat.beat_track(y=amps,sr=samplerate)
    logger.info(f'BPM {selected_audio_file}: {bpm}')
    logger.info(f'Beats {selected_audio_file}: {beats}')

     # Create folder to store images of new gif
    if not os.path.exists('data/temp'):
        os.makedirs(f'data/temp')
    
    # Empty "data/temp" to store generated images for gif
    logger.info('Removing files from data/temp')
    files = glob('data/temp/*')
    for f in files:
        try:
            logger.debug('Removing {f}')
            os.remove(f)
        except Exception as e:
            logger.error(f'Failed to remove {f}. Reason: {e}')
    
    # Open selected image
    logger.debug(f'Loading image {selected_image_file}')
    try:
        im = Image.open(selected_image_file)
        logger.info('Image loaded successfully')
    except Exception as e:
        logger.error('Failed to load image:')
        logger.exception(e)
    
    width, height = im.size
    amps *= 1000
    images = list()
    len_amps = len(amps)
    logger.debug(f'Max amplitude: {max(amps)}')
    indexes_amps = calculateCommonIntervalSrFps(samplerate, FPS, len_amps)
    len_indexes_amps = len(indexes_amps)
    
    logger.info('Starting single threaded GIF generation...')
    start = time.time()

    counter = 1
    start_render = time.time()
    for i in indexes_amps:
        logger.debug(f'Generating image {counter}/{len_indexes_amps}')
        temp_im = imge.sortMiddleLine(im, amps[int(i)])
        images.append(temp_im)
        counter += 1
    end_render = time.time() - start_render

    logger.debug(f'Time it took to render GIF: {round(end_render, 2)} s')

    imge.addInformationToGif(images, end_render, FPS, samplerate)
    
    '''for i in amps[1000:1200]:
        logger.debug(f'Generating image {counter}/{len_list}')
        dy = abs(int(i * 100))
        temp_im = imge.sortMiddleLine(im.copy(), dy)
        draw = ImageDraw.Draw(temp_im)
        draw.text((20,20), f'Frame: {counter}', (255,255,255))
        
        images.append(temp_im)
        counter += 1'''

    end = time.time()
    time_single = end - start
    
    imge.createGif('data/test01.gif', images, FPS)
    
    images = list()
    start = time.time()
    data = list()
    pixels = np.asarray(im)
    

    end = time.time()
    time_multi = end - start
    logging.info(f'Time image generation: {time_multi}')
    logging.info(f'Time image generation: {time_multi}')
    print(f'time single THREADED: {time_single}')
    
    # Add information to gif
    #imge.addInformation(images, time_multi, FPS, samplerate)
    
    #imge.createGif('data/test4.gif', images, FPS)
    
    
    print(f'')