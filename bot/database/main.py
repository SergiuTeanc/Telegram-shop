from typing import Final
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from bot.misc import EnvKeys, SingletonMeta


class Database(metaclass=SingletonMeta):
    BASE: Final = declarative_base()

    def __init__(self):
        db_username = EnvKeys.DB_USERNAME
        db_password = EnvKeys.DB_PASSWORD
        db_host = EnvKeys.DB_HOST
        db_name = EnvKeys.DB_NAME
        self.__engine = create_engine(f'postgresql://{db_username}:{db_password}@{db_host}/{db_name}')
        session = sessionmaker(bind=self.__engine)
        self.__session = session()

    @property
    def session(self):
        return self.__session

    @property
    def engine(self):
        return self.__engine
