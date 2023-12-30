from aiogram import Dispatcher, Bot


async def get_bot_user_ids(query):
    bot: Bot = query.bot
    user_id = query.from_user.id
    return bot, user_id


async def check_sub_channel(chat_member):
    return str(chat_member.status) != 'left'


def register_other_handlers(dp: Dispatcher) -> None:
    pass
