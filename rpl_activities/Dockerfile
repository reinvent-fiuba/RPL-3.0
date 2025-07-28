FROM python:3.13-slim

WORKDIR /

COPY ./base_requirements.txt /rpl_activities/base_requirements.txt
COPY ./rpl_activities/extra_requirements.txt /rpl_activities/extra_requirements.txt

RUN pip install --no-cache-dir --upgrade -r /rpl_activities/base_requirements.txt -r /rpl_activities/extra_requirements.txt

COPY ./rpl_activities/src /rpl_activities/src
COPY ./rpl_activities/__init__.py /rpl_activities/__init__.py



# For development
# CMD ["uvicorn", "rpl_activities.src.main:app", "--host", "0.0.0.0", "--port", "80", "--reload", "--reload-dir", "rpl_activities/src", "--use-colors"]

CMD ["uvicorn", "rpl_activities.src.main:app", "--host", "0.0.0.0", "--port", "80", "--use-colors"]

