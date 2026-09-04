from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse

from src.auth.dependencies import NotAuthenticated
from src.db import Base, engine
from src.routes.auth import router as auth_router

# 마이그레이션 도구(Alembic 등)는 아직 미확정 — 우선 create_all로 부트스트랩.
# (docs/workorder/attend_a1_workorder.md §0은 "마이그레이션"을 언급하지만 도구가
#  tech_conventions에 아직 없어 판단 근거로 남김 — 실제 운영 마이그레이션 전략은 별도 결정 필요)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="학생 출결 등록 프로그램")


@app.exception_handler(NotAuthenticated)
async def not_authenticated_handler(request: Request, exc: NotAuthenticated):
    # docs/trd/attend_a1_trd.md AC-7 — 세션 없이 보호된 경로 접근 시 /login으로 리다이렉트
    return RedirectResponse(url="/login", status_code=302)


app.include_router(auth_router)
