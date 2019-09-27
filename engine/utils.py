import yaml
from log import log

NO_NAME_IN_SKILL_YAML = "No name in skill from file {0}"
NO_DEFAULT_STATE = "No default name in skill from file {0}"
USER_NOT_DEFINED = "User is not defined in message"
UNKNOWN_EVENT = "Unknown event: {0}"
INCORRECT_STATE = "Wrong state: {0}"


def read_yaml(filename):
    with open(filename, 'r') as stream:
        try:
            return yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)
