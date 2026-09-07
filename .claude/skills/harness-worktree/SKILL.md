---
name: harness-worktree
description: Prints (does NOT execute) the exact git worktree commands needed to run two harness units' feature branches simultaneously in separate working directories, per harness/harness_15_parallel_work.md. Use when two units have been confirmed independent (§1 of that doc) and you want to work on both at once without one session's checkout stepping on the other's uncommitted changes.
argument-hint: "[unit-code-1] [unit-code-2] [base-branch]"
allowed-tools: Read
---

⚠️ **이 스킬은 git 명령을 스스로 실행하지 않습니다.** `CLAUDE.md`의
"Git 관련 작업 금지" 규칙에 따라, 이 스킬은 사용자가 그대로 복사해서 **직접
실행할** 명령어 텍스트만 출력합니다. 절대 Bash로 이 명령을 대신 실행하지
마세요(애초에 이 스킬엔 Bash 권한이 없습니다).

## 절차

1. `harness/harness_15_parallel_work.md`를 읽고 §1(병렬 가능 여부 판단
   기준)과 §3(인터페이스 계약 고정 규칙)을 사용자에게 먼저 상기시킨다 —
   "두 단위가 서로의 산출물에 의존하지 않는지 확인했는가?"를 반드시 되묻는다.
   의존관계가 있다고 답하면, 병렬 진행 대신 순차 진행을 권하고 중단한다.
2. 인자로 받은 unit-code-1, unit-code-2, base-branch로 아래 형태의 명령을
   정확히 채워서 코드블록으로 출력한다 (실행하지 않는다):

```
# 단위 1 작업 공간 생성
git worktree add ../{repo-name}-{unit-code-1} -b feature/{unit-code-1} {base-branch}

# 단위 2 작업 공간 생성
git worktree add ../{repo-name}-{unit-code-2} -b feature/{unit-code-2} {base-branch}

# 각 작업 공간에서 별도 Claude Code 세션을 엽니다
#   cd ../{repo-name}-{unit-code-1}   (세션 A)
#   cd ../{repo-name}-{unit-code-2}   (세션 B)
```

3. 각 단위 작업이 끝나고 `harness_05 §1` 머지 조건(AC 통과 + diff 리뷰 +
   CI 통과)을 충족해서 실제로 base 브랜치에 병합된 걸
   `git merge-base --is-ancestor`로 확인한 뒤에만 정리 명령을 출력한다:

```
git worktree remove ../{repo-name}-{unit-code-1}
git worktree remove ../{repo-name}-{unit-code-2}
```

4. `{repo-name}`은 사용자에게 실제 저장소 폴더명을 물어보거나, 확인 가능하면
   현재 작업 디렉토리명에서 추정해 출력에 명시적으로 보여준다(추정임을 표시).

## 하지 않는 것
- git 명령을 스스로 실행하지 않는다.
- 두 단위의 의존관계를 스스로 판단해서 "병렬 가능"이라고 단정하지 않는다 —
  항상 사용자 확인을 거친다.
