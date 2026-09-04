from pathlib import Path

from fastapi import APIRouter, Depends, Form, Request, status
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from src.auth.dependencies import get_session, require_login, verify_csrf
from src.auth.security import verify_password
from src.auth.session import clear_session_cookie, create_session_payload, set_session_cookie
from src.db import get_db
from src.models.user import User

router = APIRouter()
templates = Jinja2Templates(directory=str(Path(__file__).resolve().parent.parent / "templates"))

# 계정 존재/활성 여부를 노출하지 않기 위한 공통 에러 메시지 (AC-2, AC-3, AC-4)
GENERIC_LOGIN_ERROR = "아이디 또는 비밀번호가 올바르지 않습니다"


@router.get("/login")
async def login_form(request: Request):
    if get_session(request) is not None:
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    return templates.TemplateResponse(request, "login.html", {"error": None})


@router.post("/login")
async def login_submit(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.username == username).first()

    # bcrypt는 의도적으로 CPU 연산이 무거운 함수라, 이벤트 루프에서 동기 호출하면
    # 동시 요청 전체가 그 시간만큼 블로킹된다 — 스레드풀로 오프로드 (코드리뷰에서 발견)
    password_ok = False
    if user is not None and user.use_yn == "Y":
        password_ok = await run_in_threadpool(verify_password, password, user.password_hash)

    # AC-2/AC-3/AC-4: 존재 여부/비활성 여부를 구분하지 않고 동일한 응답
    if user is None or user.use_yn != "Y" or not password_ok:
        return templates.TemplateResponse(
            request,
            "login.html",
            {"error": GENERIC_LOGIN_ERROR},
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    payload = create_session_payload(user_id=user.id, role=user.role.value)
    redirect = RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    set_session_cookie(redirect, payload)
    return redirect


@router.post("/logout")
async def logout(request: Request, _csrf_ok: bool = Depends(verify_csrf)):
    redirect = RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    clear_session_cookie(redirect)
    # verify_csrf -> require_login이 이 요청 초입에 request.state.session을 채워뒀으므로,
    # 여기서 비워두지 않으면 SessionRenewalMiddleware가 응답 직후 세션 쿠키를 다시
    # 발급해 로그아웃을 무효화한다 (fix 적용 중 회귀 테스트로 발견).
    request.state.session = None
    return redirect


@router.get("/")
async def home(request: Request, session: dict = Depends(require_login)):
    # 임시 placeholder — 메인 화면 상세 레이아웃은 A1 범위 밖
    # (docs/workorder/attend_a1_workorder.md §2). 로그인/로그아웃 흐름 확인용 최소 화면.
    return templates.TemplateResponse(request, "home.html", {"csrf_token": session["csrf_token"]})
