# 🎬 Thumbnail Changer Bot

Changes the cover/thumbnail of any video file on Telegram without re-uploading — it re-sends the same file_id with your custom thumbnail.

---

## 📁 Files

```
thumbnail_bot/
├── main.py          # Bot logic
├── config.py        # Token config
├── requirements.txt # Dependencies
└── README.md
```

---

## 🚀 Setup

### 1. Get a bot token
Talk to [@BotFather](https://t.me/BotFather) → `/newbot` → copy the token.

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Set your token (pick one way)

**Environment variable (recommended):**
```bash
export BOT_TOKEN="123456:ABC-your-token-here"
```

**Or edit `config.py` directly:**
```python
BOT_TOKEN = "123456:ABC-your-token-here"
```

### 4. Run
```bash
python main.py
```

---

## 🤖 How to use

| Step | You do | Bot replies |
|------|--------|-------------|
| 1 | Send any **photo** | "✅ New Thumbnail Saved. Now send the video file." |
| 2 | Send any **video file** (with or without caption) | Re-sends the same file with your thumbnail + bold caption |

- `/start` — check if the bot is online
- Caption is **always sent as bold** regardless of how you type it (plain, italic, monospace, etc.)
- Thumbnail is saved per-user in memory (resets on bot restart)

---

## ⚙️ Notes

- The bot uses `file_id` re-sending — **no download or upload of the video happens**
- Supports: `.mkv`, `.mp4`, `.avi`, `.mov`, `.ts`, `.m2ts`, `.webm`, `.flv` and anything with a `video/*` MIME type
- Thumbnail must be a JPEG photo for best results (Telegram auto-converts)
- For persistent thumbnail storage across restarts, replace the `user_thumbnails` dict with a SQLite/Redis store
