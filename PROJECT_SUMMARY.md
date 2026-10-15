# 🤖 Telegram AI Asistent Userbot — Toʻliq Loyiha Hujjati

Ushbu hujjat loyihaning arxitekturasi, oʻrnatilgan modullar, sozlamalar va bartaraf etilgan barcha texnik masalalarni oʻz ichiga oladi. Kelgusida loyiha bilan ishlovchi dasturchi yoki AI agent ushbu fayl orqali tizimni bir zumda tushunishi mumkin.

---

## 📌 1. Loyiha Haqida

- **Loyiha nomi:** Telegram AI Assistant Userbot
- **Joylashuvi:** `C:\Users\user\Desktop\AI_Asistent`
- **Asosiy maqsad:** Telegram shaxsiy akkauntini sun'iy intellekt (Google Gemini) bilan integratsiya qilib, matn, audio (ovozli xabar), video (dumaloq video) va suratlarni qabul qilib, kontekstni eslagan holda javob qaytaruvchi avtomatlashtirilgan userbot yaratish.

---

## 🏛 2. Tizim Arxitekturasi

Loyiha quyidagi tasdiqlangan oqim asosida qurilgan:

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
             [ AI Core Engine ] (Google Gemini 3.5 Flash Lite)
                      │
                      ▼ (Generatsiyalangan javob)
          [ Output Handler (Typing...) ]
                      │
                      ▼
[ Userbot orqali chatga javob yuborish ]
```

---

## 📂 3. Fayllar Tuzilishi va Modullar

```
AI_Asistent/
├── 📄 .env                    # Maxfiy kalitlar va konfiguratsiya (API_ID, API_HASH, GEMINI_API_KEY)
├── 📄 .env.example            # Sozlamalar namunasi
├── 📄 .gitignore              # Xavfsizlik uchun (.session, .env, .db fayllarini gitga chiqarmaslik)
├── 📄 Dockerfile                # Render bulutli serveri uchun Docker muhiti (Python 3.12 + FFmpeg)
├── 📄 .dockerignore            # Docker image ga ortiqcha fayllar tushmasligini ta'minlash
├── 📄 config.py               # Loyiha konfiguratsiyasi va whitelist tekshiruvi
├── 📄 main.py                 # Asosiy ishga tushirish fayli (TelegramClient, UTF-8 konsol, Health check)
├── 📄 requirements.txt        # Kerakli Python kutubxonalari
├── 📄 README.md               # Foydalanuvchi uchun tezkor qo'llanma
├── 📄 PROJECT_SUMMARY.md      # Ushbu to'liq texnik hujjat
│
├── 📁 core/                   # Asosiy AI va media vositalari
│   ├── __init__.py
│   ├── ai_engine.py           # Google Gemini SDK, avtomatik model fallback, STT
│   └── ffmpeg_utils.py        # Videodan audio ajratish, MP3 konvertatsiya, FFmpeg
│
├── 📁 database/               # Kontekst va xotira boshqaruvi
│   ├── __init__.py
│   ├── context_manager.py     # SQLite (aiosqlite) orqali chat tarixi va whitelistni saqlash
│   └── chat_history.db        # Mahalliy SQLite ma'lumotlar bazasi
│
├── 📁 handlers/               # Xabarlar oqimini qayta ishlash
│   ├── __init__.py
│   ├── message_handler.py     # Markaziy router (Whitelist va xabar turini aniqlash)
│   ├── text_handler.py        # Matnli so'rovlar va boshqaruv buyruqlari (.help, .clear va hk.)
│   ├── media_handler.py       # Ovozli/video xabarlarni yuklab olish va AI ga uzatish
│   └── output_handler.py      # "typing..." animatsiyasi va uzun xabarlarni bo'lib yuborish
│
├── 📁 utils/                  # Yordamchi utility funksiyalar
│   ├── __init__.py
│   └── helpers.py             # Banner chiqarish, vaqtni formatlash
│
└── 📁 downloads/              # Vaqtinchalik audio/video fayllar joyi (avtomatik tozalanadi)
```

---

## ⚙️ 4. Texnologiyalar Staki

| Qism | Texnologiya | Izoh |
|---|---|---|
| **Userbot Framevork** | `Telethon` (1.45.0) | Telegram MTProto asinxron mijozi |
| **Sun'iy Intellekt** | `google-genai` (2.24.0) | Google Gemini zamonaviy rasmiy SDK |
| **AI Modeli** | `gemini-3.5-flash-lite` | Tezkor, arzon va multimodal tahlil qila oluvchi model |
| **Media Protsessor** | `FFmpeg` (9.0.1) | Audio/video konvertatsiya va formatlash |
| **Ma'lumotlar Bazasi** | `SQLite` + `aiosqlite` | Xabarlar tarixi (Context Manager) va doimiy Whitelist |
| **Muhit** | Python 3.12 (Windows) | Asinxron (`asyncio`) arxitektura |

---

## 🛠 5. Hal Qilingan Muammolar va Maxsus Yechimlar (Troubleshooting)

1. **Windows Konsolida Emoji va UTF-8 Muammosi:**
   - *Muammo:* Windows konsoli (`cp1251` / `charmap`) 🤖, 🧹 kabi emojilarni chiqara olmasdan `UnicodeEncodeError` bergandi.
   - *Yechim:* `main.py` boshiga `sys.stdout.reconfigure(encoding="utf-8")` va `sys.stderr.reconfigure(encoding="utf-8")` qoʻshildi.

2. **Google Gemini Modelining 404 Xatoligi (`gemini-1.5-flash`):**
   - *Muammo:* Google yangi API versiyasida eski `gemini-1.5-flash` modelini toʻxtatgan (deprecated qilgan).
   - *Yechim:* Model `gemini-3.5-flash-lite` ga yangilandi.

3. **Model Fallback (Avtomatik Zaxira Tizimi):**
   - *Yechim:* `ai_engine.py` da `_generate_content_with_fallback()` funksiyasi yaratildi. Agar tanlangan model vaqtincha band (503) yoki mavjud boʻlmasa, bot toʻxtab qolmasdan quyidagi roʻyxat boʻyicha navbatdagi modelga avtomatik oʻtadi:
     `gemini-3.5-flash-lite` ➔ `gemini-3.1-flash-lite` ➔ `gemini-3.8-flash` ➔ `gemini-flash-latest`.

4. **Xotira va Disk Tozaligi:**
   - Yuklab olingan audio/video fayllar AI tahlilidan soʻng `finally` blokida darhol diskdan oʻchirib tashlanadi (`_cleanup_files`).

5. **Render Docker Muhitida `google-genai` Import Xatosi:**
   - *Muammo:* `requirements.txt` da eski `google-generativeai` koʻrsatilgani tufayli Docker build paytida `from google import genai` chaqirilganda `ImportError: cannot import name 'genai' from 'google'` xatoligi yuz bergan.
   - *Yechim:* `requirements.txt` fayliga `google-genai>=0.1.0` qoʻshildi va omborga qayta push qilindi.

6. **Render Bepul Tarifida Port Scan Timeout:**
   - *Muammo:* Render bepul (Free) tarifida faqat Web Service-larni qabul qiladi va konteyner belgilangan portda (`PORT=10000`) ulanishlarni kutmasa, uni xato deb oʻchirib qoʻyadi.
   - *Yechim:* `main.py` ga yengil asinxron HTTP Health Check serveri qoʻshildi, bu orqali Render servisni uzluksiz `Live` holatda ushlab turadi.

7. **Foydalanuvchining Shaxsiy Yozish Uslubi va Tabiiy Muloqot Sozlamasi:**
   - *Xususiyat:* Bot oʻzini robot yoki sunʼiy intellekt deb tanishtirmasligi, "Qanday yordam bera olaman?" kabi gaplarni aytmasligi uchun maxsus shaxsiy profil va qatʼiy qoidalar kiritildi. Bot akkaunt egasi nomidan Telegramda qisqa (1-2 gap), amaliy, "hullas", "bo'ldi", "ishdaman" kabi kundalik soʻzlardan foydalanib, xuddi band insondek javob qaytaradi. Moliyaviy va jiddiy masalalarda avtomatik oʻylab "Hozir band edim, keyinroq o'zim yozvoraman" deb javob beradi.

---

## 🎮 6. Userbot Buyruqlari

| Buyruq | Vazifasi |
|---|---|
| `.help` | Barcha mavjud buyruqlar roʻyxatini chiqaradi |
| `.clear` yoki `.reset` | Ushbu chatdagi suhbat tarixini SQLite bazasidan oʻchiradi |
| `.ping` | Bot aloqasi va ishlashini tekshiradi |
| `.whitelist list` | Ruxsat etilgan chatlar roʻyxatini koʻrsatadi |
| `.whitelist add [id]` | Joriy yoki koʻrsatilgan chatni ruxsatnomaga kiritadi |
| `.whitelist remove [id]` | Chatni ruxsatnomadan chiqaradi |
| `.stt` | Ovozli xabarga javoban (reply) yozilsa, uning matnini chiqarib beradi |

---

## 🚀 7. Loyihani Mahalliy Qayta Ishga Tushirish

Loyihani kompyuterda istalgan vaqtda ishga tushirish uchun PowerShell yoki CMD da quyidagi buyruq beriladi:

```powershell
cd C:\Users\user\Desktop\AI_Asistent
python main.py
```

*Birinchi kirishda yaratilgan `ai_userbot.session` fayli sababli qayta telefon raqam yoki kod soʻralmaydi.*

---

## 🌐 8. Bulutli Serverga Joylashtirish (Render & GitHub Deployment)

Loyiha kompyuter oʻchiq boʻlganda ham 24/7 ishlashi uchun **Render** bulutli platformasiga Docker konteyneri orqali joylashtirildi.

- **GitHub Ombori:** [axadullayev01-commits/MyAsistent](https://github.com/axadullayev01-commits/MyAsistent)
- **Render Dashboard:** [ai-asistent-bot boshqaruv paneli](https://dashboard.render.com/web/srv-db882con74is73e5k7ng)
- **Servis URL:** `https://ai-asistent-bot.onrender.com`
- **Holati:** `Live` (24/7 faol)
- **Konteynerlashtirish:** `Dockerfile` orqali Linux muhitida Python 3.12 va `FFmpeg` toʻliq integratsiya qilingan (audio/video xabarlarni serverda muammosiz konvertatsiya qilish uchun).
- **Sessiya Boshqaruvi:** Serverda SMS kod kiritish talab etilmasligi uchun mahalliy Telegram sessiyasidan `StringSession` generatsiya qilinib, Render muhit oʻzgaruvchilariga (`STRING_SESSION`) kiritildi.
- **Avtomatik Deploy (CI/CD):** GitHub repozitoriyasining `main` tarmogʻiga yangi oʻzgarishlar kiritilganda Render avtomatik ravishda yangi versiyani quradi va deploy qiladi.

