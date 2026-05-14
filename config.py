import os

# ── Bot token ─────────────────────────────────────────────────────────────────
# Option 1 (recommended): set the environment variable before running:
#   export BOT_TOKEN="123456:ABC-your-token-here"
#
# Option 2: paste your token directly below (not recommended for public repos)
BOT_TOKEN: str = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")

if BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
    raise RuntimeError(
        "BOT_TOKEN is not set.\n"
        "Either export BOT_TOKEN=<your token> or edit config.py directly."
    )
