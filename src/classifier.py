from werkzeug.datastructures import FileStorage
from transformers import pipeline
from PIL import Image

import os
import json

# Definied Globally so model is only created on startup of each pod in a cluster
text_classifier = pipeline("zero-shot-classification",
                           model="facebook/bart-large-mnli")

image_classifier = pipeline(
    "zero-shot-image-classification", model="google/siglip-so400m-patch14-384")

IMAGE_PASS_RATE = 0.8
FIRST_ATTEMPT_TEXT_PASS_RATE = 0.95
FILE_CONTENT_PASS_RATE = 0.8
TEXT_FAIL_SAFE_PASS_RATE = 0.6


def get_catagories() -> list[str]:
    """Returns classifier catagories from either:

    - CATAGORIES_FILE_PATH  for kuberenetes/prod
    - classifier_catagories.json  for dev
    """
    categories_file = os.getenv(
        "CATEGORIES_FILE_PATH", "classifier_catagories.json")
    with open(categories_file) as file:
        try:
            return json.loads(file.read())['categories']
        except json.JSONDecodeError:
            raise ValueError(f"File '{categories_file}' unreadable")


def classify_file(file: FileStorage, is_image: bool) -> str:
    """Return the file classification

    Takes in a file and uses two different hugging face inferences on it.

    - Image: use image classifier, if fails, use text classifier on file name

    - Text File: use text classifer on filename, if fails, uses same classifer on contents and choses the highest result
    """
    catagories = get_catagories()
    filename = file.filename.lower()

    filename_result = classify_plain_text(filename, catagories)
    if (filename_result[1] > FIRST_ATTEMPT_TEXT_PASS_RATE or is_image):
        return filename_result[0]

    if (is_image):
        image_results = classify_image(file, catagories)
        if (image_results[1] > IMAGE_PASS_RATE):
            return image_results[0]
        if filename_result[1] > TEXT_FAIL_SAFE_PASS_RATE:
            return filename_result[0]
        return "unknown file"

    file_contents = file.stream.read().decode()
    file_contents_result = classify_plain_text(file_contents, catagories)

    if (file_contents_result[1] > FIRST_ATTEMPT_TEXT_PASS_RATE):
        return file_contents_result[0]

    if (file_contents_result[1] > filename_result[1] and file_contents_result[1] > TEXT_FAIL_SAFE_PASS_RATE):
        return file_contents_result[1]

    if (filename_result[1] > file_contents_result[1] and filename_result[1] > TEXT_FAIL_SAFE_PASS_RATE):
        return filename_result[1]

    return "unknown file"


def classify_plain_text(filename: str, labels: list[str]) -> tuple[str, int]:
    '''Returns [classname, confidence] of the most confident response
    '''
    result = text_classifier(filename, candidate_labels=labels)
    return [result['labels'][0], result['scores'][0]]


def classify_image(image: FileStorage, labels: list[str]) -> tuple[str, int]:
    '''Returns [classname, confidence] of the most confident response
    '''
    image_file = Image.open(image)
    result = image_classifier(image_file, candidate_labels=labels)
    return [result[0]['label'], result[0]['score']]
