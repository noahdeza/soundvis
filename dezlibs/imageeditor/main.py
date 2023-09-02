# Import and set logging
import dezlibs.logger.Logger as Logger

logger = Logger.getLogger()

# Python imports
import time
import numpy as np

# Visual related imports
from PIL import ImageDraw

# Sorting algoritms:
def sortSecond(val):
    return val[1]

def addInformationToImages(images, render_time, fps, samplerate, audio_file):
    '''
    # INPUT
    #   images = list of Image objects
    #   render_time = time.time() object of time it took to render all the images
    #   fps = frames per second
    # OUTPUS
    #   images = list of Image objects with data added to them
    '''
    len_images = images[-1][0]
    for i, im, duration in images:
        draw = ImageDraw.Draw(im)
        text_info = f'''\n
        Frame: {i}
        Time to render: {duration:.2f} s
        Total amount of frames rendered: {len_images}
        Total render time: {render_time:.2f} s
        FPS: {fps}
        Audio file: {audio_file}
        Sample rate: {samplerate}'''
        
        draw.text((20,20), text_info, (255,255,255))
    
    return images


def saveGif(file_name, images, fps):
    '''
    # INPUT
    #   file_name = name of gif that needs to be created
    #   images = list(i, im) where "i" is the position of the "im" PIL Image object
    #   sr = sample rate
    #   duration = duration of 1 frame in milliseconds
    '''
    duration_frame = 1000 / fps # millisecond
    logger.info('Saving gif...')

    images_list = list()
    for i in images:
        images_list.append(i[1])
    
    try:
        images_list[0].save(
            file_name,
            save_all=True,
            append_images=images_list[1:],
            optimize=False,
            duration=duration_frame,
            loop=0
        )
        logger.info('Gif succesfully saved')
    except Exception as e:
        logger.exception(f'Failed to save gif. Reason: {e}')
        return


def saveImages(images):
    from datetime import datetime
    date = datetime.now().strftime('%d%m%Y-%H%M%S')
    save_to_dir = 'data/temp/'
    filename_prefix = 'temp_'
    file_extension = '.jpg'

    counter = 1
    logger.info('Saving images...')
    for i, im, duration in images:
        #im.convert('RGB') # Necessary to save as .jpg
        file_name = save_to_dir + filename_prefix + date + '_' + str(i) + file_extension
        im.convert('RGB').save(file_name)
        counter += 1
    logger.info('Images saved successfully')


# Define different sorting algoritms here
def sortMiddleLine(data, im):
    '''
    # Input
    #   im = Image object
    #   data:
    #       [0] = index of frame
    #       [1] = dy
    #       []
    #   min_x = minimum width that gets sorted
    #   max_x = maximum width that gets sorted
    # Output
    #   im_copy = manipulated "im" object
    #   duration = duration is time it took to generate image
    '''
    start = time.time()
    im_copy = im.copy()
    index = data[0]
    width, height = im.size
    half_height = int((height / 2) - 1)

    # "dy" cannot equal or be bigger than "half_height"
    # as this will cause an index error
    dy = abs(int(data[1]))
    if dy > half_height:
        dy = half_height

    min_x = 0
    min_y = half_height - dy - 1
    max_x = int(dy * 2)
    max_y = half_height + dy

    if max_x > width - 1:
        max_x = width - 1

    for y in range(min_y, max_y, 1):
        pixel_row = list()
        counter = 0

        for x in range(min_x, max_x, 1):
            pixel = im.getpixel((x, y))
            total = pixel[0] + pixel[1] + pixel[2]
            pixel_row.append([pixel, total])

            counter += 1

        pixel_row.sort(reverse=True, key=sortSecond)

        for i in range(len(pixel_row)):
            im_copy.putpixel((i, y), pixel_row[i][0])
    
    duration = time.time() - start
    return index, im_copy, duration
    