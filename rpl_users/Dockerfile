FROM python:3.13-slim

WORKDIR /

COPY ./base_requirements.txt /rpl_users/base_requirements.txt
COPY ./rpl_users/extra_requirements.txt /rpl_users/extra_requirements.txt

RUN pip install --no-cache-dir --upgrade -r /rpl_users/base_requirements.txt -r /rpl_users/extra_requirements.txt

COPY ./rpl_users/src /rpl_users/src
COPY ./rpl_users/__init__.py /rpl_users/__init__.py


# CMD ["fastapi", "run", "rpl_users/src/main.py", "--port", "80"]
# CMD ["fastapi", "dev", "rpl_users/src/main.py", "--host", "0.0.0.0", "--port", "80", "--reload"]
CMD python3 -m uvicorn rpl_users.src.main:app --host 0.0.0.0 --port 80 --reload --reload-dir rpl_users/src --use-colors
