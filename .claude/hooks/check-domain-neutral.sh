#!/bin/bash
# PostToolUse 훅 — Write/Edit 직후 도메인 중립 위반 가능성을 경고(차단 아님).
#
# 이 스크립트는 "완전한 도메인 탐지기"가 아닙니다 — 그런 건 원리적으로
# 불가능합니다(어떤 업무 도메인이든 올 수 있어서 키워드로 다 못 막음).
# 대신 이 저장소에서 실제로 검증 가능한 두 가지만 확인합니다:
#   A) 구조적 규칙: docs/src/tests는 .gitkeep 외에 실제 파일이 있으면 안 된다
#      (CLAUDE.md "프로젝트 개요" 규칙 그대로 — 이건 키워드 추측이 아니라
#      사실 확인이라 오탐이 거의 없음)
#   B) 회귀 감시: 이 저장소에서 실제로 두 번 재발했던 특정 문구("졸업/전학")가
#      harness/*.md·CLAUDE.md·README.md에 다시 나타나는지 — 과거 사건 하나에
#      대한 좁은 회귀 방지책일 뿐, 새로운 종류의 도메인 누출은 못 잡음.

INPUT=$(cat)
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')
[ -z "$FILE_PATH" ] && exit 0

# 백슬래시 -> 슬래시 정규화, 저장소 루트 기준 상대경로로 변환
FILE_PATH_NORM="${FILE_PATH//\\//}"
PROJECT_DIR_NORM="${CLAUDE_PROJECT_DIR//\\//}"
REL_PATH="${FILE_PATH_NORM#"$PROJECT_DIR_NORM"/}"

WARN=""

# --- A) 구조적 규칙: docs/src/tests에 .gitkeep 아닌 실제 파일 ---
case "$REL_PATH" in
  docs/trd/*|docs/workorder/*|docs/handoff/*|src/*|tests/*)
    BASENAME="${REL_PATH##*/}"
    if [ "$BASENAME" != ".gitkeep" ]; then
      WARN="⚠️ 도메인 중립 규칙 위반 가능성: '$REL_PATH'는 HARNESS_BASIC이 항상 빈 골격으로 유지해야 하는 경로입니다(CLAUDE.md \"프로젝트 개요\"). 실제 프로젝트 코드/TRD/테스트라면 이 저장소가 아니라 'Use this template'으로 만든 별도 저장소에 있어야 합니다."
    fi
    ;;
esac

# --- B) 회귀 감시: 과거 실제로 재발했던 특정 문구 ---
case "$REL_PATH" in
  harness/*.md|CLAUDE.md|README.md)
    if [ -f "$FILE_PATH" ] && grep -qE '졸업|전학' "$FILE_PATH" 2>/dev/null; then
      REGRESSION="⚠️ 회귀 감지: '$REL_PATH'에 과거 두 차례 재발했던 교육기관 특정 문구(졸업/전학 계열)가 다시 감지됐습니다. harness_10_data_lifecycle.md §3 같은 곳에 실수로 들어간 게 아닌지 확인하세요."
      if [ -n "$WARN" ]; then
        WARN="$WARN\n$REGRESSION"
      else
        WARN="$REGRESSION"
      fi
    fi
    ;;
esac

if [ -n "$WARN" ]; then
  ESCAPED=$(echo -e "$WARN" | sed ':a;N;$!ba;s/\n/\\n/g' | sed 's/"/\\"/g')
  echo "{\"hookSpecificOutput\":{\"hookEventName\":\"PostToolUse\",\"systemMessage\":\"$ESCAPED\"}}"
fi
exit 0
