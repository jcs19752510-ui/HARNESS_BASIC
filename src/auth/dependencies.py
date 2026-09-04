import hmac
from typing import Optional

from fastapi import Depends, Form, HTTPException, Request, status

from src.auth.session import SESSION_COOKIE_NAME, load_session


class NotAuthenticated(Exception):
    """미인증 상태로 보호된 경로 접근 (docs/trd/attend_a1_trd.md AC-7). main.py에서 302로 변환."""


def get_session(request: Request) -> Optional[dict]:
    cookie_value = request.cookies.get(SESSION_COOKIE_NAME)
    return load_session(cookie_value)


async def require_login(request: Request) -> dict:
    """보호된 경로 공통 의존성. A2~A6에서도 그대로 재사용 가능하게 분리.

    활동 시 자동 연장(AC-6)은 여기서 직접 쿠키를 갱신하지 않는다 — 라우트가 자체
    Response(TemplateResponse/RedirectResponse 등)를 반환하면 FastAPI가 이 함수에
    주입된 Response의 헤더를 병합하지 않아 조용히 무시되기 때문(코드리뷰에서 발견됨).
    대신 request.state.session에 세션을 남기고, SessionRenewalMiddleware(main.py)가
    응답 종류와 무관하게 항상 쿠키를 갱신한다.
    """
    session = get_session(request)
    if session is None:
        raise NotAuthenticated()
    request.state.session = session
    return session


async def verify_csrf(
    session: dict = Depends(require_login),
    csrf_token: Optional[str] = Form(None),
) -> bool:
    """CR-001 / docs/attend_adr.md ADR-006 — 상태변경 POST에 세션 바인딩 CSRF 토큰 요구."""
    expected = session.get("csrf_token")
    if not csrf_token or not expected or not hmac.compare_digest(csrf_token, expected):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="CSRF 토큰이 유효하지 않습니다")
    return True
