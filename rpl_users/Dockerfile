FROM python:3.13-slim

WORKDIR /app

COPY ./base_requirements.txt /app/base_requirements.txt
COPY ./rpl_users/extra_requirements.txt /app/extra_requirements.txt

RUN pip install --no-cache-dir --upgrade -r /app/base_requirements.txt -r /app/extra_requirements.txt

COPY ./rpl_users/src /app/src

CMD ["fastapi", "run", "src/main.py", "--port", "80"]