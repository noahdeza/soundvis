# soundvis information
SV_INFO = {
    'author':'Noah Dezaire',
    'version':'0.0.2',
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

    # Import libraries for multiprocessing
    from multiprocessing import Pool, cpu_count
    from functools import partial
    import dezlibs.imageeditor.main as imge

    # 3rd party imports
    import numpy as np
    import pandas as pd

    # Visual related imports
    from PIL import Image
    import librosa

    end_import_libraries = time.time() - start_import_libraries
    logger.info(f'Libraries imported in {end_import_libraries}')

    # Check if all necessary directories have been created
    logger.info('Creating mandatory directories if they do not exist...')
    Path('data/audio').mkdir(exist_ok=True)
    Path('data/img').mkdir(exist_ok=True)
    Path('data/temp').mkdir(exist_ok=True)

    # Empty "data/temp" to store generated images for video
    logger.info('Removing files from data/temp')
    files = glob('data/temp/*')
    for f in files:
        try:
            logger.debug(f'Removing {f}')
            os.remove(f)
        except Exception as e:
            logger.error(f'Failed to remove {f}. Reason: {e}')

    logger.info('Importing functions...')
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

        counter = 1
        for i in range(0, amount_of_frames, 1):
            try:
                data.append((counter, amps[int(i * ratio_sr_fps)]))
            except IndexError as e:
                logger.exception('Index error when creating "data": {e}')
                data.append((counter, amps[-1]))

            counter += 1

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
    logger.debug(f'Audio files: {audio_files}')

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
    amps *= 1000
    logger.info('Audio file loaded')

    logger.debug('Information about audio file:')
    logger.debug(f'Sample rate: {samplerate}')
    logger.debug(f'Max amplitude: {np.max(amps)}')
    logger.debug(f'Min amplitude min: {np.min(amps)}')
    logger.debug(f'Median amplitude: {np.median(amps)}')

    # Perform beat track
    logger.info('Performing beat tracking...')
    bpm, beats = librosa.beat.beat_track(y=amps,sr=samplerate)
    logger.info(f'BPM {selected_audio_file}: {bpm}')
    logger.info(f'Beats {selected_audio_file}: {beats}')
    
    # Open selected image
    logger.info(f'Loading image {selected_image_file}')
    try:
        im = Image.open(selected_image_file)
        logger.info('Image loaded successfully')
    except Exception as e:
        logger.error(f'Failed to load image: {e}')
    
    # Get all necessary variables for image creation
    indexes_amps = calculateCommonIntervalSrFps(samplerate, FPS, amps)
    len_indexes_amps = len(indexes_amps)

    logger.info('Starting multiprocessing image generation...')
    start_render_multi = time.time()

    render_func = partial(imge.sortMiddleLine, im=im.copy())
    images_multi = list()

    logger.info('Initiating multiprocessing pool...')
    CPU_COUNT = cpu_count() - 1
    logger.debug(f'Amount of cores used: {CPU_COUNT - 1}')
    with Pool(CPU_COUNT) as p:
        logger.info('Initiated pool')
        results = p.imap_unordered(render_func, indexes_amps)

        for index, _im, duration in results:
            logger.debug(f'Image {index} generated in {duration:.2f} s')
            images_multi.append([index, _im.copy(), duration])
    
    # Delete "results" as it is not needed anymore
    # and takes up a lot of memory
    del results

    end_render_multi = time.time() - start_render_multi
    logger.info('Finished multi threaded image generation')

    # Sort the images so they are in correct order
    images_multi.sort()

    logger.info(f'Time it took to render images with multi threading: {round(end_render_multi, 2)} s')

    imge.addInformationToImages(images_multi, end_render_multi, FPS, samplerate, selected_audio_file)
    imge.saveGif('data/test02.gif', images_multi, FPS)

    imge.saveImages(images_multi)
    
    logger.info('Finished with script')