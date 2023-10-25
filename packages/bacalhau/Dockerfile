FROM python:3.10 as build
WORKDIR /app/bacalhau
COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt 


COPY . .

CMD [ "python3", "job_scheduler.py" ]
