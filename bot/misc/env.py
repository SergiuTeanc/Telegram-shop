import os
from abc import ABC
from typing import Final


class EnvKeys(ABC):
    TOKEN: Final = os.environ.get('TOKEN')
    OWNER: Final = os.environ.get('OWNER_ID')
    CLIENT_TOKEN: Final = os.environ.get('ACCESS_TOKEN')
    RECEIVER_TOKEN: Final = os.environ.get('ACCOUNT_NUMBER')
    DB_USERNAME: Final = os.environ.get('DB_OWNER', 'postgres')
    DB_PASSWORD: Final = os.environ.get('DB_PASSWORD')
    DB_HOST: Final = os.environ.get('DB_HOST')
    DB_NAME: Final = os.environ.get('DB_NAME')
