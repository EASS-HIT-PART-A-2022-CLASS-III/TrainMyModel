# TrainMyModel Backend Service
TrainMyModel is a web app to train a CNN (Convolution Neural Network) deep learning model to clasify between different classes.   
The Backend microservice, manages all classes management operations, as well as the integration with the CNN model itself running on a different microservice.  
The backend was built using FastApi.  

## Requirements
- Docker
- Python 3.9+


## Setup
| :warning:    | Be advised, it is prefered to run the app with docker-compose! |
|---------------|:------------------------|

1. Clone the repository to your local machine.
2. Install the dependencies by running ```pip install -r requirements.txt```.
3. set the environment variables in the ```.env``` file in the root of the backend dir.  
```ini
SHARED_VOLUME=path/to/shared/volume.  
MYMODEL_URL=http://model-service:port
```
4. Run the server with ```uvicorn main:app --reload```.

## Routes
- `/classes` - Classes management routes  
Allowing the user CRUD operations for the database management:
    - **[GET]** `/` - Get dataset from the app.
    - **[GET]** `/get_images/{label}` - Get sample images of the class.
    - **[POST]** `/add` - Add images to a new or existing class.
    - **[POST]** `/update` - Update class label.
    - **[POST]** `/delete` - Delete class and all images.
    
- `/model` - model management routes
Allowing the interactions between the user and the model service:
    - **[GET]** `/status` - Get the model status (Not trained, Training, Trained).
    - **[GET]** `/download` - Download model weights after training.
    - **[GET]** `/architecture` - Download model architecture image.
    - **[POST]** `/train` - Start model training.
    - **[POST]** `/predict` - Predict the class of one image.
    - **[GET]** `/delete` - Delete the model.
    