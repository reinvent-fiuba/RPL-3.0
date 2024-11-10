FROM python:3.12-slim

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./src /code/app 

CMD cd /code/app; python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload