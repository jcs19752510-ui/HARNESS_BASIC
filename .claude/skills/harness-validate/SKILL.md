---
name: harness-validate
description: Validates one harness document (TRD, work order, A0, ADR, release plan, RACI, etc.) against the required-field checklist in harness/harness_19_template_validation.md §1, flags remaining "[ ]"/"[사람 작성]" placeholders, and runs the §3 AC-ambiguity keyword check for TRDs. Use before marking any harness document as "확정" or before moving to the next Phase/unit.
argument-hint: "[doc-path]"
allowed-tools: Read, Grep, Glob
---

이 스킬은 `harness/harness_19_template_validation.md` §3이 이미 예고한
"간단한 lint 스크립트로 전환 가능"을 실제로 구현한 것입니다. §1의 필수필드
표를 이 스킬 안에 복제하지 마세요 — 매번 `harness_19_template_validation.md`를
**직접 읽고** 그 시점 최신 표를 기준으로 판정하세요.

## 절차

1. `harness/harness_19_template_validation.md` §1(필수 필드 표)과 §3(AC
   모호성 검출 규칙)을 읽는다.
2. 인자로 받은 문서 경로를 읽는다.
3. 파일명/제목으로 문서 유형을 판별한다(TRD / 작업지시서 / A0 / ADR /
   릴리스계획 / 개인정보생애주기 / 기술컨벤션 / 백업DR / RACI / 변경관리 /
   병렬작업 / UX디자인프로세스). 판별이 애매하면 추측하지 말고 사용자에게
   묻는다.
4. §1 표에서 해당 문서 유형의 필수 필드 목록을 가져와, 문서 안에서 그 섹션이
   `[ ]`, `[사람 작성]`, 빈 표 행, "추후 작성" 등 미완성 상태로 남아있는지
   확인한다. **단, `harness_19 §4` 프로젝트 규모별 적용 프로파일에서 "생략
   가능"으로 명시된 조합(예: 1인 프로젝트의 RACI 정식 매트릭스)은 결격
   사유로 잡지 않는다** — 이것도 §4를 직접 읽어서 확인하고, 추측하지 않는다.
5. 문서가 TRD라면 §3의 AC 모호성 금지어("적절히", "알아서", "충분히",
   "가능한 한", "잘 동작", "필요시")가 구체 수치/조건 없이 §5 AC 텍스트에
   남아있는지 확인한다.
6. 결과를 표로 보고한다: [필드/항목 | 상태(OK/누락/모호) | 근거 줄번호].
   전부 OK가 아니면 마지막에 "다음 단계 진행 차단 대상" 요약을 명시한다
   (§2 검증 절차의 "반려" 개념 그대로).

## 하지 않는 것
- 빈 필드를 스스로 채우지 않는다. 검증만 하고 수정은 사용자/별도 작업으로 넘긴다.
- 검증 결과만으로 문서를 "확정" 상태로 바꾸지 않는다 — 그건 여전히 사람의 몫이다.
