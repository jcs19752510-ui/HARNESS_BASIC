from typing import Optional

from fastapi import Depends, Form, HTTPException, Request, Response, status

from src.auth.session import SESSION_COOKIE_NAME, load_session, set_session_cookie


class NotAuthenticated(Exception):
    """미인증 상태로 보호된 경로 접근 (docs/trd/attend_a1_trd.md AC-7). main.py에서 302로 변환."""


def get_session(request: Request) -> Optional[dict]:
    cookie_value = request.cookies.get(SESSION_COOKIE_NAME)
    return load_session(cookie_value)


async def require_login(request: Request, response: Response) -> dict:
    """보호된 경로 공통 의존성. A2~A6에서도 그대로 재사용 가능하게 분리."""
    session = get_session(request)
    if session is None:
        raise NotAuthenticated()
    # 활동 시 자동 연장 (docs/trd/attend_a1_trd.md AC-6 "활동 시 자동 연장")
    set_session_cookie(response, session)
    request.state.session = session
    return session


async def verify_csrf(
    session: dict = Depends(require_login),
    csrf_token: Optional[str] = Form(None),
) -> bool:
    """CR-001 / docs/attend_adr.md ADR-006 — 상태변경 POST에 세션 바인딩 CSRF 토큰 요구."""
    if not csrf_token or csrf_token != session.get("csrf_token"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="CSRF 토큰이 유효하지 않습니다")
    return True
