from aiogram import Dispatcher
from aiogram.types import Message, CallbackQuery

from bot.database.models import Permission
from bot.keyboards import setting, back, reset_config
from bot.database.methods import check_role, delete_config, check_channel, update_config, create_config, check_helper, \
    check_rules, check_group
from bot.misc import TgConfig
from bot.logger_mesh import logger
from bot.handlers.other import get_bot_user_ids


async def settings_callback_handler(call: CallbackQuery):
    bot, user_id = await get_bot_user_ids(call)
    TgConfig.STATE[user_id] = None
    role = check_role(user_id)
    if role >= Permission.SETTINGS_MANAGE:
        await bot.edit_message_text('⛩️ Меню управления настройками',
                                    chat_id=call.message.chat.id,
                                    message_id=call.message.message_id,
                                    reply_markup=setting())
        return
    await call.answer('Недостаточно прав')


async def reset_config_callback_handler(call: CallbackQuery):
    bot, user_id = await get_bot_user_ids(call)
    key = call.data[6:]
    TgConfig.STATE[user_id] = None
    role = check_role(user_id)
    if role >= Permission.SETTINGS_MANAGE:
        delete_config(key)
        await bot.edit_message_text(f'✅ {key} сброшен',
                                    chat_id=call.message.chat.id,
                                    message_id=call.message.message_id,
                                    reply_markup=back('settings'))
        user_info = await bot.get_chat(user_id)
        logger.info(f"{key} был сброшен пользователем {user_id} ({user_info.first_name})")
        return
    await call.answer('Недостаточно прав')


async def upd_channel_callback_handler(call: CallbackQuery):
    bot, user_id = await get_bot_user_ids(call)
    TgConfig.STATE[f'{user_id}_message_id'] = call.message.message_id
    TgConfig.STATE[user_id] = 'upd_channel'
    if check_channel():
        keyboard = reset_config('channel')
    else:
        keyboard = back("settings")
    role = check_role(user_id)
    if role >= Permission.SETTINGS_MANAGE:
        await bot.edit_message_text(
            'Введите ссылку на канал для добавления\nНапример <s>https://t.me/</s> <u>1a2b3c4d5e6f7g8h</u>\n'
            'Перед этим назначьте бота администратором канала, бот будет проверять, '
            'подписан ли пользователь на данный канал',
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            parse_mode='HTML',
            reply_markup=keyboard)
        return
    await call.answer('Недостаточно прав')


async def process_channel_for_upd(message: Message):
    bot, user_id = await get_bot_user_ids(message)
    TgConfig.STATE[user_id] = None
    message_id = TgConfig.STATE.get(f'{user_id}_message_id')
    await bot.delete_message(chat_id=message.chat.id,
                             message_id=message.message_id)
    if check_channel():
        update_config('channel', message.text)
    else:
        create_config('channel', message.text)
    await bot.edit_message_text(chat_id=message.chat.id,
                                message_id=message_id,
                                text='✅ Канал обновлен',
                                reply_markup=back("settings"))
    user_info = await bot.get_chat(user_id)
    logger.info(f"Канал был обновлен пользователем {user_id} ({user_info.first_name})")


async def upd_helper_callback_handler(call: CallbackQuery):
    bot, user_id = await get_bot_user_ids(call)
    TgConfig.STATE[f'{user_id}_message_id'] = call.message.message_id
    TgConfig.STATE[user_id] = 'upd_helper'
    if check_helper():
        keyboard = reset_config('helper')
    else:
        keyboard = back("settings")
    role = check_role(user_id)
    if role >= Permission.SETTINGS_MANAGE:
        await bot.edit_message_text('Введите никнейм саппорта для добавления\n'
                                    'Например <u>@username</u>',
                                    chat_id=call.message.chat.id,
                                    message_id=call.message.message_id,
                                    parse_mode='HTML',
                                    reply_markup=keyboard)
        return
    await call.answer('Недостаточно прав')


async def process_helper_for_upd(message: Message):
    bot, user_id = await get_bot_user_ids(message)
    TgConfig.STATE[user_id] = None
    message_id = TgConfig.STATE.get(f'{user_id}_message_id')
    await bot.delete_message(chat_id=message.chat.id,
                             message_id=message.message_id)
    if check_helper():
        update_config('helper', message.text)
    else:
        create_config('helper', message.text)
    await bot.edit_message_text(chat_id=message.chat.id,
                                message_id=message_id,
                                text='✅ Саппорт обновлен',
                                reply_markup=back("settings"))
    user_info = await bot.get_chat(user_id)
    logger.info(f"Саппорт был обновлен пользователем {user_id} ({user_info.first_name})")


async def upd_rules_callback_handler(call: CallbackQuery):
    bot, user_id = await get_bot_user_ids(call)
    TgConfig.STATE[f'{user_id}_message_id'] = call.message.message_id
    TgConfig.STATE[user_id] = 'upd_rules'
    if check_rules():
        keyboard = reset_config('rules')
    else:
        keyboard = back("settings")
    role = check_role(user_id)
    if role >= Permission.SETTINGS_MANAGE:
        await bot.edit_message_text('Введите правила для добавления',
                                    chat_id=call.message.chat.id,
                                    message_id=call.message.message_id,
                                    reply_markup=keyboard)
        return
    await call.answer('Недостаточно прав')


async def process_rules_for_upd(message: Message):
    bot, user_id = await get_bot_user_ids(message)
    TgConfig.STATE[user_id] = None
    message_id = TgConfig.STATE.get(f'{user_id}_message_id')
    await bot.delete_message(chat_id=message.chat.id,
                             message_id=message.message_id)
    if check_rules():
        update_config('rules', message.text)
    else:
        create_config('rules', message.text)
    await bot.edit_message_text(chat_id=message.chat.id,
                                message_id=message_id,
                                text='✅ Правила обновлены',
                                reply_markup=back("settings"))
    user_info = await bot.get_chat(user_id)
    logger.info(f"Правила были обновлены пользователем {user_id} ({user_info.first_name})")


async def upd_group_callback_handler(call: CallbackQuery):
    bot, user_id = await get_bot_user_ids(call)
    TgConfig.STATE[f'{user_id}_message_id'] = call.message.message_id
    TgConfig.STATE[user_id] = 'upd_group'
    if check_group():
        keyboard = reset_config('group')
    else:
        keyboard = back("settings")
    role = check_role(user_id)
    if role >= Permission.SETTINGS_MANAGE:
        await bot.edit_message_text('Введите ID группы для обновления\n Например <u>-988765433</u>\n '
                                    'Перед этим добавьте бота в группу. '
                                    'При поступлении товаров бот будет сообщать об этом в группе, например:\n'
                                    '🎁 Залив\n'
                                    '🏷️ Товар: *<b>Item</b>*\n'
                                    '📦 Количество: *<b>number</b>*',
                                    chat_id=call.message.chat.id,
                                    message_id=call.message.message_id,
                                    parse_mode='HTML',
                                    reply_markup=keyboard)
        return
    await call.answer('Недостаточно прав')


async def process_group_for_upd(message: Message):
    bot, user_id = await get_bot_user_ids(message)
    TgConfig.STATE[user_id] = None
    message_id = TgConfig.STATE.get(f'{user_id}_message_id')
    await bot.delete_message(chat_id=message.chat.id,
                             message_id=message.message_id)
    group_link = check_group()
    if not group_link:
        create_config('group_id', message.text)
        await bot.edit_message_text(chat_id=message.chat.id,
                                    message_id=message_id,
                                    text='✅ Группа создана',
                                    reply_markup=back("settings"))
        return
    update_config('group_id', message.text)
    await bot.edit_message_text(chat_id=message.chat.id,
                                message_id=message_id,
                                text='✅ Группа обновлена',
                                reply_markup=back("settings"))
    user_info = await bot.get_chat(user_id)
    logger.info(f"Группа была обновлена пользователем {user_id} ({user_info.first_name})")


def register_settings(dp: Dispatcher) -> None:
    dp.register_callback_query_handler(settings_callback_handler,
                                       lambda c: c.data == 'settings')
    dp.register_callback_query_handler(upd_channel_callback_handler,
                                       lambda c: c.data == 'channel_data')
    dp.register_callback_query_handler(upd_helper_callback_handler,
                                       lambda c: c.data == 'helper_data')
    dp.register_callback_query_handler(upd_rules_callback_handler,
                                       lambda c: c.data == 'rules_data')
    dp.register_callback_query_handler(upd_group_callback_handler,
                                       lambda c: c.data == 'group_data')

    dp.register_message_handler(process_channel_for_upd,
                                lambda c: TgConfig.STATE.get(c.from_user.id) == 'upd_channel')
    dp.register_message_handler(process_helper_for_upd,
                                lambda c: TgConfig.STATE.get(c.from_user.id) == 'upd_helper')
    dp.register_message_handler(process_rules_for_upd,
                                lambda c: TgConfig.STATE.get(c.from_user.id) == 'upd_rules')
    dp.register_message_handler(process_group_for_upd,
                                lambda c: TgConfig.STATE.get(c.from_user.id) == 'upd_group')

    dp.register_callback_query_handler(reset_config_callback_handler,
                                       lambda c: c.data.startswith('reset_'))
