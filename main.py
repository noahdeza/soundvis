# soundvis information
SV_INFO = {
    'author':'Noah Dezaire',
    'version':'0.0.1',
}

# Declare starting variables
PI = 3.141592653589793
FPS = 30 # Must be 30 or 60
VIDEO_LENGTH = 2 # SECONDS
TOTAL_FRAMES = FPS * VIDEO_LENGTH


if __name__ == '__main__':
    # Python imports
    import os
    import time
    from glob import glob
    from pathlib import Path

    # Logging imports
    import logging
    import dezlibs.logger.Logger as Logger

    # Create logger
    LOGGER_LVL = logging.DEBUG
    logger = Logger.createLogger(lvl=LOGGER_LVL, mode='w')
    logger.setLevel(logging.DEBUG)

    logger.info(f'Starting soundvis v{SV_INFO["version"]}...')
    logger.info(f'Author: {SV_INFO["author"]}')
    logger.info('Importing libraries...')
    start_import_libraries = time.time()

    # 3rd party imports
    import numpy as np
    import pandas as pd

    # Visual related imports
    from PIL import Image
    import librosa
    import dezlibs.imageeditor.main as imge

    end_import_libraries = time.time() - start_import_libraries
    logger.info(f'Libraries imported in {end_import_libraries}')

    # Check if all necessary directories have been created
    logger.debug('Creating mandatory directories if they do not exist...')
    Path('data/audio').mkdir(exist_ok=True)
    Path('data/img').mkdir(exist_ok=True)
    Path('data/temp').mkdir(exist_ok=True)

    # Empty "data/temp" to store generated images for video
    logger.info('Removing files from data/temp')
    files = glob('data/temp/*')
    for f in files:
        try:
            logger.debug('Removing {f}')
            os.remove(f)
        except Exception as e:
            logger.error(f'Failed to remove {f}. Reason: {e}')

    logger.debug('Importing functions...')
    # Declare functions
    def calculateCommonIntervalSrFps(sr: float, fps: int, amps: list) -> list:
        '''
        # INPUT
        #   sr = samplerate of audio file
        #   fps = frames per second of GIF
        #   amps = list() of amplitudes of wave file that should be analysed
        #
        # OUTPUT
        #   data = data of "amps" that should be
        #       used for the generation of the GIF
        #
        # INFO
        #   Take the necessary values of "amps" for each frame that needs
        #   to be generated.
        '''
        amps = list(amps)
        data = list()
        len_amps = len(amps)
        ratio_sr_fps = sr / fps
        len_gif = round((len_amps / sr), 1) # seconds
        amount_of_frames = int(len_gif * fps)

        for i in range(0, amount_of_frames, 1):
            try:
                data.append(amps[int(i * ratio_sr_fps)])
            except IndexError as e:
                logger.debug('Index error when creating "data": {e}')
                data.append(amps[-1])

        return data                                         

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
    
    # Open selected image
    logger.debug(f'Loading image {selected_image_file}')
    try:
        im = Image.open(selected_image_file)
        logger.info('Image loaded successfully')
    except Exception as e:
        logger.error(f'Failed to load image: {e}')
    
    width, height = im.size
    amps *= 1000
    images = list()
    len_amps = len(amps)
    logger.debug(f'Max amplitude: {max(amps)}')
    indexes_amps = calculateCommonIntervalSrFps(samplerate, FPS, amps)
    len_indexes_amps = len(indexes_amps)
    
    logger.info('Starting single threaded GIF generation...')

    counter = 1
    start_render = time.time()
    for i in indexes_amps:
        logger.debug(f'Generating image {counter}/{len_indexes_amps}')
        try:
            temp_im = imge.sortMiddleLine(im, i)
        except IndexError as e:
            logger.debug(f'Index error for sortMiddleLine: {e}')
            temp_im = im.copy()
        images.append(temp_im)
        counter += 1
    end_render = time.time() - start_render

    logger.debug(f'Time it took to render images: {round(end_render, 2)} s')

    imge.addInformationToImages(images, end_render, FPS, samplerate)
    imge.createGif('data/test01.gif', images, FPS)

    logger.info('Saving images...')
    imge.saveImages(images)
    logger.info('Images saved')