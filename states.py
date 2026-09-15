# states.py
# Foydalanuvchi bilan bosqichma-bosqich suhbat holatlari (FSM)

from aiogram.fsm.state import State, StatesGroup


class BandQilish(StatesGroup):
    jins_tanlash = State()
    xalat_tanlash = State()
    kun_kiritish = State()
    tolov_tanlash = State()
    chek_kutish = State()
