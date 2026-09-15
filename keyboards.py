# keyboards.py
# Barcha inline va oddiy klaviaturalar shu yerda

from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    KeyboardButton,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder


def asosiy_menu(is_admin: bool = False) -> ReplyKeyboardMarkup:
    tugmalar = [
        [KeyboardButton(text="🥼 Xalat band qilish")],
        [KeyboardButton(text="📦 Mening bandlarim")],
        [KeyboardButton(text="ℹ️ Yordam")],
    ]
    if is_admin:
        tugmalar.append([KeyboardButton(text="👨‍💼 Admin panel")])
    return ReplyKeyboardMarkup(keyboard=tugmalar, resize_keyboard=True)


def jins_tanlash_klaviatura() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="👨 Erkaklar uchun", callback_data="jins_erkak")
    builder.button(text="👩 Ayollar uchun", callback_data="jins_ayol")
    builder.adjust(1)
    return builder.as_markup()


def xalatlar_klaviatura(xalatlar) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for x in xalatlar:
        builder.button(text=f"№{x['raqam']}", callback_data=f"xalat_{x['id']}")
    builder.button(text="⬅️ Orqaga", callback_data="orqaga_jins")
    builder.adjust(4)
    return builder.as_markup()


def tolov_turi_klaviatura() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="💵 Naqd pul", callback_data="tolov_naqd")
    builder.button(text="💳 Elektron to'lov", callback_data="tolov_karta")
    builder.adjust(1)
    return builder.as_markup()


def bekor_qilish_klaviatura() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="❌ Bekor qilish", callback_data="bekor_qilish")
    return builder.as_markup()


def admin_tasdiqlash_klaviatura(band_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Tasdiqlash", callback_data=f"admin_tasdiq_{band_id}")
    builder.button(text="❌ Rad etish", callback_data=f"admin_rad_{band_id}")
    builder.adjust(2)
    return builder.as_markup()


def qaytarish_klaviatura(bandlar) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for b in bandlar:
        builder.button(
            text=f"↩️ №{b['raqam']} qaytarish", callback_data=f"qaytar_{b['id']}"
        )
    builder.adjust(1)
    return builder.as_markup()


def admin_panel_klaviatura() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="📊 Daromad hisoboti", callback_data="admin_hisobot")
    builder.button(text="🥼 Xalatlar holati", callback_data="admin_xalatlar")
    builder.button(text="📦 Barcha bandlar", callback_data="admin_bandlar")
    builder.button(text="⏳ Tasdiq kutayotganlar", callback_data="admin_kutilmoqda")
    builder.adjust(1)
    return builder.as_markup()
