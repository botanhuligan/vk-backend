"""
Intent Classification module
"""
import pickle
from pymongo import MongoClient
from sklearn.neighbors import KNeighborsClassifier
from decouple import config
import logging
import numpy as np
from typing import List, Union
from bert_serving.client import BertClient
from icaas.errors import EmptyKnnClassifierException
logging.basicConfig(
    format='%(levelname)s: [%(asctime)s.%(msecs)03d] {} %(name)s '
 '%(filename)s:%(funcName)s:%(lineno)s: %(message)s'.format("Classifier_service"),
 datefmt='%Y-%m-%d %H:%M:%S', level="INFO")
log = logging.getLogger(__name__)
TIMEOUT = 10

DOC_IDS = "_id"
DOC_EXTERNAL_IDS = "external_ids"
DOC_DOCS = "docs"
DOC_EMBEDDINGS = "embeddings"

EVENT_IDS = "_id"
EVENT_NAME = 'name'
EVENT_EMBEDDINGS = 'embeddings'
EVENT_PHRASES = 'phrases'


def id_generator(start_point: int):
    itt = int(start_point)
    while True:
        itt += 1
        yield itt


class Event:
    """
    Описательный класс для Ивентов
    """
    def __init__(self, ids: str, name: str, phrases: List[str], embeddings: Union[List[np.ndarray], None]):
        self.ids = ids
        self.name = name
        self.phrases = phrases
        self.embeddings = embeddings


class TextData:
    """
    Описательный класс для текстовых полей документов
    """
    def __init__(self, text: str, embedding: np.ndarray):
        self.text = text
        self.embedding = embedding

    def __str__(self):
        return self.text


class Document:
    """
    Описательный класс документов
    """

    def __init__(self, ids: int, external_id: Union[int, str, float], docs: List[TextData]):
        self.ids = ids
        self.external_id = external_id
        self.docs = docs

    def __str__(self):
        return "Document ex_ids -> " + str(self.external_id)


class IntentClassifier:
    """
    Класс интент классификатора (только для inference)
    """

    def __init__(self, mongo_address: str = None, mongo_port: int = None, db_name: str = None,
                 doc_collection_name: str = None, event_collection_name: str = None, id_point: int = None,
                 k_neighbors: int = None, knn_weights: str = None, knn_metric: str = None, knn_jobs: int = None,
                 bert_host: str = None, bert_port_in: int = None, bert_port_out: int = None
                 ):
        self.mongo_address = mongo_address
        self.mongo_port = mongo_port
        self.db_name = db_name
        self.doc_collection_name = doc_collection_name
        self.event_collection_name = event_collection_name
        self.id_point = id_point
        self.k_neighbors = k_neighbors
        self.knn_weights = knn_weights
        self.knn_metric = knn_metric
        self.knn_jobs = knn_jobs
        self.bert_host = bert_host
        self.bert_port_in = bert_port_in
        self.bert_port_out = bert_port_out
        self._load_settings()
        self._set_up_documents_knn()
        self._set_up_events()
        self.connection, self.doc_collection, self.events_collection = self._get_connection()
        self.generator = id_generator(self.id_point)
        self.documents: List[Document] = []
        self.events: List[Event] = []
        self._load_documents()
        self._load_events()

    def _get_vector_service(self):
        """
        Метод подключения клиента BERT
        :return:
        """
        self.bert_client = BertClient(
            ip=self.bert_host,
            port=self.bert_port_in,
            port_out=self.bert_port_out,
            timeout=TIMEOUT
        )

    def _load_settings(self):
        """
        Метод догрузки настроек для корректной работы из среды окружения (или .env файла)
        :return:
        """
        log.info("LOADING SETTINGS")
        if not self.mongo_address:
            log.info("LOADING ENV SETTING IC_MONGO_ADDRESS")
            self.mongo_address = config('IC_MONGO_ADDRESS', default="127.0.0.1", cast=str)
        if not self.mongo_port:
            log.info("LOADING ENV SETTING IC_MONGO_ADDRESS")
            self.mongo_port = config('IC_MONGO_PORT', default="27017", cast=int)
        if not self.db_name:
            log.info("LOADING ENV SETTING IC_MONGO_DB_NAME")
            self.db_name = config('IC_MONGO_DB_NAME', default="icaas", cast=str)
        if not self.doc_collection_name:
            log.info("LOADING ENV SETTING IC_MONGO_DOC_COLLECTION_NAME")
            self.doc_collection_name = config('IC_DOC_MONGO_COLLECTION_NAME', default="documents", cast=str)
        if not self.event_collection_name:
            log.info("LOADING ENV SETTING IC_EVENT_MONGO_COLLECTION_NAME")
            self.event_collection_name = config('IC_EVENT_MONGO_COLLECTION_NAME', default="events", cast=str)
        if not self.id_point:
            log.info("LOADING ENV SETTING IC_ID_POINT")
            self.collection_name = config('IC_ID_POINT', default="0", cast=int)
        if not self.k_neighbors:
            log.info("LOADING ENV SETTING IC_KNN_K_NEIGHBORS")
            self.k_neighbors = config('IC_KNN_K_NEIGHBORS', default="10", cast=int)
        if not self.knn_weights:
            log.info("LOADING ENV SETTING IC_KNN_WEIGHTS")
            self.knn_weights = config('IC_KNN_WEIGHTS', default="uniform", cast=str)
        if not self.knn_metric:
            log.info("LOADING ENV SETTING IC_KNN_METRIC")
            self.knn_metric = config('IC_KNN_METRIC', default="cosine", cast=str)
        if not self.knn_jobs:
            log.info("LOADING ENV SETTING IC_KNN_JOBS")
            self.knn_jobs = config('IC_KNN_JOBS', default="10", cast=int)
        if not self.bert_host:
            log.info("LOADING ENV SETTING BERT_HOST_ADDRESS")
            self.bert_host = config('BERT_HOST_ADDRESS', default="127.0.0.1", cast=str)
        if not self.bert_port_in:
            log.info("LOADING ENV SETTING BERT_PORT_IN")
            self.bert_port_in = config('BERT_PORT_IN', default="5555", cast=int)
        if not self.bert_port_out:
            self.bert_port_out = config('BERT_PORT_OUT', default="5556", cast=int)

    def _get_vector(self, string: str) -> np.ndarray:
        """
         Метод для преобразование строки в embedding
        """
        return self.bert_client.encode([string, ])[0]

    def _set_up_documents_knn(self) -> None:
        """
        Метод для инициализации KNN класификатора для документов
        :return: None
        """

        self.documents_knn = KNeighborsClassifier(
            n_neighbors=self.k_neighbors,
            weights=self.knn_weights,
            metric=self.knn_metric,
            n_jobs=self.knn_jobs
        )

    def _set_up_events(self) -> None:
        """
        Метод для инициализации KNN классификатора для ивентов
        :return:
        """
        self.events_knn = KNeighborsClassifier(
            n_neighbors=self.k_neighbors,
            weights=self.knn_weights,
            metric=self.knn_metric,
            n_jobs=self.knn_jobs
        )

    def _load_events_knn(self) -> None:
        """
        Метод для перестройки KNN классификатора иветнов
        :return:
        """
        if not self.events_knn:
            raise EmptyKnnClassifierException()
        X = []  # Привычки Data Science =) Не ругайтесь на формат переменной)
        Y = []  # Привычки Data Science =) Не ругайтесь на формат переменной)
        for event in self.events:
            if not event.embeddings:
                log.warning("_LOAD_EVENT_KNN: EXCEPTION WHEN LOADING ITEM'S EMBEDDING: " + str(event))
                continue
            if not event.name:
                log.warning("_LOAD_EVENT_KNN: EXCEPTION WHEN LOADING ITEM'S NAME: " + str(event))
                continue
            X.append(event.embeddings)
            Y.append(event.name)
        self.events_knn.fit(X, Y)

    def _load_documents_knn(self) -> None:
        """
        Метод для перестройки KNN классификатора документов
        :return:
        """
        if not self.documents_knn:
            raise EmptyKnnClassifierException()
        X = []  # Привычки Data Science =) Не ругайтесь на формат переменной)
        Y = []  # Привычки Data Science =) Не ругайтесь на формат переменной)
        for document in self.documents:
            if not document.docs:
                log.warning("_LOAD_KNN: EXCEPTION WHEN LOADING ITEM'S docs: " + str(document))
                continue
            if not document.external_id:
                log.warning("_LOAD_KNN: EXCEPTION WHEN LOADING ITEM'S EXTERNAL IDS FOR DOCUMENT ID: "
                            + str(document.ids))
                continue
            X.append(np.array(x.embedding for x in document.docs))
            Y.append(np.array(document.external_id).reshape(1, -1))
        self.documents_knn.fit(X, Y)

    def _load_documents(self):
        """
        Метод для предзагрузки документов в локальную коллекцию
        :return:
        """
        for doc in self.doc_collection.find():
            document = Document(
                ids=doc[DOC_IDS],
                external_id=doc[DOC_EXTERNAL_IDS],
                docs=[TextData(text=d, embedding=self._get_vector(d)) for d in doc[DOC_DOCS]],
            )
            self.documents.append(document)
        self._load_documents_knn()

    def _load_events(self):
        """
        Метод для загрузки ивентов в локальную память
        :return:
        """
        for event in self.events_collection.find():
            event = Event(
                ids=event[EVENT_IDS],
                name=event[EVENT_NAME],
                phrases=event[EVENT_PHRASES],
                embeddings=[self._get_vector(ph) for ph in event[EVENT_PHRASES]]
            )
            self.events.append(event)
        self._load_events()

    def _get_connection(self):
        """
        Подключение к базу данных MongoDB
        :return:
        """
        connection = MongoClient(self.mongo_address, self.mongo_port)
        doc_collection = connection[self.db_name][self.doc_collection_name]
        event_collection = connection[self.db_name][self.event_collection_name]
        return connection, doc_collection, event_collection

    def on_stop(self):
        """
        Безопасное отключение ресурсов базы данных. Рекомендовано использовать для
        :return:
        """
        self.connection.close()

    def add_document(self, external_ids: str, docs: List[str], ):
        """
        Добавление документов в память (+ добавление в БД с проверкой на дубликаты)
        Метод проводит векторизацию объектов под капотом
        :return:
        """
        try:
            if not self.doc_collection.find_one({DOC_EXTERNAL_IDS: external_ids}):
                log.info("ADD DOCUMENT: ADDING NEW DOCUMENT TO THE DB")
                document_id = self.doc_collection.insert_one({
                    DOC_EXTERNAL_IDS: external_ids,
                    DOC_DOCS: docs
                }).inserted_id
                document = self.doc_collection.find_one({DOC_IDS: document_id})
            else:
                log.info("ADD DOCUMENT: COLLECTING EXISTING OBJECT FROM DB")
                document = self.doc_collection.find_one({DOC_EXTERNAL_IDS: external_ids})
            log.info("ADD DOCUMENT: ADDING DOCUMENT " + str(document))
            self.documents.append(Document(
                ids=document[DOC_IDS],
                external_id=document[DOC_EXTERNAL_IDS],
                docs=[TextData(d, self._get_vector(d)) for d in document[DOC_DOCS]],
            ))
            self._load_documents_knn()
        except ValueError:
            log.exception("ADD DOCUMENT EXCEPTION", exc_info=True)

    def delete_document(self, doc_id: str, delete_in_db: bool = False) -> None:
        """
        Метод удаления документа из локальной колекции
        :param delete_in_db: (bool) - флаг удаления из базы данных
        :param doc_id: (str) - идентификатор объекта
        :return:
        """
        for document in self.documents:
            if not document.ids == doc_id:
                continue
            log.info("DELETING DOCUMENT: FOUND DOCUMENT, FORCING TO DELETE")
            self.documents.remove(document)
            if delete_in_db:
                self.doc_collection.delete_one({DOC_IDS: doc_id})
            break
        log.warning("DELETING DOCUMENT: DOCUMENT NOT FOUND")
        # Для постоянной работоспособности сервиса, ошибки не имплементируются

    def add_event(self, name: str, phrases: List[str]):
        """
        Метод для добавления ивента
        :return:
        """
        if not self.events_collection.find_one({EVENT_NAME: name}):
            event_id = self.events_collection.insert_one({
                EVENT_NAME: name,
                EVENT_PHRASES: phrases
            }).inserted_id
            event = self.events_collection.find_one({EVENT_IDS: event_id})
        else:
            event = self.events_collection.find_one({EVENT_NAME: name})
        self.events.append(Event(
            ids=event[EVENT_IDS],
            name=event[EVENT_NAME],
            phrases=event[EVENT_PHRASES],
            embeddings=[self._get_vector(ev) for ev in event[EVENT_PHRASES]]
        ))
        self._load_events()

    def delete_event(self):
        pass

    def predict_event(self):
        pass

    def predict_document(self):
        pass

    def predict_all(self):
        pass

if __name__ == '__main__':
    service = IntentClassifier()
