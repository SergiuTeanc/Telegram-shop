from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def main_menu(role, channel=None, helper=None) -> InlineKeyboardMarkup:
    inline_keyboard = [
        [
            InlineKeyboardButton('🏪 Магазин', callback_data='shop'),
            InlineKeyboardButton('📜 Правила', callback_data='rules'),
        ],
        [InlineKeyboardButton('👤 Профиль', callback_data='profile')],
    ]
    if helper and channel:
        inline_keyboard.append([
            InlineKeyboardButton('🆘 Поддержка', url=f"https://t.me/{helper.lstrip('@')}"),
            InlineKeyboardButton('ℹ Новостной канал', url=f"https://t.me/{channel}")
        ])
    else:
        if helper:
            inline_keyboard.append([InlineKeyboardButton('🆘 Поддержка', url=f"https://t.me/{helper.lstrip('@')}")])
        if channel:
            inline_keyboard.append(
                [InlineKeyboardButton('ℹ Новостной канал', url=f"https://t.me/{channel}")])
    if role > 1:
        inline_keyboard.append([InlineKeyboardButton('🎛 Панель администратора', callback_data='console')])

    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


def categories_list(list_items, current_index, max_index) -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup()
    page_items = list_items[current_index * 10: (current_index + 1) * 10]
    for name in page_items:
        markup.add(InlineKeyboardButton(text=name, callback_data=f'category_{name}'))
    if max_index > 0:
        buttons = [
            InlineKeyboardButton(text='◀️', callback_data=f'categories-page_{current_index - 1}'),
            InlineKeyboardButton(text=f'{current_index + 1}/{max_index + 1}', callback_data='dummy_button'),
            InlineKeyboardButton(text='▶️', callback_data=f'categories-page_{current_index + 1}')
        ]
        markup.row(*buttons)
    markup.add(InlineKeyboardButton('🔙 Вернуться в меню', callback_data='back_to_menu'))
    return markup


def goods_list(list_items, category_name, current_index, max_index) -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup()
    page_items = list_items[current_index * 10: (current_index + 1) * 10]
    for name in page_items:
        markup.add(InlineKeyboardButton(text=name, callback_data=f'item_{name}'))
    if max_index > 0:
        buttons = [
            InlineKeyboardButton(text='◀️', callback_data=f'goods-page_{category_name}_{current_index - 1}'),
            InlineKeyboardButton(text=f'{current_index + 1}/{max_index + 1}', callback_data='dummy_button'),
            InlineKeyboardButton(text='▶️', callback_data=f'goods-page_{category_name}_{current_index + 1}')
        ]
        markup.row(*buttons)
    markup.add(InlineKeyboardButton('🔙 Вернуться назад', callback_data='shop'))
    return markup


def user_items_list(list_items, data, back_data, pre_back, current_index, max_index) -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup()
    page_items = list_items[current_index * 10: (current_index + 1) * 10]
    for item in page_items:
        markup.add(InlineKeyboardButton(text=item.item_name, callback_data=f'bought-item:{item.id}:{pre_back}'))
    if max_index > 0:
        buttons = [
            InlineKeyboardButton(text='◀️', callback_data=f'bought-goods-page_{current_index - 1}_{data}'),
            InlineKeyboardButton(text=f'{current_index + 1}/{max_index + 1}', callback_data='dummy_button'),
            InlineKeyboardButton(text='▶️', callback_data=f'bought-goods-page_{current_index + 1}_{data}')
        ]
        markup.row(*buttons)
    markup.add(InlineKeyboardButton('🔙 Вернуться назад', callback_data=back_data))
    return markup


def item_info(item_name, category_name) -> InlineKeyboardMarkup:
    inline_keyboard = [
        [InlineKeyboardButton('💰 Купить', callback_data=f'buy_{item_name}')],
        [InlineKeyboardButton('🔙 Вернуться назад', callback_data=f'category_{category_name}')
         ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


def profile(user_items=0) -> InlineKeyboardMarkup:
    inline_keyboard = [
        [InlineKeyboardButton('💸 Пополнить баланс', callback_data='replenish_balance')
         ],
        [InlineKeyboardButton('🎲 Реферальная система', callback_data='referral_system')
         ]
    ]
    if user_items != 0:
        inline_keyboard.append([InlineKeyboardButton('🎁 Купленные товары', callback_data='bought_items')])
    inline_keyboard.append([InlineKeyboardButton('🔙 Вернуться в меню', callback_data='back_to_menu')])
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


def rules() -> InlineKeyboardMarkup:
    inline_keyboard = [
        [InlineKeyboardButton('🔙 Вернуться в меню', callback_data='back_to_menu')
         ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


def console() -> InlineKeyboardMarkup:
    inline_keyboard = [
        [InlineKeyboardButton('⚙️ Управление настройками', callback_data='settings')
         ],
        [InlineKeyboardButton('🏪 Управление магазином', callback_data='shop_management')
         ],
        [InlineKeyboardButton('👥 Управление пользователями', callback_data='user_management')
         ],
        [InlineKeyboardButton('📢 Рассылка', callback_data='send_message')
         ],
        [InlineKeyboardButton('🔙 Вернуться в меню', callback_data='back_to_menu')
         ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


def user_management(admin_role, user_role, admin_manage, items, user_id) -> InlineKeyboardMarkup:
    inline_keyboard = [
        [
            InlineKeyboardButton('💸 Пополнить баланс пользователя', callback_data=f'fill-user-balance_{user_id}')
        ]
    ]
    if items > 0:
        inline_keyboard.append([InlineKeyboardButton('🎁 Купленные товары', callback_data=f'user-items_{user_id}')])
    if admin_role >= admin_manage and admin_role > user_role:
        if user_role == 1:
            inline_keyboard.append(
                [InlineKeyboardButton('⬆️ Назначить администратором', callback_data=f'set-admin_{user_id}')])
        else:
            inline_keyboard.append(
                [InlineKeyboardButton('⬇️ Снять администратора', callback_data=f'remove-admin_{user_id}')])
    inline_keyboard.append([InlineKeyboardButton('🔙 Вернуться назад', callback_data='user_management')])
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


def user_manage_check(user_id) -> InlineKeyboardMarkup:
    inline_keyboard = [
        [InlineKeyboardButton('✅ Да', callback_data=f'check-user_{user_id}')
         ],
        [InlineKeyboardButton('🔙 Вернуться назад', callback_data='user_management')
         ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


def shop_management() -> InlineKeyboardMarkup:
    inline_keyboard = [
        [InlineKeyboardButton('Управление позициями (товарами)', callback_data='goods_management')
         ],
        [InlineKeyboardButton('Управление категориями', callback_data='categories_management')
         ],
        [InlineKeyboardButton('Статистика', callback_data='statistics')
         ],
        [InlineKeyboardButton('🔙 Вернуться назад', callback_data='console')
         ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


def goods_management() -> InlineKeyboardMarkup:
    inline_keyboard = [
        [InlineKeyboardButton('добавить позицию (товар)', callback_data='item-management'),
         InlineKeyboardButton('изменить позицию', callback_data='update_item'),
         InlineKeyboardButton('удалить позицию', callback_data='delete_item')
         ],
        [InlineKeyboardButton('🔙 Вернуться назад', callback_data='shop_management')
         ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


def item_management() -> InlineKeyboardMarkup:
    inline_keyboard = [
        [InlineKeyboardButton('создать позицию', callback_data='add_item'),
         InlineKeyboardButton('добавить товар к существующей', callback_data='update_item_amount'),
         ],
        [InlineKeyboardButton('🔙 Вернуться назад', callback_data='goods_management')
         ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


def categories_management() -> InlineKeyboardMarkup:
    inline_keyboard = [
        [InlineKeyboardButton('добавить категорию', callback_data='add_category'),
         InlineKeyboardButton('изменить категорию', callback_data='update_category'),
         InlineKeyboardButton('удалить категорию', callback_data='delete_category')
         ],
        [InlineKeyboardButton('🔙 Вернуться назад', callback_data='shop_management')
         ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


def close() -> InlineKeyboardMarkup:
    inline_keyboard = [
        [InlineKeyboardButton('Скрыть', callback_data='close')
         ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


def check_sub() -> InlineKeyboardMarkup:
    inline_keyboard = [
        [InlineKeyboardButton('Подписаться', url='https://t.me/Serge_as_the_meaning_of_life')
         ],
        [InlineKeyboardButton('Проверить', callback_data='sub_channel_done')
         ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


def back(callback) -> InlineKeyboardMarkup:
    inline_keyboard = [
        [InlineKeyboardButton('🔙 Вернуться назад', callback_data=callback)
         ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


def setting() -> InlineKeyboardMarkup:
    inline_keyboard = [
        [InlineKeyboardButton('🆘 Изменить саппорта', callback_data='helper_data'),
         InlineKeyboardButton('📜 Изменить правила', callback_data='rules_data')
         ],
        [InlineKeyboardButton('ℹ️ Изменить канал', callback_data='channel_data'),
         InlineKeyboardButton('ℹ️ Изменить группу', callback_data='group_data')],
        [InlineKeyboardButton('🔙 Вернуться назад', callback_data='console')
         ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


def payment_menu(url, label) -> InlineKeyboardMarkup:
    inline_keyboard = [
        [InlineKeyboardButton('Оплатить', url=url)
         ],
        [InlineKeyboardButton('Проверить', callback_data=f'check_{label}')
         ],
        [InlineKeyboardButton('🔙 Вернуться назад', callback_data='replenish_balance')
         ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


def reset_config(key) -> InlineKeyboardMarkup:
    inline_keyboard = [
        [InlineKeyboardButton(f'Сбросить {key}', callback_data=f'reset_{key}')
         ],
        [InlineKeyboardButton('🔙 Вернуться назад', callback_data='settings')
         ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


def question_buttons(question, back_data) -> InlineKeyboardMarkup:
    inline_keyboard = [
        [InlineKeyboardButton('✅ Да', callback_data=f'{question}_yes'),
         InlineKeyboardButton('❌ Нет', callback_data=f'{question}_no')
         ],
        [InlineKeyboardButton('🔙 Вернуться назад', callback_data=back_data)
         ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
