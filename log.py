import logging.config
import os

logging_conf_path = os.path.normpath(
    os.path.join(os.path.dirname(__file__), 'logging.conf'))
logging.config.fileConfig(logging_conf_path)
log = logging.getLogger(__name__)
