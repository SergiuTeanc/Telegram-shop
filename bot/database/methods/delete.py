from bot.database.models import Database, Goods, ItemValues, Configuration, Categories, UnfinishedOperations


def delete_item(item_name) -> None:
    Database().session.query(Goods).filter(Goods.name == item_name).delete()
    Database().session.query(ItemValues).filter(ItemValues.item_name == item_name).delete()
    Database().session.commit()


def delete_category(category_name) -> None:
    goods = Database().session.query(Goods.name).filter(Goods.category_name == category_name).all()
    for item in goods:
        Database().session.query(ItemValues).filter(ItemValues.item_name == item.name).delete()
    Database().session.query(Goods).filter(Goods.category_name == category_name).delete()
    Database().session.query(Categories).filter(Categories.name == category_name).delete()
    Database().session.commit()


def finish_operation(operation_id) -> None:
    Database().session.query(UnfinishedOperations).filter(UnfinishedOperations.operation_id == operation_id).delete()
    Database().session.commit()


def buy_item(item_id) -> None:
    Database().session.query(ItemValues).filter(ItemValues.id == item_id).delete()
    Database().session.commit()


def delete_config(key) -> None:
    Database().session.query(Configuration).filter(Configuration.key == key).delete()
    Database().session.commit()
