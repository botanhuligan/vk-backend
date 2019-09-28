"""
  Сервис для запуска берта РУЧКАМИ зоть и с либой bert_as_a_service
"""
import os
import logging
from bert_serving.server import BertServer
from bert_serving.server.helper import get_args_parser
from decouple import config
log = logging.getLogger(__name__)

# RUBERT_LINK = "http://files.deeppavlov.ai/deeppavlov_data/bert/rubert_cased_L-12_H-768_A-12_v2.tar.gz"
# ZIP_FILE = "bert_compressed.tar.gz"
# RU_BERT_INNER_FOLDER = ""


# def exists_bert(dir_path: str):
#     """
#     Функция для инициализации - проверяет наличие директории с бертом и производит автоматическу загрузку
#     :param dir_path:
#     :return:
#     """
#     log.info("PARSING DIR: " + str(dir_path))
#     try:
#         os.mkdir(dir_path)
#     except FileExistsError:
#         log.info("DIRECTORY EXISTS")
#     log.info("DIRECTORY [" + str(dir_path) + "] already exists")
#     log.info("DIRECTORY [" + str(dir_path) + "] have been created")
#     log.info("LOADING_BERT")
#     if len(os.listdir(dir_path)) > 0:
#         return
#     if not os.path.exists(ZIP_FILE):
#         with open(ZIP_FILE, 'wb') as output_file, requests.get(RUBERT_LINK, stream=True) as response:
#             if not response.ok:
#                 raise LoadingBertModelException()
#             shutil.copyfileobj(response.raw, output_file)
#     log.info("BERT DOWNLOADED")
#     try:
#         with tarfile.open(ZIP_FILE, "r") as tar_ref:
#             subdir_and_files = [
#                 tarinfo for tarinfo in tar_ref.getmembers()
#                 if tarinfo.name.startswith("subfolder/")
#             ]
#             print(subdir_and_files)
#             tar_ref.extractall(members=subdir_and_files)
#     except EOFError:
#         pass
#     log.info("BERT DECOMPRESSED")


def run_bert():
    log.info("SETTING UP BERT")
    print("DEBUG!")
    for item in os.listdir("."):
        print(item)
    logging.info("CHECKING RU-BERT FILES")
    # exists_bert(config('BERT_MODEL_DIR', default="bert", cast=str)) # Пока качаем ручками
    args = get_args_parser().parse_args([
        '-model_dir', config('BERT_MODEL_DIR', default="rubert_cased_L-12_H-768_A-12_v2", cast=str),
        '-port', config('BERT_PORT_IN', default="5555", cast=str),
        '-port_out', config('BERT_PORT_OUT', default="5556", cast=str),
        '-max_seq_len', config('BERT_MAX_SEQ', default="None", cast=str),
        '-num_worker', config('BERT_WORKERS', default="1", cast=str),
        '-cpu'
    ])
    log.info("STARTING WITH ARGS: ", str(args))
    bert = BertServer(args)
    log.info("START SERVING")
    bert.start()


if __name__ == '__main__':
    log.info("RUNNING MAIN SCRIPT")
    run_bert()