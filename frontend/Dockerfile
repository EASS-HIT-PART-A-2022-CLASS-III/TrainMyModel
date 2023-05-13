FROM python:3.9-slim

WORKDIR /usr/src/frontend

COPY requirements.txt ./

RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY . .

EXPOSE 8000

ENTRYPOINT ["streamlit", "run", "Homepage.py", "--server.port=8000", "--server.address=0.0.0.0"]