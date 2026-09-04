import os

from dotenv import load_dotenv

load_dotenv()

# docs/attend_env_setup.md 참조 — 실제 값은 .env(gitignore 처리됨)에만 존재
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./dev.db")

# 세션 서명 키 (itsdangerous). 운영 값은 반드시 .env로만 주입 — 코드/문서에 하드코딩 금지
SESSION_SECRET_KEY = os.environ.get("SESSION_SECRET_KEY", "dev-insecure-secret-change-me")

# docs/attend_adr.md ADR-007 — 운영 기본값 true, 로컬 HTTP 개발 시에만 false로 완화
SESSION_COOKIE_SECURE = os.environ.get("SESSION_COOKIE_SECURE", "true").lower() == "true"

# docs/trd/attend_a1_trd.md AC-6 — 30분 미활동 시 만료
SESSION_MAX_AGE_SECONDS = 30 * 60
