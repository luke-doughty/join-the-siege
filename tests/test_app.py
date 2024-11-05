from io import BytesIO
from werkzeug.datastructures import FileStorage

import pytest
from src.app import app, allowed_file
from src.classifier import filename_classifier


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.mark.parametrize("filename, expected", [
    ("file.pdf", True),
    ("file.png", True),
    ("file.jpg", True),
    ("file.txt", False),
    ("file", False),
])
def test_allowed_file(filename, expected):
    assert allowed_file(filename) == expected


def test_no_file_in_request(client):
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
    classification = filename_classifier("bank_statement.jpg")
    assert classification == "bank_statement"


def test_image_classifier():
    image_file = None
    with open('../files/drivers_license_1.jpg', 'r') as img:
        image_file = FileStorage(img)
    classification = filename_classifier(image_file)
    assert classification == "drivers_license"
