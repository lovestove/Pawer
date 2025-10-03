from aiogram.fsm.state import State, StatesGroup


class PetCreation(StatesGroup):
    choosing_name = State()
    choosing_type = State()
