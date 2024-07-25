from aiogram import F, Router
from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.widgets.text import Format, Const
from aiogram_dialog.widgets.kbd import Start, Back, SwitchTo

from TGBot.private_chat.menu import states
from aiogram.filters import CommandStart
from aiogram.filters.command import Command
from aiogram.types import Message
from TGBot.private_chat.menu.whatcanbot import opportunities_menu
from TGBot.private_chat.menu.admins_panel import admin_panel
from TGBot.filters.is_admin import IsAbsoluteAdmin


main_menu = Dialog(  # Главное меню бота
    Window(
        Format(
            "{event.from_user.full_name}, Добро пожаловать в меню Бота Кай!\n"
            "В этом меню ты сможешь зарегистрировать Кая для работы в своём чате😱, "
            "а также настроить любые параметры работы уже зарегистрированного чата в Панели управления😎"
        ),
        Start(Const("Возможности бота"), id="opportunities", state=states.Opportunities.START),
        SwitchTo(Const("Подключить бота"), id="chat_connect", state=states.MainMenu.CONNECTION),
        Start(Const("Панель управления"), id="admin_panel", state=states.Settings.START),
        state=states.MainMenu.START
    ),
    Window(
        Format(
            "Для регистрации работы Кая в вашем чате вам необходимо приобрести подписку.\n"
            "Минимальная подписка действует месяц. За покупкой - https://t.me/xrnze"
        ),
        Back(Const("Назад")),
        state=states.MainMenu.CONNECTION
    ),
)


main_menu_router = Router()
main_menu_router.message.filter(F.chat.type == "private")


main_menu_router.include_router(main_menu)
main_menu_router.include_router(opportunities_menu)
main_menu_router.include_router(admin_panel)


@main_menu_router.message(CommandStart())
async def start(message: Message, dialog_manager: DialogManager):
    await dialog_manager.start(states.MainMenu.START)
