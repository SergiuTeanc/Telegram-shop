import asyncio
from aiogram import Dispatcher
from aiogram.types import Message, CallbackQuery
from aiogram.utils.exceptions import BotBlocked

from bot.keyboards import back, close
from bot.database.methods import check_role, get_all_users
from bot.database.models import Permission
from bot.misc import TgConfig
from bot.logger_mesh import logger
from bot.handlers.other import get_bot_user_ids


async def send_message_callback_handler(call: CallbackQuery):
    bot, user_id = await get_bot_user_ids(call)
    TgConfig.STATE[user_id] = 'waiting_for_message'
    TgConfig.STATE[f'{user_id}_message_id'] = call.message.message_id
    role = check_role(user_id)
    if role >= Permission.BROADCAST:
        await bot.edit_message_text(chat_id=call.message.chat.id,
                                    message_id=call.message.message_id,
                                    text='Отправьте сообщение для рассылки:',
                                    reply_markup=back("console"))
        return
    await call.answer('Недостаточно прав')


async def broadcast_messages(message: Message):
    bot, user_id = await get_bot_user_ids(message)
    user_info = await bot.get_chat(user_id)
    msg = message.text
    message_id = TgConfig.STATE.get(f'{user_id}_message_id')
    TgConfig.STATE[user_id] = None
    await bot.delete_message(chat_id=message.chat.id,
                             message_id=message.message_id)
    users = get_all_users()
    max_users = 0
    for user_row in users:
        max_users += 1
        user_id = user_row[0]
        await asyncio.sleep(0.1)
        try:
            await bot.send_message(chat_id=int(user_id),
                                   text=msg,
                                   reply_markup=close())
        except BotBlocked:
            pass
    await bot.edit_message_text(chat_id=message.chat.id,
                                message_id=message_id,
                                text='Рассылка завершена',
                                reply_markup=back("console"))
    logger.info(f"Пользователь {user_info.id} ({user_info.first_name})"
                f" совершил рассылку. Рассылка была отправлена {max_users} пользователям.")


def register_mailing(dp: Dispatcher) -> None:
    dp.register_callback_query_handler(send_message_callback_handler,
                                       lambda c: c.data == 'send_message')

    dp.register_message_handler(broadcast_messages,
                                lambda c: TgConfig.STATE.get(c.from_user.id) == 'waiting_for_message')
