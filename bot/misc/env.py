import os
from abc import ABC
from typing import Final


class EnvKeys(ABC):
    TOKEN: Final = os.environ.get('TOKEN')
    OWNER_ID: Final = os.environ.get('OWNER_ID')
    ACCESS_TOKEN: Final = os.environ.get('ACCESS_TOKEN')
    ACCOUNT_NUMBER: Final = os.environ.get('ACCOUNT_NUMBER')
