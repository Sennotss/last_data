import html
import json
import os
import urllib.request
import uuid

# Batas Telegram 4096 karakter per pesan, sisakan ruang untuk tag <pre>
MAX_CHUNK = 3900


def split_chunks(text: str, limit: int = MAX_CHUNK):
    chunks, current = [], ""
    for line in text.splitlines(keepends=True):
        while len(line) > limit:
            if current:
                chunks.append(current)
                current = ""
            chunks.append(line[:limit])
            line = line[limit:]
        if len(current) + len(line) > limit:
            chunks.append(current)
            current = ""
        current += line
    if current.strip():
        chunks.append(current)
    return chunks


def get_config():
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        print("TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID belum di-set, skip kirim telegram")
        return None, None
    return token, chat_id


def send_telegram_file(filename: str, content: str, caption: str = "") -> bool:
    token, chat_id = get_config()
    if not token:
        return False

    boundary = uuid.uuid4().hex
    parts = []
    for name, value in (("chat_id", chat_id), ("caption", caption)):
        parts.append(
            f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="{name}"\r\n\r\n'
            f"{value}\r\n".encode()
        )
    parts.append(
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="document"; filename="{filename}"\r\n'
        f"Content-Type: text/plain; charset=utf-8\r\n\r\n".encode()
        + content.encode("utf-8")
        + b"\r\n"
    )
    parts.append(f"--{boundary}--\r\n".encode())

    url = f"https://api.telegram.org/bot{token}/sendDocument"
    req = urllib.request.Request(
        url,
        data=b"".join(parts),
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
    )
    try:
        urllib.request.urlopen(req, timeout=60).read()
    except Exception as e:
        print(f"Gagal kirim file telegram: {e}")
        return False
    return True


def send_telegram(text: str) -> bool:
    token, chat_id = get_config()
    if not token:
        return False

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    for chunk in split_chunks(text):
        payload = json.dumps({
            "chat_id": chat_id,
            "text": f"<pre>{html.escape(chunk)}</pre>",
            "parse_mode": "HTML",
        }).encode()
        req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
        try:
            urllib.request.urlopen(req, timeout=30).read()
        except Exception as e:
            print(f"Gagal kirim telegram: {e}")
            return False
    return True
