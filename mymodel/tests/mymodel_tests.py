from fastapi.testclient import TestClient
from main import app


def test_root():
    with TestClient(app) as client:
        response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "model is running"}

def test_load_model():
    with TestClient(app) as client:
        response = client.get("/model/load", params={"num_classes": 2})
    assert response.status_code == 200
    assert response.json() == {"message": "model not found"}

def test_train():
    data = {
    'batch_size' : 5,
    'epochs' : 10,
    'optimizer' : "Adam",
    'loss' : "Mean Squared Error",
    'learning_rate' : 0.002,
    'momentum' : 0
    }
    with TestClient(app) as client:
        response = client.get("/model/train", params=data)
    assert response.status_code == 404
    assert response.json() == {"detail": "Dataset not found"}

def test_delete_model():
    with TestClient(app) as client:
        response = client.get("/model/delete")
    assert response.status_code == 400
    assert response.json() == {'detail':"Model not trained"}

