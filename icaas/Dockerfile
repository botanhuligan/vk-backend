FROM python:3
ENV PYTHONUNBUFFERED 1
RUN mkdir app
WORKDIR /app
ADD . /app

RUN pip3 install -r icaas/local_requirements.txt

CMD python3 icaas/web_app.py