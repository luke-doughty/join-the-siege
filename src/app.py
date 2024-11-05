from cgi import FieldStorage
from flask import Flask, request, jsonify
from PIL import Image
from src.classifier import classify_file
from werkzeug.datastructures import FileStorage

app = Flask(__name__)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def is_image_type(file: FileStorage):
    img_type = file.content_type
    return "image" in img_type


@app.route('/classify_file', methods=['POST'])
def classify_file_route():

    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    file_class = ""

    is_image = is_image_type(file)

    file_class = classify_file(file, is_image)

    return jsonify({"file_class": file_class}), 200


if __name__ == '__main__':
    app.run(debug=True)
