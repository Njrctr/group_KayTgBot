from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.text import Const
from aiogram_dialog.widgets.kbd import Row, Cancel, SwitchTo
from TGBot.private_chat.menu import states
from TGBot.private_chat.menu.command_list import panel_commands_TEXT
from TGBot.group_chat.group_commands import all_commands


opportunities_menu = Dialog(
    Window(
        Const("Выберите пункт информации:"),
        Row(
            SwitchTo(
                Const("Панель управления"),
                id="panel_commands_list",
                state=states.Opportunities.PANEL_COMMANDS),
            SwitchTo(
                Const("Команды бота"),
                id="bot_commands_list",
                state=states.Opportunities.BOT_COMMANDS),
        ),
        Cancel(Const("Назад")),
        state=states.Opportunities.START,
    ),

    Window(
        Const(text=panel_commands_TEXT),
        SwitchTo(
            Const("Назад"),
            id='main1',
            state=states.Opportunities.START),
        state=states.Opportunities.PANEL_COMMANDS,
        parse_mode="MarkdownV2",
    ),

    Window(
        Const(text=all_commands),
        SwitchTo(
            Const("Назад"),
            id='main2',
            state=states.Opportunities.START),
        state=states.Opportunities.BOT_COMMANDS,
        parse_mode="MarkdownV2",
    ),
)
