import os
import json
from itsdangerous import TimestampSigner, SignatureExpired, BadSignature
from urllib.parse import unquote_plus

def handler(request, token):
    try:
        signed = unquote_plus(token)
    except:
        return {"statusCode": 400, "body": "Bad token"}

    secret = os.environ.get("SIGNING_SECRET")
    if not secret:
        return {"statusCode": 500, "body": "SIGNING_SECRET missing"}

    expire = int(os.environ.get("EXPIRE_SECONDS", "3600"))
    signer = TimestampSigner(secret)

    try:
        raw = signer.unsign(signed, max_age=expire)
    except SignatureExpired:
        return {"statusCode": 410, "body": "Expired"}
    except BadSignature:
        return {"statusCode": 400, "body": "Invalid"}

    payload = json.loads(raw.decode())
    file_path = payload["file_path"]

    bot_token = os.environ.get("BOT_TOKEN")
    if not bot_token:
        return {"statusCode": 500, "body": "BOT_TOKEN missing"}

    download_url = f"https://api.telegram.org/file/bot{bot_token}/{file_path}"

    return {
        "statusCode": 302,
        "headers": {"Location": download_url}
    }
