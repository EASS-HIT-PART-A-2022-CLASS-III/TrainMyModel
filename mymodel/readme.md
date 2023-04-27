# TrainMyModel MyModel Service
This is a service that performs compiling, training and prediction on an image classification model.

## Requirements
- Docker
- Python 3.7+

## Setup
1. Clone the repository.
2. Install the necessary packages by running ```pip install -r requirements.txt```.
3. Set the environment variables for the *BACKEND_URL* and *SHARED_VOLUME*.  
*SHARED_VOLUME* should be the path to the shared volume where the images will be stored.   
*BACKEND_URL* should be the URL of the backend service. 
4. Run the service by running ```uvicorn app:app --reload```.