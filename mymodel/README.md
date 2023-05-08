# TrainMyModel MyModel Service
TrainMyModel is a web app to train a CNN (Convolution Neural Network) deep learning model to clasify between different classes.   
MyModel microservice, is in charge of building, training and predicting with the CNN model.  
MyModel microservice was built using FastApi, and Tensorflow. 

## Requirements
- Docker
- Python 3.9+

## Setup
| :warning:    | Be advised, it is prefered to run the app with docker-compose! |
|---------------|:------------------------|

1. Clone the repository to your local machine.
2. Set the environment variables in the ```.env``` file in the root of the backend dir.  
```ini
SHARED_VOLUME=path/to/shared/volume.  
MYMODEL_URL=http://backend-service:port
```
3. Run the container with:
``` bash
docker build -t train-my-model-mymodel .
docker run -d --name train-my-model-mymodel -p 8002:8002 train-my-model-mymodel
```

## Routes
- `/model` - Classes management routes  
Allowing model functionality:
    - **[GET]** `/load` - Load the model from the shared folder.
    - **[GET]** `/train` - Create the model and start training.
    - **[POST]** `/predict` - Predict an image class using the trained model.
    - **[GET]** `/delete` - Delete class and all images.
    