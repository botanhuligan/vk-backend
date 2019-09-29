"""
Image Classification Service
"""
import io
import os
import numpy as np
import logging
import flask
from decouple import config
import requests
from typing import List

from pymongo import MongoClient
from sklearn.neighbors import KNeighborsClassifier
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications import ResNet50
from tensorflow.keras.applications.resnet50 import preprocess_input

log = logging.getLogger(__name__)
logging.basicConfig(
    format='%(levelname)s: [%(asctime)s.%(msecs)03d] {} %(name)s '
 '%(filename)s:%(funcName)s:%(lineno)s: %(message)s'.format("IMAGE_CLASSIFIER_WEB_SERVICE"),
 datefmt='%Y-%m-%d %H:%M:%S', level="DEBUG")

CLASSIFIER = "CLASSIFIER"
IMAGE_FOLDER = "images"
IMAGE_IDS = "ConstituentID"
IMAGES_CSV_URL = "https://media.githubusercontent.com/media/MuseumofModernArt/collection/master"
URL_HEADER = "ThumbnailURL"

DOC_IDS = "_id"
DOC_EXTERNAL_IDS = "external_ids"
DOC_IMG = 'img'


def dir_exists(path: str):
    if os.path.exists(path):
        return
    os.mkdir(path)

def process_image(image_path: str):
    log.debug("process_image: processing image")
    img = image.load_img(image_path, target_size=(224, 224))
    x = image.img_to_array(img)
    x = np.expand_dims(x, axis=0)
    log.debug("process_image: returning array")
    return preprocess_input(x)


class Image:
    def __init__(self, ids: str, path: str, embedding: np.ndarray = None):
        self.ids = ids
        self.path = path
        self.embedding = embedding


class ImageClassifier:

    def __init__(self, model_path: str = None, k_neighbors: int = None, knn_weights: str = None,
                 mongo_address: str = None, mongo_port: int = None, db_name: str = None,
                 doc_collection_name: str = None, knn_metric: str = None, knn_jobs: int = None):
        self.images: List[Image] = []
        self.model_path = model_path
        self.k_neighbors = k_neighbors
        self.knn_weights = knn_weights
        self.knn_metric = knn_metric
        self.knn_jobs = knn_jobs
        self.mongo_address = mongo_address
        self.mongo_port = mongo_port
        self.db_name = db_name
        self.doc_collection_name = doc_collection_name
        self._get_settings()
        self.connection, self.doc_collection = self._get_connection()
        self._get_knn_classifier()
        self._get_vector_model()
        self._load_model()
        self._load_data()

    def _get_settings(self):
        if not self.mongo_address:
            log.info("LOADING ENV SETTING IC_MONGO_ADDRESS")
            self.mongo_address = config('IC_MONGO_ADDRESS', default="", cast=str)
        if not self.mongo_port:
            log.info("LOADING ENV SETTING IC_MONGO_ADDRESS")
            self.mongo_port = config('IC_MONGO_PORT', default="27017", cast=int)
        if not self.db_name:
            log.info("LOADING ENV SETTING IC_MONGO_DB_NAME")
            self.db_name = config('IC_MONGO_DB_NAME', default="pushkin", cast=str)
        if not self.doc_collection_name:
            log.info("LOADING ENV SETTING IC_MONGO_DOC_COLLECTION_NAME")
            self.doc_collection_name = config('IC_DOC_MONGO_COLLECTION_NAME', default="art", cast=str)
        if not self.model_path:
            log.info("LOADING ENV SETTING I2V_MODEL_PATH")
            self.model_path = config('I2V_MODEL_PATH', default="model.json", cast=str)
        if not self.k_neighbors:
            log.info("LOADING ENV SETTING I2V_KNN_K_NEIGHBORS")
            self.k_neighbors = config('I2V_KNN_K_NEIGHBORS', default="1", cast=int)
        if not self.knn_weights:
            log.info("LOADING ENV SETTING I2V_KNN_WEIGHTS")
            self.knn_weights = config('I2V_KNN_WEIGHTS', default="uniform", cast=str)
        if not self.knn_metric:
            log.info("LOADING ENV SETTING I2V_KNN_METRIC")
            self.knn_metric = config('I2V_KNN_METRIC', default="cosine", cast=str)
        if not self.knn_jobs:
            log.info("LOADING ENV SETTING IC_KNN_JOBS")
            self.knn_jobs = config('I2V_KNN_JOBS', default="10", cast=int)
        self.image_folder = os.path.join(os.path.dirname(__file__), IMAGE_FOLDER)
        dir_exists(self.image_folder)

    def _get_connection(self):
        """
        Подключение к базу данных MongoDB
        :return:
        """
        log.debug("_get_connection: IN")
        connection = MongoClient(self.mongo_address, self.mongo_port)
        doc_collection = connection[self.db_name][self.doc_collection_name]
        log.debug("_get_connection: DB CONNECTED")
        return connection, doc_collection

    def _load_model(self):
        try:
            self.model = load_model(filepath=self.model_path)
        except (OSError, FileNotFoundError):
            self.model = None

    def download_image(self, url: str, image_name: str):
        if 'jpg' not in image_name:
            return None
        response = requests.get(url)
        if not response.ok:
            log.debug("download_image: Bad response")
            return None
        with open(os.path.join(self.image_folder, image_name + '.jpg'), "wb") as stream:
            log.debug("download_image: saving_file")
            for chunk in response:
                stream.write(chunk)
        log.debug("download_image: returning path")
        return os.path.join(self.image_folder, image_name + '.jpg')

    def _load_data(self):
        log.info("_load_data: IN")
        for artifact in self.doc_collection.find():
            my_img = self.download_image(artifact[DOC_IMG], artifact[DOC_EXTERNAL_IDS])
            if not my_img:
                log.info("_load_data: ARTIFACT WITH BAD IMAGE")
                continue
            self.images.append(Image(
                ids=artifact[DOC_EXTERNAL_IDS],
                path=artifact[DOC_IMG],
                embedding=self.vector_model(process_image(my_img))
            ))
            log.info("_load_data: ADDED IMAGE: " + str(artifact[DOC_EXTERNAL_IDS]))
        self._fit_knn()

    def _fit_knn(self):
        X = []
        Y = []
        if not self.images:
            return
        for img in self.images:
            if not img.embedding:
                continue
            if not img.ids:
                continue
            X.append(img.embedding)
            Y.append(img.ids)
        X = np.array(X)
        Y = np.array(Y)
        print("X.shapes: ", X.shape)
        print("Y.shapes: ", Y.shape)
        self.image_knn_classifier.fit(X, Y)

    def _get_knn_classifier(self):
        self.image_knn_classifier = KNeighborsClassifier(
            n_neighbors=self.k_neighbors,
            weights=self.knn_weights,
            metric=self.knn_metric,
            n_jobs=self.knn_jobs
        )

    def _get_vector_model(self):
        self.vector_model = ResNet50(include_top=True, weights='imagenet')

    def _predict_image(self, img: np.ndarray):
        log.info("predict_image: Predicting vector")
        vector = self.vector_model.predict(img)
        log.info("predict_image: Upgrade image vector")
        if self.model:
            vector = self.model.predict(vector) # Пока не будет обучена промежуточная модель - шаг будет пропускатсья
        result = self.image_knn_classifier.predict(vector)[0]
        result = dict(self.doc_collection.find_one({DOC_EXTERNAL_IDS: result}))
        result.pop(DOC_IDS)
        return result

    def predict(self, file_path: str):
        img = process_image(file_path)
        return self._predict_image(img)


app = flask.Flask(__name__)
app.config[CLASSIFIER] = ImageClassifier()
app.config["I2V_HOST"] = config("I2V_HOST", default="0.0.0.0", cast=str)
app.config["I2V_PORT"] = config("I2V_PORT", default="9918", cast=int)



@app.route("/get_data", methods=["POST"])
def get_image_data():
    img = flask.request.files.get("image")
    if not img:
        return "Image empty", 401
    path = os.path.join(app.config[CLASSIFIER].image_folder, 'to_do_image.jpg')
    img.save(path)
    return app.config[CLASSIFIER].predict(path), 200


if __name__ == '__main__':
    app.run(app.config["I2V_HOST"], app.config["I2V_PORT"], debug=True)
