FROM tensorflow/tensorflow:latest

WORKDIR /usr/src/mymodel

RUN apt update && apt install -y graphviz

COPY requirements.txt ./

RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--reload","--host", "0.0.0.0", "--port", "8002"]