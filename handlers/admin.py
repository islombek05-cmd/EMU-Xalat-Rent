from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery

import database as db
from config import ADMIN_USERNAMES
from keyboards import (
    asosiy_menu,
    admin_panel_klaviatura,
    admin_tasdiqlash_klaviatura,
    qaytarish_klaviatura,
)

router = Router()


def is_admin_user(user) -> bool:
    username = (user.username or "").lower()
    return username in [x.lower() for x in ADMIN_USERNAMES]


@router.message(F.text == "👨‍💼 Admin panel")
async def admin_panel(message: Message):
    if not is_admin_user(message.from_user):
        await message.answer("❌ Sizda admin huquqi yo‘q.")
        return

    await message.answer(
        "👨‍💼 <b>Admin panel</b>\n\n"
        "Kerakli bo‘limni tanlang:",
        reply_markup=admin_panel_klaviatura(),
    )


@router.callback_query(F.data == "admin_hisobot")
async def admin_hisobot(callback: CallbackQuery):
    if not is_admin_user(callback.from_user):
        await callback.answer("❌ Ruxsat yo‘q.", show_alert=True)
        return

    hisobot = await db.get_income_report()

    matn = (
        "📊 <b>Daromad hisoboti</b>\n\n"
        f"💰 Jami daromad: {hisobot['jami']:,} so‘m\n"
        f"📅 Bugungi daromad: {hisobot['bugungi']:,} so‘m\n"
        f"🗓 Oylik daromad: {hisobot['oylik']:,} so‘m\n\n"
        f"🥼 Band xalatlar: {hisobot['band_soni']} ta\n"
        f"✅ Mavjud xalatlar: {hisobot['mavjud_soni']} ta"
    )

    await callback.message.edit_text(matn)
    await callback.answer()


@router.callback_query(F.data == "admin_xalatlar")
async def admin_xalatlar(callback: CallbackQuery):
    if not is_admin_user(callback.from_user):
        await callback.answer("❌ Ruxsat yo‘q.", show_alert=True)
        return

    xalatlar = await db.get_all_xalatlar()

    erkaklar_mavjud = []
    erkaklar_band = []
    ayollar_mavjud = []
    ayollar_band = []

    for x in xalatlar:
        if x["jins"] == "erkak":
            if x["holat"] == "mavjud":
                erkaklar_mavjud.append(x["raqam"])
            else:
                erkaklar_band.append(x["raqam"])
        else:
            if x["holat"] == "mavjud":
                ayollar_mavjud.append(x["raqam"])
            else:
                ayollar_band.append(x["raqam"])

    matn = (
        "🥼 <b>Xalatlar holati</b>\n\n"
        f"👨 <b>Erkaklar:</b>\n"
        f"✅ Mavjud: {', '.join(erkaklar_mavjud) or 'yo‘q'}\n"
        f"🔴 Band: {', '.join(erkaklar_band) or 'yo‘q'}\n\n"
        f"👩 <b>Ayollar:</b>\n"
        f"✅ Mavjud: {', '.join(ayollar_mavjud) or 'yo‘q'}\n"
        f"🔴 Band: {', '.join(ayollar_band) or 'yo‘q'}"
    )

    await callback.message.edit_text(matn)
    await callback.answer()


@router.callback_query(F.data == "admin_bandlar")
async def admin_bandlar(callback: CallbackQuery):
    if not is_admin_user(callback.from_user):
        await callback.answer("❌ Ruxsat yo‘q.", show_alert=True)
        return

    bandlar = await db.get_all_active_bookings()

    if not bandlar:
        await callback.message.edit_text(
            "📦 Hozircha faol bandlar yo‘q."
        )
        await callback.answer()
        return

    matn = "📦 <b>Barcha faol bandlar:</b>\n\n"

    for b in bandlar:
        matn += (
            f"🥼 Xalat №{b['raqam']}\n"
            f"👤 Telegram ID: <code>{b['telegram_id']}</code>\n"
            f"📅 {b['boshlanish_sana']} → {b['tugash_sana']}\n"
            f"💰 {b['narx']:,} so‘m\n"
            f"💳 To‘lov: {b['tolov_holati']}\n"
            f"📝 Band №{b['id']}\n\n"
        )

    await callback.message.edit_text(matn)

    await callback.message.answer(
        "↩️ Qaytarilgan xalatni tanlang:",
        reply_markup=qaytarish_klaviatura(bandlar),
    )

    await callback.answer()


@router.callback_query(F.data == "admin_kutilmoqda")
async def admin_kutilmoqda(callback: CallbackQuery):
    if not is_admin_user(callback.from_user):
        await callback.answer("❌ Ruxsat yo‘q.", show_alert=True)
        return

    bandlar = await db.get_pending_payments()

    if not bandlar:
        await callback.message.edit_text(
            "⏳ Hozircha tasdiq kutayotgan to‘lovlar yo‘q."
        )
        await callback.answer()
        return

    await callback.message.edit_text(
        f"⏳ <b>Tasdiq kutayotgan to‘lovlar: {len(bandlar)} ta</b>"
    )

    for b in bandlar:
        matn = (
            f"💳 <b>To‘lovni tekshirish</b>\n\n"
            f"🥼 Xalat: №{b['raqam']}\n"
            f"👤 Telegram ID: <code>{b['telegram_id']}</code>\n"
            f"📅 Muddat: {b['kunlar_soni']} kun\n"
            f"💰 Summa: {b['narx']:,} so‘m\n"
            f"📝 Band №{b['id']}"
        )

        if b["chek_file_id"]:
            await callback.message.answer_photo(
                photo=b["chek_file_id"],
                caption=matn,
                reply_markup=admin_tasdiqlash_klaviatura(b["id"]),
            )
        else:
            await callback.message.answer(
                matn,
                reply_markup=admin_tasdiqlash_klaviatura(b["id"]),
            )

    await callback.answer()


@router.callback_query(F.data.startswith("admin_tasdiq_"))
async def admin_tasdiqlash(callback: CallbackQuery):
    if not is_admin_user(callback.from_user):
        await callback.answer("❌ Ruxsat yo‘q.", show_alert=True)
        return

    band_id = int(callback.data.replace("admin_tasdiq_", ""))

    band = await db.get_booking(band_id)

    if not band:
        await callback.answer("❌ Band topilmadi.", show_alert=True)
        return

    await db.confirm_payment(band_id)

    try:
        await callback.bot.send_message(
            band["telegram_id"],
            f"✅ <b>To‘lovingiz tasdiqlandi!</b>\n\n"
            f"🥼 Xalat: №{band['raqam']}\n"
            f"💰 Summa: {band['narx']:,} so‘m\n"
            f"📝 Band №{band_id}\n\n"
            "Xalatingiz siz uchun band qilindi."
        )
    except Exception:
        pass

    await callback.message.edit_caption(
        caption=f"✅ To‘lov tasdiqlandi.\n\nBand №{band_id}",
        reply_markup=None,
    ) if callback.message.photo else await callback.message.edit_text(
        f"✅ To‘lov tasdiqlandi.\n\nBand №{band_id}"
    )

    await callback.answer("✅ To‘lov tasdiqlandi.")


@router.callback_query(F.data.startswith("admin_rad_"))
async def admin_rad_etish(callback: CallbackQuery):
    if not is_admin_user(callback.from_user):
        await callback.answer("❌ Ruxsat yo‘q.", show_alert=True)
        return

    band_id = int(callback.data.replace("admin_rad_", ""))

    band = await db.get_booking(band_id)

    if not band:
        await callback.answer("❌ Band topilmadi.", show_alert=True)
        return

    await db.reject_payment(band_id)

    try:
        await callback.bot.send_message(
            band["telegram_id"],
            f"❌ <b>To‘lovingiz rad etildi.</b>\n\n"
            f"🥼 Xalat: №{band['raqam']}\n"
            f"📝 Band №{band_id}\n\n"
            "Iltimos, to‘lov chekini qayta tekshiring yoki administratorga murojaat qiling."
        )
    except Exception:
        pass

    if callback.message.photo:
        await callback.message.edit_caption(
            caption=f"❌ To‘lov rad etildi.\n\nBand №{band_id}",
            reply_markup=None,
        )
    else:
        await callback.message.edit_text(
            f"❌ To‘lov rad etildi.\n\nBand №{band_id}"
        )

    await callback.answer("❌ To‘lov rad etildi.")


@router.callback_query(F.data.startswith("qaytar_"))
async def xalatni_qaytarish(callback: CallbackQuery):
    if not is_admin_user(callback.from_user):
        await callback.answer("❌ Ruxsat yo‘q.", show_alert=True)
        return

    band_id = int(callback.data.replace("qaytar_", ""))

    band = await db.get_booking(band_id)

    if not band:
        await callback.answer("❌ Band topilmadi.", show_alert=True)
        return

    await db.return_xalat(band_id)

    try:
        await callback.bot.send_message(
            band["telegram_id"],
            f"↩️ <b>Xalat qaytarildi.</b>\n\n"
            f"🥼 Xalat: №{band['raqam']}\n"
            f"📝 Band №{band_id}\n\n"
            "Rahmat!"
        )
    except Exception:
        pass

    await callback.message.edit_text(
        f"✅ №{band['raqam']} xalat qaytarildi va yana mavjud holatga o'tkazildi."
    )

    await callback.answer("✅ Xalat qaytarildi.")
