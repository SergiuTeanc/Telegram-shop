from typing import List

import sqlalchemy
from sqlalchemy import cast, Date
from sqlalchemy import exc, func

from bot.database.models import Database, User, ItemValues, Goods, Categories, Configuration, Role, BoughtGoods, \
    Operations, UnfinishedOperations


def check_user(telegram_id: int) -> User | None:
    try:
        return Database().session.query(User).filter(User.telegram_id == telegram_id).one()
    except exc.NoResultFound:
        return None


def check_role(telegram_id: int) -> User | None:
    role_id = Database().session.query(User.role_id).filter(User.telegram_id == telegram_id).one()[0]
    return Database().session.query(Role.permissions).filter(Role.id == role_id).one()[0]


def check_role_name_by_id(role_id: int):
    return Database().session.query(Role.name).filter(Role.id == role_id).one()[0]


def select_max_role_id() -> int:
    return Database().session.query(func.max(Role.id)).scalar()


def select_today_users(date: str) -> int | None:
    try:
        return Database().session.query(User).filter(
            func.date_trunc('day', cast(User.registration_date, Date)) == func.date_trunc('day', cast(date, Date))
        ).count()
    except exc.NoResultFound:
        return None


def get_user_count() -> int:
    return Database().session.query(User).count()


def select_admins() -> int | None:
    try:
        return Database().session.query(func.count()).filter(User.role_id > 1).scalar()
    except exc.NoResultFound:
        return None


def check_channel() -> User | None:
    try:
        return Database().session.query(Configuration.value).filter(Configuration.key == 'channel').scalar()
    except exc.NoResultFound:
        return None


def check_helper() -> str | None:
    try:
        return Database().session.query(Configuration.value).filter(Configuration.key == 'helper').scalar()
    except exc.NoResultFound:
        return None


def check_rules() -> str | None:
    try:
        return Database().session.query(Configuration.value).filter(Configuration.key == 'rules').scalar()
    except exc.NoResultFound:
        return None


def get_all_users() -> list[tuple[int]]:
    return Database().session.query(User.telegram_id).all()


def get_all_categories() -> List[str]:
    return [category[0] for category in Database().session.query(Categories.name).all()]


def get_all_items(category_name: str) -> List[str]:
    return [item[0] for item in
            Database().session.query(Goods.name).filter(Goods.category_name == category_name).all()]


def get_bought_item_info(item_id: str) -> dict | None:
    result = Database().session.query(BoughtGoods).filter(BoughtGoods.id == item_id).first()
    return result.__dict__ if result else None


def get_item_info(item_name: str) -> dict | None:
    result = Database().session.query(Goods).filter(Goods.name == item_name).first()
    return result.__dict__ if result else None


def get_user_balance(telegram_id: int) -> float | None:
    result = Database().session.query(User.balance).filter(User.telegram_id == telegram_id).first()
    return result[0] if result else None


def get_all_admins() -> List[int]:
    return [admin[0] for admin in Database().session.query(User.telegram_id).filter(User.role_id == 'ADMIN').all()]


def check_item(item_name: str) -> dict | None:
    result = Database().session.query(Goods).filter(Goods.name == item_name).first()
    return result.__dict__ if result else None


def check_category(category_name: str) -> dict | None:
    result = Database().session.query(Categories).filter(Categories.name == category_name).first()
    return result.__dict__ if result else None


def get_item_value(item_name: str) -> dict | None:
    result = Database().session.query(ItemValues).filter(ItemValues.item_name == item_name).first()
    return result.__dict__ if result else None


def select_item_values_amount(item_name: str) -> int:
    return Database().session.query(func.count()).filter(ItemValues.item_name == item_name).scalar()


def check_value(item_name: str) -> bool | None:
    try:
        result = False
        values = select_item_values_amount(item_name)
        for i in range(values):
            is_inf = Database().session.query(ItemValues).filter(ItemValues.item_name == item_name).first()
            if is_inf and is_inf.is_infinity:
                result = True
    except exc.NoResultFound:
        return False
    return result


def select_user_items(buyer_id: int) -> int:
    return Database().session.query(func.count()).filter(BoughtGoods.buyer_id == buyer_id).scalar()


def select_bought_items(buyer_id: int) -> list:
    return Database().session.query(BoughtGoods).filter(BoughtGoods.buyer_id == buyer_id).all()


def bought_items_list(buyer_id: int) -> List[str]:
    return [
        item[0] for item in
        Database().session.query(BoughtGoods.item_name).filter(BoughtGoods.buyer_id == buyer_id).all()]


def select_all_users() -> int:
    return Database().session.query(func.count()).filter(User).scalar()


def select_count_items() -> int:
    return Database().session.query(ItemValues).count()


def select_count_goods() -> int:
    return Database().session.query(Goods).count()


def select_count_categories() -> int:
    return Database().session.query(Categories).count()


def select_count_bought_items() -> int:
    return Database().session.query(BoughtGoods).count()


def select_today_orders(date: str) -> float:
    return Database().session.query(func.sum(BoughtGoods.price)).filter(
        func.date_trunc('day', cast(BoughtGoods.bought_datetime, Date)) == func.date_trunc('day', cast(date, Date))
    ).scalar() or 0


def select_all_orders() -> float:
    return Database().session.query(func.sum(BoughtGoods.price)).scalar() or 0


def select_today_operations(date: str) -> float:
    return Database().session.query(func.sum(Operations.operation_value)).filter(
        func.date_trunc('day', cast(Operations.operation_time, Date)) == func.date_trunc('day', cast(date, Date))
    ).scalar() or 0


def select_all_operations() -> float:
    return Database().session.query(func.sum(Operations.operation_value)).scalar() or 0


def select_users_balance() -> float:
    return Database().session.query(func.sum(User.balance)).scalar()


def select_user_operations(user_id: int) -> List[float]:
    return [operation[0] for operation in
            Database().session.query(Operations.operation_value).filter(Operations.user_id == user_id).all()]


def check_group() -> int | None:
    result = Database().session.query(Configuration.value).filter(Configuration.key == 'group_id').first()
    return result[0] if result else None


def check_time() -> int | None:
    result = Database().session.query(Configuration.value).filter(Configuration.key == 'time').first()
    return result[0] if result else None


def select_unfinished_operations(operation_id: str):
    try:
        return Database().session.query(UnfinishedOperations.operation_value).filter(
            UnfinishedOperations.operation_id == operation_id).one()
    except sqlalchemy.exc.NoResultFound:
        return None


def check_user_referrals(user_id: int) -> List[int]:
    return Database().session.query(User).filter(User.referral_id == user_id).count()


def get_user_referral(user_id: int) -> int | None:
    result = Database().session.query(User.referral_id).filter(User.telegram_id == user_id).first()
    return result[0] if result else None
