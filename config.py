# config.py
# Bot sozlamalari shu yerda saqlanadi

import os

# Avval environment variable'dan o'qishga harakat qiladi (Render/serverlar uchun xavfsizroq),
# topa olmasa shu yerdagi standart tokenni ishlatadi (mahalliy sinov uchun)
BOT_TOKEN = os.environ.get(
    "BOT_TOKEN", "8936899117:AAE8Jtrbad8mccmWSo3Mz0uxLpfD2hEVBXM"
)

# Admin username (@ belgisisiz, kichik harflarda solishtiriladi)
ADMIN_USERNAME = "ilhomvich07"

# Agar bir nechta admin bo'lsa, shu ro'yxatga qo'shing (username, @ siz)
ADMIN_USERNAMES = ["ilhomvich07"]

# To'lov uchun karta raqami (o'zingiznikiga almashtiring)
CARD_NUMBER = "8600 0000 0000 0000"
CARD_OWNER = "F.I.Sh."

# Kunlik ijara narxi (so'm)
PRICE_PER_DAY = 20000

# Ma'lumotlar bazasi fayli
DB_PATH = "xalat_bot.db"

# Nechchi soat/kun oldin eslatma yuborilsin (kunlarda)
REMINDER_DAYS_BEFORE = 1
