# Train My Model
TrainMyModel is a web app to train a CNN (Convolution Neural Network) deep learning model to clasify between different classes.  
The user defines classes, and add the images to the dataset.  
Using Resnet-v2 as a base model, the model is refined on the user's classes and after the training, can classify new samples!

The app is built using Streamlit and FastAPI in Docker.  

## Installation
1. Clone the repository to your local machine.
2. Make sure Docker is running.
3. Run from the directory ```docker-compose up```.
4. Go to ```localhost:8000``` and have fun.

## Usage
1. Navigate to the Homepage on `localhost:8000`.
2. Define your classes and upload images for each class.
3. Choose training parameters and train the model.
4. Predict class of a new image.

### Requirements
- Docker
- Python 3.9+
