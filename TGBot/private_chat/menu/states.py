from aiogram.fsm.state import State, StatesGroup


class MainMenu(StatesGroup):
    START = State()
    OPPORTUNITIES = State()
    CONNECTION = State()


class Opportunities(StatesGroup):
    START = State()
    PANEL_COMMANDS = State()
    BOT_COMMANDS = State()


class Settings(StatesGroup):
    START = State()
    CHOICE_SETTING = State()
    SET_MODERATORS = State()
    SET_BOT_TOPIC = State()
    SET_HELLO_MESSAGE = State()
    