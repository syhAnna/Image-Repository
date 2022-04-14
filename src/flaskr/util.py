import os
import logging
import string
from PIL import Image, ImageFont, ImageDraw, ImageFilter
import random
import hashlib
import subprocess
from .db import *
from . import UPLOAD_FOLDER
from werkzeug.exceptions import abort
from playhouse.shortcuts import model_to_dict


def generate_validate_picture(num_chars = 5):
    candidate_char_set = string.digits + string.ascii_letters
    width, heighth = num_chars * 30, 40    # size of picture 130 x 50

    # generate an image object and set the fonts
    im = Image.new('RGB',(width, heighth), 'White')
    # font = ImageFont.truetype("arial.ttf", 28, encoding="unic")
    # This is for Windows
    # font = ImageFont.truetype("arial.ttf", 28, encoding="unic")
    # This is for Mac
    font = ImageFont.truetype("/Library/Fonts/Arial", 28)
    draw = ImageDraw.Draw(im)
    generated_string = ''
    # output each char
    for item in range(num_chars):
        text = random.choice(candidate_char_set)
        generated_string += text
        draw.text((13 + random.randint(4, 7) + 20*item, random.randint(3, 7)), text=text, fill='Black', font=font)

    # draw several lines
    for num in range(8):
        x1 = random.randint(0, width/2)
        y1 = random.randint(0, heighth/2)
        x2 = random.randint(0, width)
        y2 = random.randint(heighth/2, heighth)
        draw.line(((x1, y1), (x2, y2)), fill='black', width=1)

    # Vague
    im = im.filter(ImageFilter.FIND_EDGES)
    return im, generated_string

def generate_filecont_hash(content):
    m = hashlib.sha256()
    m.update(content)
    return m.hexdigest()

def check_filecontent_hash(filehash, content):
    content_hash = generate_filecont_hash(content)
    return filehash == content_hash
