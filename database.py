# database.py
# SQLite bilan ishlash uchun barcha funksiyalar shu yerda

import aiosqlite
from datetime import datetime, date, timedelta
from config import DB_PATH, PRICE_PER_DAY


async def init_db():
    """Bazani va jadvallarni yaratish, xalatlarni to'ldirish"""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS xalatlar (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                raqam TEXT UNIQUE NOT NULL,
                jins TEXT NOT NULL,
                holat TEXT NOT NULL DEFAULT 'mavjud'
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS foydalanuvchilar (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER UNIQUE NOT NULL,
                ism TEXT,
                username TEXT,
                telefon TEXT
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS bandlar (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                xalat_id INTEGER NOT NULL,
                telegram_id INTEGER NOT NULL,
                boshlanish_sana TEXT NOT NULL,
                tugash_sana TEXT NOT NULL,
                kunlar_soni INTEGER NOT NULL,
                narx INTEGER NOT NULL,
                tolov_turi TEXT NOT NULL,
                tolov_holati TEXT NOT NULL DEFAULT 'kutilmoqda',
                chek_file_id TEXT,
                holat TEXT NOT NULL DEFAULT 'faol',
                yaratilgan_vaqt TEXT NOT NULL,
                eslatma_yuborildi INTEGER NOT NULL DEFAULT 0,
                FOREIGN KEY (xalat_id) REFERENCES xalatlar (id)
            )
        """)
        await db.commit()

        cursor = await db.execute("SELECT COUNT(*) FROM xalatlar")
        (count,) = await cursor.fetchone()
        if count == 0:
            rows = []
            for i in range(1, 41):
                raqam = f"{i:02d}"
                jins = "erkak" if i <= 20 else "ayol"
                rows.append((raqam, jins))
            await db.executemany(
                "INSERT INTO xalatlar (raqam, jins, holat) VALUES (?, ?, 'mavjud')",
                rows,
            )
            await db.commit()


async def upsert_foydalanuvchi(telegram_id: int, ism: str, username: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """
            INSERT INTO foydalanuvchilar (telegram_id, ism, username)
            VALUES (?, ?, ?)
            ON CONFLICT(telegram_id) DO UPDATE SET ism=excluded.ism, username=excluded.username
            """,
            (telegram_id, ism, username),
        )
        await db.commit()


async def set_telefon(telegram_id: int, telefon: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE foydalanuvchilar SET telefon = ? WHERE telegram_id = ?",
            (telefon, telegram_id),
        )
        await db.commit()


async def get_available_xalatlar(jins: str):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM xalatlar WHERE jins = ? AND holat = 'mavjud' ORDER BY raqam",
            (jins,),
        )
        return await cursor.fetchall()


async def get_xalat_by_id(xalat_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM xalatlar WHERE id = ?", (xalat_id,))
        return await cursor.fetchone()


async def get_all_xalatlar():
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM xalatlar ORDER BY raqam")
        return await cursor.fetchall()


async def create_booking(
    xalat_id: int,
    telegram_id: int,
    kunlar_soni: int,
    tolov_turi: str,
    chek_file_id: str = None,
) -> int:
    boshlanish = date.today()
    tugash = boshlanish + timedelta(days=kunlar_soni)
    narx = kunlar_soni * PRICE_PER_DAY
    tolov_holati = "tasdiqlangan" if tolov_turi == "naqd" else "kutilmoqda"

    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            """
            INSERT INTO bandlar
            (xalat_id, telegram_id, boshlanish_sana, tugash_sana, kunlar_soni,
             narx, tolov_turi, tolov_holati, chek_file_id, holat, yaratilgan_vaqt)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'faol', ?)
            """,
            (
                xalat_id,
                telegram_id,
                boshlanish.isoformat(),
                tugash.isoformat(),
                kunlar_soni,
                narx,
                tolov_turi,
                tolov_holati,
                chek_file_id,
                datetime.now().isoformat(),
            ),
        )
        band_id = cursor.lastrowid
        await db.execute("UPDATE xalatlar SET holat = 'band' WHERE id = ?", (xalat_id,))
        await db.commit()
        return band_id


async def get_booking(band_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            """
            SELECT b.*, x.raqam, x.jins FROM bandlar b
            JOIN xalatlar x ON x.id = b.xalat_id
            WHERE b.id = ?
            """,
            (band_id,),
        )
        return await cursor.fetchone()


async def get_user_active_bookings(telegram_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            """
            SELECT b.*, x.raqam, x.jins FROM bandlar b
            JOIN xalatlar x ON x.id = b.xalat_id
            WHERE b.telegram_id = ? AND b.holat = 'faol'
            ORDER BY b.yaratilgan_vaqt DESC
            """,
            (telegram_id,),
        )
        return await cursor.fetchall()


async def confirm_payment(band_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE bandlar SET tolov_holati = 
