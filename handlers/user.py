from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
import database as db
from config import ADMIN_USERNAMES, CARD_NUMBER, CARD_OWNER, PRICE_PER_DAY
from keyboards import (
    asosiy_menu,
    jins_tanlash_klaviatura,
    xalatlar_klaviatura,
    tolov_turi_klaviatura,
    bekor_qilish_klaviatura,
)
from states import BandQilish
router = Router()
def is_admin(message: Message) -> bool:
    username = (message.from_user.username or "").lower()
    return username in [x.lower() for x in ADMIN_USERNAMES]
@router.message(CommandStart())
async def start_handler(message: Message, state: FSMContext):
    await state.clear()
    await db.upsert_foydalanuvchi(
        message.from_user.id,
        message.from_user.full_name,
        message.from_user.username or "",
    )
    await message.answer(
        "👋 Assalomu alaykum!\n\n"
        "🥼 Xalat ijarasi botiga xush kelibsiz.",
        reply_markup=asosiy_menu(is_admin(message)),
    )
@router.message(F.text == "🥼 Xalat band qilish")
async def band_boshlash(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(BandQilish.jins_tanlash)
    await message.answer(
        "🥼 Qaysi turdagi xalat kerak?",
        reply_markup=jins_tanlash_klaviatura(),
    )
@router.callback_query(BandQilish.jins_tanlash, F.data.startswith("jins_"))
async def jins_tanlash(callback: CallbackQuery, state: FSMContext):
    jins = callback.data.replace("jins_", "")
    await state.update_data(jins=jins)
    xalatlar = await db.get_available_xalatlar(jins)
    if not xalatlar:
        await callback.message.edit_text(
            "😔 Hozircha bu turdagi xalatlarning barchasi band."
        )
        await callback.answer()
        return
    await state.set_state(BandQilish.xalat_tanlash)
    nomi = "erkaklar" if jins == "erkak" else "ayollar"
    await callback.message.edit_text(
        f"🥼 {nomi.title()} uchun mavjud xalatni tanlang:",
        reply_markup=xalatlar_klaviatura(xalatlar),
    )
    await callback.answer()
@router.callback_query(BandQilish.xalat_tanlash, F.data == "orqaga_jins")
async def jinsga_qaytish(callback: CallbackQuery, state: FSMContext):
    await state.set_state(BandQilish.jins_tanlash)
    await callback.message.edit_text(
        "🥼 Qaysi turdagi xalat kerak?",
        reply_markup=jins_tanlash_klaviatura(),
    )
    await callback.answer()
@router.callback_query(BandQilish.xalat_tanlash, F.data.startswith("xalat_"))
async def xalat_tanlash(callback: CallbackQuery, state: FSMContext):
    xalat_id = int(callback.data.replace("xalat_", ""))
    xalat = await db.get_xalat_by_id(xalat_id)
    if not xalat or xalat["holat"] != "mavjud":
        await callback.answer(
            "Bu xalat hozir band bo‘lib qolgan.",
            show_alert=True,
        )
        return
    await state.update_data(xalat_id=xalat_id)
    await state.set_state(BandQilish.kun_kiritish)
    await callback.message.edit_text(
        f"🥼 №{xalat['raqam']} tanlandi.\n\n"
        f"💰 1 kunlik ijara: {PRICE_PER_DAY:,} so‘m\n\n"
        "📅 Necha kunga ijaraga olmoqchisiz?\n"
        "Masalan: 3"
    )
    await callback.answer()
@router.message(BandQilish.kun_kiritish)
async def kun_kiritish(message: Message, state: FSMContext):
    try:
        kunlar = int(message.text.strip())
    except (ValueError, AttributeError):
        await message.answer("❗ Faqat son kiriting. Masalan: 3")
        return
    if kunlar < 1 or kunlar > 365:
        await message.answer("❗ Ijara muddati 1 dan 365 kungacha bo‘lishi kerak.")
        return
    await state.update_data(kunlar_soni=kunlar)
    await state.set_state(BandQilish.tolov_tanlash)
    summa = kunlar * PRICE_PER_DAY
    await message.answer(
        f"📅 Muddat: {kunlar} kun\n"
        f"💰 Jami summa: {summa:,} so‘m\n\n"
        "💳 To‘lov turini tanlang:",
        reply_markup=tolov_turi_klaviatura(),
    )
@router.callback_query(BandQilish.tolov_tanlash, F.data == "tolov_naqd")
async def naqd_tolov(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    band_id = await db.create_booking(
        xalat_id=data["xalat_id"],
        telegram_id=callback.from_user.id,
        kunlar_soni=data["kunlar_soni"],
        tolov_turi="naqd",
    )
    await state.clear()
    await callback.message.edit_text(
        f"✅ Band qilish muvaffaqiyatli!\n\n"
        f"🥼 Xalat: №{(await db.get_xalat_by_id(data['xalat_id']))['raqam']}\n"
        f"📅 Muddat: {data['kunlar_soni']} kun\n"
        f"💰 Summa: {data['kunlar_soni'] * PRICE_PER_DAY:,} so‘m\n"
        f"💵 To‘lov: naqd\n\n"
        f"📝 Band raqami: #{band_id}"
    )
    await callback.message.answer(
        "Asosiy menyu:",
        reply_markup=asosiy_menu(is_admin(callback.message)),
    )
    await callback.answer()
@router.callback_query(BandQilish.tolov_tanlash, F.data == "tolov_karta")
async def karta_tolov(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    summa = data["kunlar_soni"] * PRICE_PER_DAY
    await state.set_state(BandQilish.chek_kutish)
    await callback.message.edit_text(
        "💳 Elektron to‘lov\n\n"
        f"💰 To‘lov summasi: {summa:,} so‘m\n\n"
        f"💳 Karta: <code>{CARD_NUMBER}</code>\n"
        f"👤 Karta egasi: {CARD_OWNER}\n\n"
        "To‘lovni amalga oshirgach, chek rasmini shu yerga yuboring."
    )
    await callback.answer()
@router.message(BandQilish.chek_kutish, F.photo)
async def chek_qabul_qilish(message: Message, state: FSMContext):
    data = await state.get_data()
    photo = message.photo[-1]
    band_id = await db.create_booking(
        xalat_id=data["xalat_id"],
        telegram_id=message.from_user.id,
        kunlar_soni=data["kunlar_soni"],
        tolov_turi="karta",
        chek_file_id=photo.file_id,
    )
    await state.clear()
    await message.answer(
        f"✅ Buyurtmangiz qabul qilindi!\n\n"
        f"💰 Summa: {data['kunlar_soni'] * PRICE_PER_DAY:,} so‘m\n"
        f"📝 Band raqami: #{band_id}\n\n"
        "⏳ To‘lovingiz admin tomonidan tekshiriladi.",
        reply_markup=asosiy_menu(is_admin(message)),
    )
@router.message(BandQilish.chek_kutish)
async def chek_kutilmoqda(message: Message):
    await message.answer(
        "📸 Iltimos, to‘lov chekini rasm ko‘rinishida yuboring."
    )
@router.message(F.text == "📦 Mening bandlarim")
async def mening_bandlarim(message: Message):
    bandlar = await db.get_user_active_bookings(message.from_user.id)
    if not bandlar:
        await message.answer("📦 Sizda hozircha faol bandlar yo‘q.")
        return
    matn = "📦 <b>Sizning faol bandlaringiz:</b>\n\n"
    for b in bandlar:
        matn += (
            f"🥼 Xalat: №{b['raqam']}\n"
            f"📅 {b['boshlanish_sana']} → {b['tugash_sana']}\n"
            f"💰 {b['narx']:,} so‘m\n"
            f"💳 To‘lov: {b['tolov_holati']}\n"
            f"📝 Band №{b['id']}\n\n"
        )
    await message.answer(matn)
@router.message(F.text == "ℹ️ Yordam")
async def yordam(message: Message):
    await message.answer(
        "ℹ️ <b>Yordam</b>\n\n"
        "🥼 Xalat band qilish — mavjud xalatlardan tanlab, ijara rasmiylashtirasiz.\n\n"
        "📦 Mening bandlarim — faol bandlaringizni ko‘rasiz.\n\n"
        "💳 Elektron to‘lovda to‘lov chekini rasm sifatida yuboring.\n\n"
        "Savollar bo‘lsa, administratorga murojaat qiling."
    )
@router.callback_query(F.data == "bekor_qilish")
async def bekor_qilish(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.answer(
        "❌ Band qilish bekor qilindi.",
        reply_markup=asosiy_menu(is_admin(callback.message)),
    )
    await callback.answer()
