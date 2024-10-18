import datetime
from sqlalchemy import Column, Integer, String, BigInteger, ForeignKey, Text, Boolean, VARCHAR
from bot.database.main import Database
from sqlalchemy.orm import relationship


class Permission:
    USE = 1
    BROADCAST = 2
    SETTINGS_MANAGE = 4
    USERS_MANAGE = 8
    SHOP_MANAGE = 16
    ADMINS_MANAGE = 32
    OWN = 64


class Role(Database.BASE):
    __tablename__ = 'roles'
    id = Column(Integer, primary_key=True)
    name = Column(String(64), unique=True)
    default = Column(Boolean, default=False, index=True)
    permissions = Column(Integer)
    users = relationship('User', backref='role', lazy='dynamic')

    def __init__(self, name: str, permissions=None, **kwargs):
        super(Role, self).__init__(**kwargs)
        if self.permissions is None:
            self.permissions = 0
        self.name = name
        self.permissions = permissions

    @staticmethod
    def insert_roles():
        roles = {
            'USER': [Permission.USE],
            'ADMIN': [Permission.USE, Permission.BROADCAST,
                      Permission.SETTINGS_MANAGE, Permission.USERS_MANAGE, Permission.SHOP_MANAGE, ],
            'OWNER': [Permission.USE, Permission.BROADCAST,
                      Permission.SETTINGS_MANAGE, Permission.USERS_MANAGE, Permission.SHOP_MANAGE,
                      Permission.ADMINS_MANAGE,
                      Permission.OWN],
        }
        default_role = 'USER'
        for r in roles:
            role = Database().session.query(Role).filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.reset_permissions()
            for perm in roles[r]:
                role.add_permission(perm)
            role.default = (role.name == default_role)
            Database().session.add(role)
        Database().session.commit()

    def add_permission(self, perm):
        if not self.has_permission(perm):
            self.permissions += perm

    def remove_permission(self, perm):
        if self.has_permission(perm):
            self.permissions -= perm

    def reset_permissions(self):
        self.permissions = 0

    def has_permission(self, perm):
        return self.permissions & perm == perm

    def __repr__(self):
        return '<Role %r>' % self.name


class User(Database.BASE):
    __tablename__ = 'users'
    telegram_id = Column(BigInteger, nullable=False, unique=True, primary_key=True)
    role_id = Column(Integer, ForeignKey('roles.id'), default=1)
    balance = Column(BigInteger, nullable=False, default=0)
    referral_id = Column(BigInteger, nullable=True)
    registration_date = Column(VARCHAR, nullable=False)
    user_operations = relationship("Operations", back_populates="user_telegram_id")
    user_unfinished_operations = relationship("UnfinishedOperations", back_populates="user_telegram_id")

    def __init__(self, telegram_id: int, registration_date: datetime.datetime, balance: int = 0,
                 referral_id=None, role_id: int = 1):
        self.telegram_id = telegram_id
        self.role_id = role_id
        self.balance = balance
        self.referral_id = referral_id
        self.registration_date = registration_date


class Categories(Database.BASE):
    __tablename__ = 'categories'
    name = Column(String(100), primary_key=True, unique=True, nullable=False)

    def __init__(self, name: str):
        self.name = name


class Goods(Database.BASE):
    __tablename__ = 'goods'
    name = Column(String(100), nullable=False, unique=True, primary_key=True)
    price = Column(BigInteger, nullable=False)
    description = Column(Text, nullable=False)
    category_name = Column(String(100), nullable=False)

    def __init__(self, name: str, price: int, description: str, category_name: str):
        self.name = name
        self.price = price
        self.description = description
        self.category_name = category_name


class ItemValues(Database.BASE):
    __tablename__ = 'item_values'
    id = Column(Integer, nullable=False, primary_key=True)
    item_name = Column(String(100), nullable=False)
    value = Column(Text, nullable=True)
    is_infinity = Column(Boolean, nullable=False)

    def __init__(self, name: str, value: str, is_infinity: bool):
        self.item_name = name
        self.value = value
        self.is_infinity = is_infinity


class BoughtGoods(Database.BASE):
    __tablename__ = 'bought_goods'
    id = Column(Integer, nullable=False, primary_key=True)
    item_name = Column(String(100), nullable=False)
    value = Column(Text, nullable=False)
    price = Column(BigInteger, nullable=False)
    buyer_id = Column(BigInteger, nullable=False, default=0)
    bought_datetime = Column(VARCHAR, nullable=False)
    unique_id = Column(BigInteger, nullable=False, unique=True)

    def __init__(self, name: str, value: str, price: int, bought_datetime: datetime.datetime, unique_id,
                 buyer_id: int = 0):
        self.item_name = name
        self.value = value
        self.price = price
        self.buyer_id = buyer_id
        self.bought_datetime = bought_datetime
        self.unique_id = unique_id


class Operations(Database.BASE):
    __tablename__ = 'operations'
    id = Column(Integer, nullable=False, primary_key=True)
    user_id = Column(BigInteger, ForeignKey('users.telegram_id'), nullable=False)
    operation_value = Column(BigInteger, nullable=False)
    operation_time = Column(VARCHAR, nullable=False)
    user_telegram_id = relationship("User", back_populates="user_operations")

    def __init__(self, user_id: int, operation_value: int, operation_time: datetime.datetime):
        self.user_id = user_id
        self.operation_value = operation_value
        self.operation_time = operation_time


class UnfinishedOperations(Database.BASE):
    __tablename__ = 'unfinished_operations'
    id = Column(Integer, nullable=False, primary_key=True)
    user_id = Column(BigInteger, ForeignKey('users.telegram_id'), nullable=False)
    operation_value = Column(BigInteger, nullable=False)
    operation_id = Column(String(500), nullable=False)
    user_telegram_id = relationship("User", back_populates="user_unfinished_operations")

    def __init__(self, user_id: int, operation_value: int, operation_id: str):
        self.user_id = user_id
        self.operation_value = operation_value
        self.operation_id = operation_id


class Configuration(Database.BASE):
    __tablename__ = 'configuration'
    key = Column(String(50), primary_key=True)
    value = Column(Text)

    def __init__(self, key: str, value: str):
        self.key = key
        self.value = value


def register_models():
    Database.BASE.metadata.create_all(Database().engine)
    Role.insert_roles()
