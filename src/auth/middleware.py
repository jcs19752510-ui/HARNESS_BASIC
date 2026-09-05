from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from src.auth.session import set_session_cookie


class SessionRenewalMiddleware(BaseHTTPMiddleware):
    """docs/trd/attend_a1_trd.md AC-6 "활동 시 자동 연장"을 응답 종류와 무관하게 강제한다.

    require_login이 인증에 성공하면 request.state.session을 채워두고, 이 미들웨어가
    응답이 나간 직후 쿠키를 갱신한다. (require_login 내부에서 직접 쿠키를 설정하지
    않는 이유는 dependencies.py의 require_login 문서 참조 — 코드리뷰에서 발견된
    버그의 수정.)
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)
        session = getattr(request.state, "session", None)
        if session is not None:
            set_session_cookie(response, session)
        return response
