# Import and set logging
import logging

logger_lvl = logging.DEBUG
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# Python imports
import numpy as np

# Visual related imports
from PIL import Image, ImageFont, ImageDraw

# Sorting algoritms:
def sortSecond(val):
    return val[1]

def addInformationToImages(images, render_time, fps, samplerate):
    '''
    # Input
    #   images = list of Image objects
    #   render_time = time.time() object of time it took to render all the images
    #   fps = frames per second
    # Output
    #   images = list of Image objects with data added to them
    '''
    len_images = len(images)
    for i in range(len_images):
        draw = ImageDraw.Draw(images[i])
        text_info = f'''\n
        Frame: {i}
        Total amount of frames rendered: {len_images}
        Render time: {round(render_time, 4)} s
        FPS: {fps}
        Sample rate: {samplerate}'''
        
        draw.text((20,20), text_info, (255,255,255))
    
    return images


def saveImages(images):
    from datetime import datetime
    date = datetime.now().strftime('%d%m%Y-%H%M%S')
    save_to_dir = 'data/temp/'
    filename_prefix = 'temp_'
    file_extension = '.jpg'

    counter = 1
    for i in images:
        #i.convert('RGB') # Necessary to save as .jpg
        file_name = save_to_dir + filename_prefix + date + '_' + str(counter) + file_extension
        i.convert('RGB').save(file_name)
        counter += 1


def sortMiddleLine(im, dy):
    '''
    # Input
    #   im = Image object
    #   dy = delta from middle y coordinate
    #   min_x = minimum width that gets sorted
    #   max_x = maximum width that gets sorted
    # Output
    #   im_copy = manipulated "im" object
    '''
    im_copy = im.copy()
    counter = int()
    width, height = im.size
    half_height = int((height / 2) - 1)
    dy = abs(int(dy))
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
    
    return im_copy


def createGif(file_name, images, fps):
    '''
    # Input
    #   images = list of PIL Image object
    #   sr = sample rate
    #   duration = duration of 1 frame in milliseconds
    '''
    duration_frame = 1000 / fps # millisecond
    logger.info('Saving gif...')
    try:
        images[0].save(
            file_name,
            save_all=True,
            append_images=images[1:],
            optimize=False,
            duration=duration_frame,
            loop=0
        )
        logger.info('Gif succesfully saved')
    except Exception as e:
        logger.exception(f'Failed to save gif. Reason: {e}')
    