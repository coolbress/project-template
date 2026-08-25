<!-- 제목은 Conventional Commits 로: type(scope): 요약
     형태의 근거는 census 다 — 중앙값 3절 · 빈 체크리스트 62%(중앙값 5항목) ·
     인라인 HTML 주석 70% · "type of change" 는 11.5%뿐이라 CC 를 쓰면 뺀다. -->

## 무엇을 왜

<!-- 결론부터. 무엇을 바꿨고 왜 필요했는지.
     이슈가 있으면 `Closes #N` 으로 닫는다. -->

## 어떻게 확인했나

<!-- 돌린 것과 결과. 버그 수정이면 그 버그를 재현하는 테스트를 먼저 넣는다. -->

## 확인

- [ ] `ci / lint` · `ci / typecheck` · `ci / test` · `ci / build` 4검사 초록
- [ ] **변경과 같은 PR 에 테스트가 실렸다** (테스트는 코드와 같은 change-unit 이다)
- [ ] 락파일을 갱신했다면 커밋했다 (`uv.lock`)
- [ ] 시크릿을 커밋하지 않았다 — 설정은 환경으로, `.env` 는 ignore
- [ ] 공개 표면을 바꿨다면 README/CHANGELOG 를 같이 고쳤다
