from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Backend is running"}

def test_add_class():
    response = client.post("/model/classes/add", params={"label": "test", "number_of_images": 5})
    assert response.status_code == 200
    assert response.json() == {"message": "Class test added 5 images successfully"}

def test_delete_class():
    response = client.post("/model/classes/delete", params={"label": "test"})
    assert response.status_code == 200
    assert response.json() == {"message": "Class test deleted successfully"}

def test_update_class():
    response = client.post("/model/classes/update", params={"oldlabel": "test", "newlabel": "test2"})
    assert response.status_code == 200
    assert response.json() == {"message": "Class test changed to test2 successfully"}

def test_get_classes():
    response = client.get("/model/classes")
    assert response.status_code == 200
    assert response.json() == {"classes": ["test2"]}

def test_train_model():
    response = client.post("/model/train", params={"batch_size": 16, "epochs": 5})
    assert response.status_code == 200
    assert response.json() == {"message": "Model training started"}

