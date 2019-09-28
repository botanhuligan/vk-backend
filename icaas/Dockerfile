FROM python:3
ENV PYTHONUNBUFFERED 1
RUN mkdir app
ADD . /app
WORKDIR /app/icaas

RUN pip3 install -r local_requirements.txt

ENV BERT_MODEL_DIR rubert_cased_L-12_H-768_A-12_v2

RUN mkdir rubert_cased_L-12_H-768_A-12_v2 -p

RUN ls -a
EXPOSE 7777
RUN wget "http://files.deeppavlov.ai/deeppavlov_data/bert/rubert_cased_L-12_H-768_A-12_v2.tar.gz" && tar xvzf rubert_cased_L-12_H-768_A-12_v2.tar.gz

RUN ls -a
RUN ls rubert_cased_L-12_H-768_A-12_v2

CMD python3 bert_service.py