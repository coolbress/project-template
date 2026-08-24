# 이 저장소에서 일하는 법

`main` 은 보호돼 있다. **브랜치 → PR → CI 초록 → 머지**로만 들어간다.
직접 푸시도 빨간불 머지도 `--admin` 강제도 거부된다 — 소유자도 못 넘는다.

```bash
uv sync --locked          # 락파일과 어긋나면 실패한다
uv run ruff check . && uv run ruff format --check .
uv run mypy .
uv run pytest
```

CI 는 이 넷을 **각각 별도 검사**로 돌린다. 로컬에서 통과시키고 PR 을 연다.

- **인수기준은 이슈에 `AC-n` 으로 산다.** PR 은 어느 AC 를 닫는지 밝힌다.
- 증명할 검사를 못 정하겠으면 **`UNVERIFIABLE` 이라고 쓴다.** 조용히 넘기지 않는다.
- **소스를 고쳤으면 테스트도 고친다.**
- CI 로직은 여기 없다 — `coolbress/workflows` 에 있고 `ci.yml` 이 SHA 로 핀한다.
