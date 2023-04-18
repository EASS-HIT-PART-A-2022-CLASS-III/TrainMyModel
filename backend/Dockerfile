FROM python:latest

WORKDIR /usr/src/backend

# COPY ./requirements.txt .
COPY . .

RUN pip install --no-cache-dir --upgrade -r requirements.txt


CMD ["uvicorn", "main:app", "--reload", "--host", "0.0.0.0","--port", "8001"]