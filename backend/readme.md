# TrainMyModel Backend Service
This is the readme file for the backend service of a CNN Classifier built with FastAPI.  
This service allows you to manage classes and train the model using the shared data volume.

## Requirements
- Docker
- Python 3.7+


## Setup
1. Clone the repository to your local machine.
2. Install the dependencies by running ```pip install -r requirements.txt```.
3. Set the environment variables *SHARED_VOLUME* and *MYMODEL_URL*.  
*SHARED_VOLUME* should be the path to the shared volume where the images will be stored.  
*MYMODEL_URL* should be the URL of the model service.  
4. Run the server with ```uvicorn main:app --reload```.
