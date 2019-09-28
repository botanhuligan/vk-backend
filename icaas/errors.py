class EmptyKnnClassifierException(Exception):
    BASE_MESSAGE = "KNN Classifier object is empty"

    def __init__(self, message: str = BASE_MESSAGE):
        self.message = message


class LoadingBertModelException(Exception):
    BASE_MESSAGE = "BERT lot loaded"

    def __init__(self, message: str = BASE_MESSAGE):
        self.message = message
