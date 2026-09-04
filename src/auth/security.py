import bcrypt

# docs/attend_adr.md ADR-004 — 비밀번호는 bcrypt 해시로만 저장, 평문 저장/전송 금지


def hash_password(plain_password: str) -> str:
    return bcrypt.hashpw(plain_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(plain_password.encode("utf-8"), password_hash.encode("utf-8"))
