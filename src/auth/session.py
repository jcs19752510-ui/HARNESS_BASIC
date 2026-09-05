import secrets
from typing import Optional

from itsdangerous import BadData, URLSafeTimedSerializer
from starlette.responses import Response

from src import config

SESSION_COOKIE_NAME = "session"

_serializer = URLSafeTimedSerializer(config.SESSION_SECRET_KEY, salt="attend-session")


def create_session_payload(user_id: int, role: str) -> dict:
    return {"user_id": user_id, "role": role, "csrf_token": secrets.token_urlsafe(32)}


def load_session(cookie_value: Optional[str]) -> Optional[dict]:
    """서명/유효기간 검증 후 세션 payload 반환. 유효하지 않으면 None (docs/trd/attend_a1_trd.md AC-6)."""
    if not cookie_value:
        return None
    try:
        # SESSION_MAX_AGE_SECONDS는 매 호출 시 config 모듈에서 읽는다 (테스트에서 monkeypatch 가능하게)
        return _serializer.loads(cookie_value, max_age=config.SESSION_MAX_AGE_SECONDS)
    except BadData:
        # BadData는 BadSignature/SignatureExpired/BadPayload/BadHeader의 공통 상위 클래스.
        # (BadSignature만 잡으면 BadPayload는 걸러지지 않아 500으로 새는 버그였음 — 코드리뷰에서 발견)
        return None


def set_session_cookie(response: Response, payload: dict) -> None:
    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=_serializer.dumps(payload),
        max_age=config.SESSION_MAX_AGE_SECONDS,
        httponly=True,
        secure=config.SESSION_COOKIE_SECURE,
        samesite="lax",
    )


def clear_session_cookie(response: Response) -> None:
    response.delete_cookie(SESSION_COOKIE_NAME)
