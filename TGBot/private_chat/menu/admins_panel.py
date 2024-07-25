from aiogram_dialog import Dialog, Window, DialogManager
from aiogram_dialog.widgets.text import Const
from aiogram_dialog.widgets.kbd import Button, Cancel, Back, SwitchTo, ScrollingGroup, Select
from aiogram_dialog.widgets.text import Format
from TGBot.private_chat.menu import states
from aiogram.types import CallbackQuery, Message
from typing import Any
from aiogram.enums import ContentType
from aiogram_dialog.widgets.input import MessageInput


async def UserCanChangeSettings(chat_id: int, user_id: int):
    moderators = await GroupRepository.get_moderators(chat_id)
    if user_id == moderators.owner_id:
        return True
    if (moderators.moderators is None) or (user_id not in [user.tg_id for user in moderators.moderators]):
        return False
    return True


async def getter_moderators(**_kwargs):
    ctx: DialogManager = _kwargs["dialog_manager"].current_context()
    chat_id = ctx.dialog_data.get("chat_id")
    moderators = (await GroupRepository.get_moderators(int(chat_id))).moderators
    return {
        'moderators': [f"<a href='tg://user?id={moderator.tg_id}'>{moderator.tg_id}</a>" for moderator in moderators]
        } if len(moderators) > 0 \
        else {'moderators': "Модераторы не установлены!"}


async def chats_getter(**_kwargs):
    return await UserRepository.get_moderated_chat(_kwargs['event_context'].chat.id)


async def getter_selected_chat(**_kwargs):
    ctx: DialogManager = _kwargs["dialog_manager"].current_context()
    chat_id = ctx.dialog_data.get("chat_id")
    from_user_id = _kwargs["event_from_user"].id
    result = await GroupRepository.get_group_with_license(int(chat_id))
    ctx.dialog_data.update(current_chat={
        'chat_id': chat_id,
        'hello_message': result.hello_message,
        'moderated_tread': result.moderated_tread
    })
    end_of_license = "Подписка на бота отсутствует!" if result.current_license is None \
        else result.current_license.end_of_license
    is_owner = True if from_user_id == result.owner_id else False
    return {'chat_id': chat_id, 'end_of_license': end_of_license, 'owner': is_owner, 'use_links': result.use_links}


async def getter_hello_message(**_kwargs):
    ctx: DialogManager = _kwargs["dialog_manager"].current_context()
    hello_message = ctx.dialog_data.get("current_chat")['hello_message']
    return {"hello_message": hello_message} if hello_message is not None else {"hello_message": ""}


async def getter_tread_id(**_kwargs):
    ctx: DialogManager = _kwargs["dialog_manager"].current_context()
    chat_id = ctx.dialog_data.get("chat_id")
    moderated_tread = ctx.dialog_data.get("current_chat")['moderated_tread']
    return {
        "moderated_tread": f"https://t.me/c/{chat_id[4:]}/{moderated_tread}"
    } if moderated_tread is not None \
        else {"moderated_tread": "Топик для бота НЕ УСТАНОВЛЕН. Бот отвечает на команды в любом разделе чата."}


async def cancel_command(callback: CallbackQuery, widget: Any, manager: DialogManager):
    print(f"callback: {callback}\nwidget: {widget}\nmanager: {manager}")
    return


async def on_chosen_chat(callback: CallbackQuery, widget: Any, manager: DialogManager, item_id: int):
    await callback.answer(f"был выбран чат  {item_id}")
    ctx = manager.current_context()
    ctx.dialog_data.update(chat_id=item_id)
    await manager.switch_to(states.Settings.CHOICE_SETTING)


async def on_input_text(message: Message, widget: MessageInput, manager: DialogManager):
    ctx = manager.current_context()
    chat_id = int(ctx.dialog_data.get("chat_id"))
    if not await UserCanChangeSettings(chat_id, message.from_user.id):
        return await manager.switch_to(state=states.Settings.START)
    if ctx.state is states.Settings.SET_HELLO_MESSAGE:
        await GroupRepository.set_hello_message(chat_id, message.text)
    elif ctx.state is states.Settings.SET_BOT_TOPIC:
        await GroupRepository.set_moderated_tread(chat_id, int(message.text))
    elif ctx.state is states.Settings.SET_MODERATORS:
        moder = int(message.text)
        if moder > 0:
            result = await GroupRepository.add_user_to_moderators(chat_id, moder)
        else:
            result = await GroupRepository.delete_user_from_moderators(chat_id, -moder)
        if result is None:
            await message.answer("Такого пользователя не существует!")
            return await manager.switch_to(state=ctx.state)
        elif result is False:
            await message.answer("Ошибка при выполнении операции, проверьте вводимые данные!")
            return await manager.switch_to(state=ctx.state)

    return await manager.switch_to(state=states.Settings.CHOICE_SETTING)


async def on_reset_button(callback: CallbackQuery, widget: Any, manager: DialogManager):
    ctx = manager.current_context()
    chat_id = int(ctx.dialog_data.get("chat_id"))
    match widget.widget_id:
        case "reset_hello_message":
            await GroupRepository.set_hello_message(chat_id, None)
        case "reset_moderated_tread":
            await GroupRepository.set_moderated_tread(chat_id, None)
    return await manager.switch_to(state=states.Settings.CHOICE_SETTING)

admin_panel = Dialog(
    Window(
        Const("Выберите чат для настройки:"),
        ScrollingGroup(
            Select(
                Format("{item.chat_id}"),
                id="scroll_chats",
                item_id_getter=lambda x: x.chat_id,
                items="chats",
                on_click=on_chosen_chat,
            ),
            id="chats_ids",
            width=1,
            height=6,
        ),
        Cancel(Const("Назад")),
        state=states.Settings.START,
        getter=chats_getter
        ),
    Window(
        Format(
            "Выбран чат {chat_id}.\nДата окончания подписки: {end_of_license}\n"
            "Выберите настройку чата, которую хотите изменить."
        ),
        SwitchTo(Const("Приветственное сообщение"), id="set_hello_msg", state=states.Settings.SET_HELLO_MESSAGE),
        SwitchTo(Const("Топик для бота"), id="set_topic", state=states.Settings.SET_BOT_TOPIC),
        SwitchTo(Const("Модераторы бота"), id="set_moderators", state=states.Settings.SET_MODERATORS, when='owner'),
        Back(Const("<< Меню выбора чата")),
        state=states.Settings.CHOICE_SETTING,
        getter=getter_selected_chat
    ),
    Window(
        Format(
            "Сейчас установлено приветственное сообщение:\n"
            "-------------\n"
            "*Привет, {event.from_user.full_name}, добро пожаловать в чат!*\n"
            "{hello_message}\n"
            "-------------\n\n"
            "Область, заключённая в '*' изменяться не будет! "
            "Введите сообщение, которое будут получать пользователи вступившие в ваш чат."),
        Button(Const("Сбросить"), id="reset_hello_message", on_click=on_reset_button),
        SwitchTo(Const("Назад"), id="back_to_choice_settings", state=states.Settings.CHOICE_SETTING),
        MessageInput(content_types=[ContentType.TEXT], func=on_input_text),
        state=states.Settings.SET_HELLO_MESSAGE,
        getter=getter_hello_message
    ),
    Window(
        Format(
            "Топик, в котором бот будет реагировать на команды и удалять сообщения, "
            "не соответствующие его командам:\n\n{moderated_tread}\n\n"
            "*Сообщения администраторов в этом чате удаляться не будут. "
            "Введите tread_id чтобы изменить топик бота. "
            "Узнать его можно при помощи команды /chatinfo в топике вашего чата."),
        Button(Const("Сбросить"), id="reset_moderated_tread", on_click=on_reset_button),
        SwitchTo(Const("Назад"), id="back_to_choice_settings", state=states.Settings.CHOICE_SETTING),
        MessageInput(content_types=[ContentType.TEXT], func=on_input_text),
        state=states.Settings.SET_BOT_TOPIC,
        getter=getter_tread_id
    ),
    Window(
        Format(
            "В качестве модераторов сейчас выступают пользователи с этими id:\n\n{moderators}\n\n"
            "Отправьте сообщение с id пользователя, чтобы добавить его в модераторы бота.\n"
            "Чтобы удалить - отправьте id модератора со знаком '-' перед его id.\n"
            "Для отмены настройки нажмите кнопку Назад."),
        SwitchTo(Const("Назад"), id="back_to_choice_settings", state=states.Settings.CHOICE_SETTING),
        MessageInput(content_types=[ContentType.TEXT], func=on_input_text),
        state=states.Settings.SET_MODERATORS,
        getter=getter_moderators,
        parse_mode='HTML'
    ),
)
