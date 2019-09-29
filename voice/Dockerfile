FROM python:3
ENV PYTHONUNBUFFERED 1
RUN mkdir app
WORKDIR /app/voice
ADD . /app

RUN pip3 install -r local_requirements.txt

CMD python3 voice_service.py