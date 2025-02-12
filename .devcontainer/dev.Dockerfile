FROM python:3.13-slim

RUN apt-get update && apt-get install -y \
    git \
    curl \
    wget \
    nano \
    && rm -rf /var/lib/apt/lists/*

COPY base_requirements.txt /tmp/base_requirements.txt
COPY users/extra_requirements.txt /tmp/users_extra_requirements.txt
COPY activities/extra_requirements.txt /tmp/activities_extra_requirements.txt
COPY .devcontainer/extra_requirements.txt /tmp/dev_extra_requirements.txt

RUN pip install --no-cache-dir --upgrade --user -r /tmp/base_requirements.txt -r /tmp/users_extra_requirements.txt -r /tmp/activities_extra_requirements.txt -r /tmp/dev_extra_requirements.txt

