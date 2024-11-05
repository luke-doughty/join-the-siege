from werkzeug.datastructures import FileStorage

import os
import json


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


def classify_file(file: FileStorage, is_image: bool):
    """Return the file classification

    Takes in a file and uses hugging face inference on the file
    """
    catagories = get_catagories()
    filename = file.filename.lower()

    if (is_image):
        # parse file_name into classifier image classifier
        return
    if (not is_image):
        # parse file_name into string classifer
        return
    file_contents = file.stream.read()

    if "drivers_license" in filename:
        return "drivers_licence"

    if "bank_statement" in filename:
        return "bank_statement"

    if "invoice" in filename:
        return "invoice"

    return "unknown file"

# TODO:
# if an image or a video, only use file name - write why ive done this
# (training an image document classifier beyond this scope)
# otherwise parse a document (define a list of document types allowed)
# use zero shot document classifier on documents
# use zero shot on document name aswell, assume document name overrides inner document
# potentially make an endpoint that can accuracy aswell
# make more tests
#
