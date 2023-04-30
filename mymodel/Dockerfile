FROM tensorflow/tensorflow:latest

WORKDIR /usr/src/mymodel

COPY . .

RUN apt update && apt install -y graphviz

RUN pip install --no-cache-dir --upgrade -r requirements.txt

CMD ["uvicorn", "main:app", "--reload","--host", "0.0.0.0", "--port", "8002"]