---
name: harness-prompt-gen
description: Assembles the final AI-delegation prompt for one harness execution unit from its TRD + 작업지시서(work order) + optional A0 handoff, following harness/harness_04_prompt_generator_template.md's 6-block format exactly. Use when a unit's TRD and work order are both confirmed (Phase B step 4) and you need the standardized prompt to hand off to an AI coding session, instead of assembling it by hand.
argument-hint: "[trd-path] [workorder-path] [a0-path(optional)]"
allowed-tools: Read, Glob
---

이 스킬은 `harness/harness_04_prompt_generator_template.md`가 정의한 "즉흥적으로
프롬프트를 쓰면 세션마다 품질이 들쭉날쭉해진다"는 문제를 실제로 막기 위한
것입니다. 절대 템플릿 내용을 이 스킬 안에 따로 복제해서 쓰지 마세요 — 매번
`harness/harness_04_prompt_generator_template.md`를 **직접 읽고** 그 시점의
최신 6-블록 규격을 그대로 따르세요. 그래야 그 문서가 나중에 바뀌어도 이 스킬이
자동으로 최신 규격을 따라갑니다.

## 절차

1. `harness/harness_04_prompt_generator_template.md`를 읽고 블록 1~6의 정확한
   조합 규칙과 체크리스트를 확인한다.
2. 인자로 받은 TRD 경로를 읽는다. 없으면 사용자에게 경로를 물어본다(추측 금지).
   - §0-1(비기능요구사항), §1~§4(스펙), §5(AC), §6(테스트시나리오), §7(미결항목)
3. 인자로 받은 작업지시서(work order) 경로를 읽는다.
   - §1(이번 단계 범위), §2(안 하는 것), §3(착수 전 확정 정책)
4. A0 경로가 주어졌으면 읽는다. 없으면 블록 6은 생략하고 그 사실을 출력에
   명시한다("이전 세션 없음 — 블록 6 생략").
5. 블록 1~6을 템플릿 순서 그대로 조합해 최종 프롬프트를 하나의 코드블록으로
   출력한다.
6. `harness_04`의 "체크리스트(프롬프트 발송 전 최종 확인)" 5개 항목을 스스로
   점검해서 pass/fail로 보고한다. 하나라도 fail이면 프롬프트를 발송용으로
   제시하지 말고, 무엇이 비어서 실패했는지 구체적으로 말하고 멈춘다.
7. TRD/작업지시서에 `[ ]`나 `[사람 작성]`이 채워지지 않은 채 남아있는 필수
   섹션이 있으면(특히 §5 AC, §0-1), 조합을 진행하지 말고 먼저 채워야 한다고
   보고한다 — 빈 AC로 프롬프트를 만들면 "코드 작성 전 AC 확정" 원칙
   (`harness_00_overview.md` 규칙 2) 위반이다.

## 하지 않는 것
- TRD/작업지시서 내용을 스스로 지어내거나 빈칸을 임의로 채우지 않는다.
- 조합된 프롬프트를 스스로 실행(AI 세션에 위임)하지 않는다 — 결과물만 낸다.
- git 작업을 하지 않는다.
