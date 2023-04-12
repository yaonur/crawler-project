FROM python:3.11.1-slim-buster

WORKDIR /app

RUN pip install --upgrade pip
RUN pip install -U setuptools
COPY ./requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python","main.py"]