# 🤖 Telegram AI Assistant Userbot

Ushbu loyiha sizning shaxsiy Telegram akkauntingizni sun'iy intellekt (Google Gemini 1.5) bilan qurollangan aqlli yordamchiga aylantiradi. Matnli xabarlar, ovozli xabarlar (Voice), dumaloq videolar (Video note) va suratlarni to'g'ridan-to'g'ri tahlil qilib, chat tarixini xotirada saqlagan holda ravon javob qaytaradi.

---

## 🏛 Loyiha Arxitekturasi

```text
[ Telegram Akkaunt (Userbot) ]
              │
              ▼ (Kiruvchi xabarlar: Matn / Ovoz / Video)
  [ Message Handler (Telethon) ]
              │
      ┌───────┴────────────────────────┐
      ▼                                ▼
[ Text Handler ]               [ Media Handler ]
      │                                │
      │                      (Audio/Video yuklash)
      │                                │
      │                        [ FFmpeg / STT ]
      │                                │
      └───────────────┬────────────────┘
                      ▼
            [ Context Manager ] (SQLite - chat tarixi)
                      │
                      ▼
             [ AI Core Engine ] (Google Gemini 1.5 Flash / Pro)
                      │
                      ▼ (Generatsiyalangan javob)
          [ Output Handler (Typing...) ]
                      │
                      ▼
[ Userbot orqali chatga javob yuborish ]
```

---

## 🚀 Imkoniyatlari

- ⚡ **Google Gemini 1.5 Integratsiyasi**: Matn, audio va videolarni to'g'ridan-to'g'ri multimodal tushunish.
- 🎙 **Ovoz va Video tahlili (FFmpeg & STT)**: Ovozli xabarlar va dumaloq videolardagi nutqni tushunish va xohishga ko'ra matnga aylantirish (`.stt`).
- 🧠 **Context Manager (SQLite)**: Har bir chat uchun alohida suhbat tarixini xotirada saqlash va kontekst asosida mantiqiy javob berish.
- 🛡 **Xavfsiz Whitelist tizimi**: Faqat siz ruxsat bergan chatlarda ishlaydi (notanishlar yoki barcha guruhlarda o'z-o'zidan yozib yubormaydi).
- ✍️ **Output Handler**: Javob yozilayotganda Telegramda haqiqiy `typing...` yoki `yozmoqda...` holatini ko'rsatish va uzun xabarlarni avtomatik bo'lib yuborish.

---

## 📋 O'rnatish va Sozlash

### 1. Telegram API Ma'lumotlarini olish:
1. [my.telegram.org](https://my.telegram.org) saytiga kiring va telefon raqamingiz orqali tasdiqlang.
2. **API development tools** bo'limiga kiring.
3. Yangi ilova yarating va `API_ID` hamda `API_HASH` qiymatlarini nusxalab oling.

### 2. Google Gemini API kalitini olish:
1. [Google AI Studio](https://aistudio.google.com/) saytiga kiring.
2. **Get API key** tugmasini bosing va bepul API kalit yarating.

### 3. `.env` faylini to'ldirish:
Loyihadagi `.env` faylini oching va qiymatlarni kiriting:

```env
API_ID=12345678
API_HASH=your_telegram_api_hash_here
GEMINI_API_KEY=AIzaSy...your_gemini_api_key_here
GEMINI_MODEL=gemini-1.5-flash
WHITELIST_CHATS=me
```

> **Eslatma:** `WHITELIST_CHATS=me` bo'lsa, bot faqat sizning "Saqlangan xabarlar" (Saved Messages) chatingizda ishlaydi. Qo'shimcha do'stlaringiz yoki guruhlaringiz ID sini vergul bilan ajratib yozishingiz mumkin (masalan: `me, 123456789, -1001987654321`).

---

## ▶️ Ishga Tushirish

Terminalda loyiha papkasiga kiring va quyidagi buyruqni bering:

```bash
python main.py
```

*Birinchi marta ishga tushirganda, Telegram sizdan telefon raqamingizni va Telegramga kelgan tasdiqlash kodini kiritishingizni so'raydi. Muvaffaqiyatli kirgach, `ai_userbot.session` fayli yaratiladi va keyingi safar kod so'ralmaydi.*

---

## 🛠 Userbot Buyruqlari

Siz yoki ruxsat berilgan chatdagi foydalanuvchilar quyidagi buyruqlardan foydalanishi mumkin:

| Buyruq | Tavsifi |
|---|---|
| `.help` | Barcha mavjud buyruqlarni ko'rsatish |
| `.clear` yoki `.reset` | Ushbu chatdagi AI xotirasini tozalash (yangi mavzu boshlash) |
| `.ping` | Botning faolligini tekshirish |
| `.whitelist list` | Ruxsat etilgan chatlar ro'yxatini ko'rish |
| `.whitelist add [chat_id]` | Joriy yoki ko'rsatilgan chatni ruxsatnomaga qo'shish |
| `.whitelist remove [chat_id]` | Chatni ruxsatnomadan o'chirish |
| `.stt` | Ovozli xabarga javoban (reply) yozilsa, uning matnini chiqarib beradi |

---

## 📁 Loyiha Strukturasi

```
AI_Asistent/
├── core/
│   ├── ai_engine.py         # Google Gemini 1.5 modeli bilan ishlash
│   └── ffmpeg_utils.py      # Audio va videoni konvertatsiya qilish
├── database/
│   └── context_manager.py   # SQLite chat tarixi va whitelist boshqaruvi
├── handlers/
│   ├── message_handler.py   # Kiruvchi xabarlar filtri va marshrutizator
│   ├── text_handler.py      # Matnli xabarlar va buyruqlar
│   ├── media_handler.py     # Ovozli va video fayllar tahlili
│   └── output_handler.py    # Typing animatsiyasi va javob yuborish
├── utils/
│   └── helpers.py           # Yordamchi vositalar
├── config.py                # Konfiguratsiya va sozlamalar
├── main.py                  # Asosiy ishga tushirish fayli
├── requirements.txt         # Kutubxonalar ro'yxati
└── .env                     # Shaxsiy maxfiy kalitlar
```
