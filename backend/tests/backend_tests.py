from fastapi.testclient import TestClient
from main import app
from PIL import Image 
import io
import base64

############ PYTESTS TESTS ############
# Testing the CRUD operations for classes management
# Using 'with TestClient' to test the environment variables in the app

def test_root():
    with TestClient(app) as client:
        response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Backend is running"}


def test_get_classes():
    with TestClient(app) as client:
        response = client.get("/classes")
    assert response.status_code == 200
    assert response.json() == []


def test_add_class():
    import numpy as np
    fake_image = np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
    image = Image.fromarray(fake_image)
    image_bytes = io.BytesIO()
    image.save(image_bytes, format='png')
    content = base64.b64encode(image_bytes.getvalue())
    content = content.decode()
    data = {'images':[{'img':content, 'filename':'test.png'}], 'label':'test'}
    with TestClient(app) as client:
        response = client.post(
            "/classes/add", json=data
        )
    assert response.status_code == 200
    assert response.json() == {"message": "Class test added 1 images successfully"}


def test_update_class():
    with TestClient(app) as client:
        response = client.post(
            "/classes/update", params={"oldlabel": "test", "newlabel": "test2"}
        )
    assert response.status_code == 200
    assert response.json() == {
            "message": "Class test changed to test2 successfully"
        }


def test_get_classes_after_update():
    with TestClient(app) as client:
        response = client.get("/classes")
    assert response.status_code == 200
    assert {"name": "test", "samples": 1} not in response.json()
    assert {"name": "test2", "samples": 1} in response.json()


def test_delete_class():
    with TestClient(app) as client:
        response = client.post("/classes/delete", params={"label": "test2"})
    assert response.status_code == 200
    assert response.json() == {"message": "Class test2 deleted successfully"}
