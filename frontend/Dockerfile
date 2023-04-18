# FROM python:latest

# WORKDIR /code

# # COPY .code/requirements.txt .
# COPY . .

# RUN pip install --no-cache-dir --upgrade -r code/requirements.txt


# EXPOSE 8000
# RUN echo "Hi"
# RUN pwd

# ENTRYPOINT ["streamlit", "run","code/main.py","--server.port=8000", "--server.address=0.0.0.0"]
# CMD ["code/main.py"]

# app/Dockerfile

FROM python:3.9-slim

WORKDIR /usr/src/frontend

# COPY requirements.txt .

COPY . .

RUN pip install --no-cache-dir --upgrade -r requirements.txt

EXPOSE 8000

# HEALTHCHECK CMD curl --fail http://localhost:8000/_stcore/health

ENTRYPOINT ["streamlit", "run", "main.py", "--server.port=8000", "--server.address=0.0.0.0"]