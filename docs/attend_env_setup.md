# 학생 출결 등록 프로그램 — 로컬 개발환경 셋업

> 마스터 TRD와 A1 작업지시서가 참조하는 문서입니다(기존에 파일이 없어 참조가
> 깨져 있었음 — 하네스 리뷰에서 발견, 이번에 신규 작성). 스택은
> `docs/attend_tech_conventions.md` §1에서 확정한 대로입니다.

---

## 1. 사전 준비
- Python 3.11 이상
- Git
- NeonDB(PostgreSQL) 프로젝트 — 접속 문자열(`DATABASE_URL`) 발급 완료

## 2. 로컬 셋업 절차
```bash
# 1) 가상환경 생성/활성화
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate

# 2) 의존성 설치 (requirements.txt는 A1 구현 시 함께 생성됨)
pip install -r requirements.txt

# 3) 환경변수 파일 준비
cp .env.example .env
# .env를 열어 DATABASE_URL, SESSION_SECRET_KEY를 실제 값으로 채운다.
# ⚠️ .env는 .gitignore에 포함되어 있어 커밋되지 않는다 — Claude Code 등 AI 에이전트에게도
#    이 파일 내용을 직접 붙여넣거나 전달하지 않는다 (harness_05 §3).

# 4) 로컬 HTTP로 개발할 경우에만 (운영에서는 절대 끄지 않음)
#    .env에서 SESSION_COOKIE_SECURE=false 로 설정 (docs/attend_adr.md ADR-007 참조)

# 5) 테스트 실행
pytest -q
```

## 3. AI 에이전트(Claude Code) 세션에 줄 것 / 주지 말 것
- 줄 것: `.env.example`, `docs/attend_tech_conventions.md`, 해당 단위 TRD/작업지시서
- 주지 말 것: 실제 `.env` 값, 실제 `DATABASE_URL`, 운영 DB 접속 정보 (`harness_05 §3`)
- AI 세션은 로컬 `.env`가 이미 설정되어 있다는 전제로 코드만 작성하고, 실행/테스트는
  로컬에 설정된 환경변수를 참조하게 한다.

## 4. pre-commit 훅 설치 (시크릿 유출 방지)
루트의 `.pre-commit-config.yaml`을 사용합니다 — 커밋 전 `.env` 등 시크릿이 섞여
들어가는 것을 자동 차단합니다.
```bash
pip install pre-commit
pre-commit install
```
설치 후에는 `git commit` 시 자동으로 시크릿 스캔이 실행됩니다. 최초 1회 전체
파일 스캔은 `pre-commit run --all-files`로 수동 실행할 수 있습니다.

## 5. CI
`.github/workflows/ci.yml`이 PR마다 pytest와 시크릿 스캔을 자동 실행합니다
(`harness_05 §2` 참조). `requirements.txt`가 아직 없는 초기 단계에서는 의존성
설치 단계를 건너뛰고 테스트 단계만 실행되며, 테스트가 아직 없어도 실패로
처리하지 않습니다(“수집된 테스트 없음”은 정상 취급) — A1 구현이 들어오는 순간부터
실제 테스트가 CI에 반영됩니다.
