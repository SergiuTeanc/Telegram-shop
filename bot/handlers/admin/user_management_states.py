import datetime

from aiogram import Dispatcher
from aiogram.types import Message, CallbackQuery
from aiogram.utils.exceptions import BotBlocked

from bot.keyboards import back, user_manage_check, user_management, user_items_list, close
from bot.database.methods import check_role, check_user, select_user_operations, select_user_items, \
    check_role_name_by_id, check_user_referrals, select_bought_items, set_role, create_operation, update_balance, \
    bought_items_list
from bot.misc import TgConfig
from bot.database.models import Permission
from bot.handlers.other import get_bot_user_ids
from bot.logger_mesh import logger


async def user_callback_handler(call: CallbackQuery):
    bot, user_id = await get_bot_user_ids(call)
    TgConfig.STATE[f'{user_id}_message_id'] = call.message.message_id
    TgConfig.STATE[user_id] = 'user_id_for_check'
    role = check_role(user_id)
    if role >= Permission.USERS_MANAGE:
        await bot.edit_message_text('👤 Введите id пользователя,\nчтобы посмотреть | изменить его данные',
                                    chat_id=call.message.chat.id,
                                    message_id=call.message.message_id,
                                    reply_markup=back('console'))
        return
    await call.answer('Недостаточно прав')


async def check_user_data(message: Message):
    bot, user_id = await get_bot_user_ids(message)
    msg = message.text
    TgConfig.STATE[user_id] = None
    message_id = TgConfig.STATE.get(f'{user_id}_message_id')
    user = check_user(msg)
    await bot.delete_message(chat_id=message.chat.id,
                             message_id=message.message_id)
    if not message.text.isdigit():
        await bot.edit_message_text(chat_id=message.chat.id,
                                    message_id=message_id,
                                    text='⚠️ Введите корректный числовой ID пользователя.',
                                    reply_markup=back('console'))
        return
    if not user:
        await bot.edit_message_text(chat_id=message.chat.id,
                                    message_id=message_id,
                                    text='❌ Профиль недоступен (такого пользователя никогда не существовало)',
                                    reply_markup=back('console'))
        return
    await bot.edit_message_text(chat_id=message.chat.id,
                                message_id=message_id,
                                text=f"Вы точно хотите посмотреть профиль пользователя {user.telegram_id}?",
                                parse_mode='HTML',
                                reply_markup=user_manage_check(user.telegram_id))


async def user_profile_view(call: CallbackQuery):
    user_id = call.data[11:]
    bot, admin_id = await get_bot_user_ids(call)
    TgConfig.STATE[user_id] = None
    TgConfig.STATE[f'{admin_id}_user_data'] = user_id
    user = check_user(user_id)
    admin_permissions = check_role(admin_id)
    user_permissions = check_role(user_id)
    user_info = await bot.get_chat(user_id)
    operations = select_user_operations(user_id)
    overall_balance = 0
    if operations:
        for i in operations:
            overall_balance += i
    items = select_user_items(user_id)
    role = check_role_name_by_id(user.role_id)
    referrals = check_user_referrals(user.telegram_id)
    await bot.edit_message_text(chat_id=call.message.chat.id,
                                message_id=call.message.message_id,
                                text=f"👤 <b>Профиль</b> — {user_info.first_name}\n\n🆔"
                                     f" <b>ID</b> — <code>{user_id}</code>\n"
                                     f"💳 <b>Баланс</b> — <code>{user.balance}</code> ₽\n"
                                     f"💵 <b>Всего пополнено</b> — <code>{overall_balance}</code> ₽\n"
                                     f"🎁 <b>Куплено товаров</b> — {items} шт\n\n"
                                     f"👤 <b>Реферал</b> — <code>{user.referral_id}</code>\n"
                                     f"👥 <b>Рефералы пользователя</b> — {referrals}\n"
                                     f"🎛 <b>Роль</b> — {role}\n"
                                     f"🕢 <b>Дата регистрации</b> — <code>{user.registration_date}</code>\n",
                                parse_mode='HTML',
                                reply_markup=user_management(admin_permissions,
                                                             user_permissions, Permission.ADMINS_MANAGE, items,
                                                             user_id))


async def user_items_callback_handler(call: CallbackQuery):
    bot, user_id = await get_bot_user_ids(call)
    user_data = call.data[11:]
    role = check_role(user_id)
    if role >= Permission.ADMINS_MANAGE:
        TgConfig.STATE[f'{user_id}_back'] = f'user-items_{user_data}'
        bought_goods = select_bought_items(user_data)
        goods = bought_items_list(user_id)
        max_index = len(goods) // 10
        if len(goods) % 10 == 0:
            max_index -= 1
        keyboard = user_items_list(bought_goods, user_data, f'check-user_{user_data}',
                                   f'user-items_{user_data}', 0, max_index)
        await bot.edit_message_text('Товары пользователя:', chat_id=call.message.chat.id,
                                    message_id=call.message.message_id, reply_markup=keyboard)
        return
    await call.answer('Недостаточно прав')


async def process_admin_for_purpose(call: CallbackQuery):
    bot, user_id = await get_bot_user_ids(call)
    user_data = call.data[10:]
    user_info = await bot.get_chat(user_data)
    role = check_role(user_id)
    if role >= Permission.ADMINS_MANAGE:
        set_role(user_data, 2)
        await bot.edit_message_text(chat_id=call.message.chat.id,
                                    message_id=call.message.message_id,
                                    text=f'✅ Роль присвоена пользователю {user_info.first_name}',
                                    reply_markup=back(f'check-user_{user_data}'))
        try:
            await bot.send_message(chat_id=user_data,
                                   text='✅ Вам присвоена роль АДМИНИСТРАТОРА бота',
                                   reply_markup=close())
        except BotBlocked:
            pass
        admin_info = await bot.get_chat(user_id)
        logger.info(f"Пользователь {user_id} ({admin_info.first_name}) "
                    f"назначил пользователя {user_data} ({user_info.first_name}) администратором")
        return
    await call.answer('Недостаточно прав')


async def process_admin_for_remove(call: CallbackQuery):
    bot, user_id = await get_bot_user_ids(call)
    user_data = call.data[13:]
    user_info = await bot.get_chat(user_data)
    role = check_role(user_id)
    if role >= Permission.ADMINS_MANAGE:
        set_role(user_data, 1)
        await bot.edit_message_text(chat_id=call.message.chat.id,
                                    message_id=call.message.message_id,
                                    text=f'✅ Роль отозвана у пользователя {user_info.first_name}',
                                    reply_markup=back(f'check-user_{user_data}'))
        try:
            await bot.send_message(chat_id=user_data,
                                   text='❌ У вас отозвана роль АДМИНИСТРАТОРА бота',
                                   reply_markup=close())
        except BotBlocked:
            pass
        admin_info = await bot.get_chat(user_id)
        logger.info(f"Пользователь {user_id} ({admin_info.first_name}) "
                    f"отозвал роль администратора у пользователя {user_data} ({user_info.first_name})")
        return
    await call.answer('Недостаточно прав')


async def replenish_user_balance_callback_handler(call: CallbackQuery):
    bot, user_id = await get_bot_user_ids(call)
    user_data = call.data[18:]
    TgConfig.STATE[f'{user_id}_message_id'] = call.message.message_id
    TgConfig.STATE[user_id] = 'process_replenish_user_balance'
    role = check_role(user_id)
    if role >= Permission.USERS_MANAGE:
        await bot.edit_message_text(chat_id=call.message.chat.id,
                                    message_id=call.message.message_id,
                                    text='💰 Введите сумму для пополнения:',
                                    reply_markup=back(f'check-user_{user_data}'))
        return
    await call.answer('Недостаточно прав')


async def process_replenish_user_balance(message: Message):
    bot, user_id = await get_bot_user_ids(message)
    msg = message.text
    TgConfig.STATE[user_id] = None
    message_id = TgConfig.STATE.get(f'{user_id}_message_id')
    user_data = TgConfig.STATE.get(f'{user_id}_user_data')
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    if not message.text.isdigit() or int(message.text) < 10 or int(message.text) > 10000:
        await bot.edit_message_text(chat_id=message.chat.id,
                                    message_id=message_id,
                                    text="❌ Неверная сумма пополнения. "
                                         "Сумма пополнения должна быть числом не меньше 10₽ и не более 10 000₽",
                                    reply_markup=back(f'check-user_{user_data}'))
        return
    current_time = datetime.datetime.now()
    formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
    create_operation(user_data, msg, formatted_time)
    update_balance(user_data, msg)
    user_info = await bot.get_chat(user_data)
    await bot.edit_message_text(chat_id=message.chat.id,
                                message_id=message_id,
                                text=f'✅ Баланс пользователя {user_info.first_name} пополнен на {msg}₽',
                                reply_markup=back(f'check-user_{user_data}'))
    admin_info = await bot.get_chat(user_id)
    logger.info(f"Пользователь {user_id} ({admin_info.first_name}) "
                f"пополнил баланс пользователя {user_data} ({user_info.first_name}) на {msg}р")
    try:
        await bot.send_message(chat_id=user_data,
                               text=f'✅ Ваш баланс пополнен на {msg}₽',
                               reply_markup=close())
    except BotBlocked:
        pass


def register_user_management(dp: Dispatcher) -> None:
    dp.register_callback_query_handler(user_callback_handler,
                                       lambda c: c.data == 'user_management')

    dp.register_message_handler(process_replenish_user_balance,
                                lambda c: TgConfig.STATE.get(c.from_user.id) == 'process_replenish_user_balance')
    dp.register_message_handler(check_user_data,
                                lambda c: TgConfig.STATE.get(c.from_user.id) == 'user_id_for_check')

    dp.register_callback_query_handler(process_admin_for_remove,
                                       lambda c: c.data.startswith('remove-admin_'))
    dp.register_callback_query_handler(process_admin_for_purpose,
                                       lambda c: c.data.startswith('set-admin_'))
    dp.register_callback_query_handler(replenish_user_balance_callback_handler,
                                       lambda c: c.data.startswith('fill-user-balance_'))
    dp.register_callback_query_handler(user_profile_view,
                                       lambda c: c.data.startswith('check-user_'))
    dp.register_callback_query_handler(user_items_callback_handler,
                                       lambda c: c.data.startswith('user-items_'))
