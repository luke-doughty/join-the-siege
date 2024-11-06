from io import BytesIO
from werkzeug.datastructures import FileStorage

import pytest
from src.app import app
from src.classifier import classify_image, classify_plain_text


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.mark.parametrize("filename, expected", [
    ("file.png", True),
    ("file.jpg", True),
    ("file.txt", False),
    ("file", False),
    ("../files/bank_statement.pdf", True),
    ("../files/drivers_license_1.jpg", True)
])
def test_no_file_in_request(client, filename, expected):
    response = client.post('/classify_file')
    assert response.status_code == 400


def test_no_selected_file(client):
    data = {'file': (BytesIO(b""), '')}  # Empty filename
    response = client.post('/classify_file', data=data,
                           content_type='multipart/form-data')
    assert response.status_code == 400


def test_success(client, mocker):
    mocker.patch('src.app.classify_file', return_value='test_class')

    data = {'file': (BytesIO(b"dummy content"), 'file.pdf')}
    response = client.post('/classify_file', data=data,
                           content_type='multipart/form-data')
    assert response.status_code == 200
    assert response.get_json() == {"file_class": "test_class"}


def test_filename_classifier():
    classification = classify_plain_text(
        "../files/bank_statement.pdf", labels=["bank_statement", "invoice"])
    assert classification[0] == "bank_statement"


def test_image_classifier():
    with open("files/drivers_license_1.jpg", 'rb') as img:
        image_file = FileStorage(
            img, filename="files/drivers_license_1.jpg", content_type="image/jpeg")
        classification = classify_image(
            image_file, labels=["drivers_license", "invoice"])
    assert classification[0] == "drivers_license"
