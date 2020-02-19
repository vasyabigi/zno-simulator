import json
import os
import requests

from os import path, walk, makedirs
from PIL import Image, ImageDraw
from urllib.parse import urljoin
from urllib.request import urlretrieve

QUESTIONS_API_ROOT = "http://zno-dev.eu-central-1.elasticbeanstalk.com/questions"
QUESTION_URL = urljoin(QUESTIONS_API_ROOT, "/questions/{id}")
CURRENT_PATH = path.dirname(path.realpath(__file__))
ORIGINAL_IMAGE_PATH = path.join(CURRENT_PATH, "original")
FORMATTED_IMAGE_PATH = path.join(CURRENT_PATH, "formatted")
THUMBNAILS_IMAGE_PATH = path.join(CURRENT_PATH, "thumbnails")


def check_dirs():
    if not path.exists(ORIGINAL_IMAGE_PATH):
        makedirs(ORIGINAL_IMAGE_PATH)

    if not path.exists(FORMATTED_IMAGE_PATH):
        makedirs(FORMATTED_IMAGE_PATH)

    if not path.exists(THUMBNAILS_IMAGE_PATH):
        makedirs(THUMBNAILS_IMAGE_PATH)


def load_originals():
    for i in range(0, 12000):
        question_json = requests.get(QUESTION_URL.format(id=i))
        question_dict = json.loads(question_json.content)

        if question_dict.get("image"):
            url = question_dict["image"]
            name = str(i) + path.splitext(url.split("/")[-1])[1]

            urlretrieve(url, path.join(ORIGINAL_IMAGE_PATH, name))


def format_image(filename):
    name = path.splitext(filename.split("\\")[-1])[0]

    try:
        original = Image.open(filename)
    except FileNotFoundError:
        print(f'File "{filename}" not found!')

        return None

    side_size = max(original.size)

    original_width, original_height = original.size

    formatted_image = Image.new("RGB", (side_size, side_size), "white")

    offset = ((side_size - original_width) // 2, (side_size - original_height) // 2)

    formatted_image.paste(original, offset)
    formatted_image.save(path.join(FORMATTED_IMAGE_PATH, name + ".jpg"), "JPEG")


def format_originals():
    tree = walk(ORIGINAL_IMAGE_PATH)

    for address, dirs, files in tree:
        for file in files:
            format_image(path.join(address, file))


def create_thumbnail(filename):
    name = path.splitext(filename.split("\\")[-1])[0]

    try:
        original = Image.open(filename)
    except FileNotFoundError:
        print(f'File "{filename}" not found!')

        return None

    size = (400, 400)

    original.thumbnail(size)
    original.save(path.join(THUMBNAILS_IMAGE_PATH, name + "_thumbnail.jpg"), "JPEG")


def create_thumbnails():
    tree = walk(FORMATTED_IMAGE_PATH)

    for address, dirs, files in tree:
        for file in files:
            create_thumbnail(path.join(address, file))


def main():
    check_dirs()
    # load_originals()
    # format_originals()
    create_thumbnails()


if __name__ == "__main__":
    main()
