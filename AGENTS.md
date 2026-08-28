# 이 저장소에서 일하는 법

> **이 파일이 정본이고 `CLAUDE.md` 는 심볼릭 링크다.** `AGENTS.md` 는 Codex · Cursor ·
> Copilot · Gemini CLI 등 20개 이상이 읽는 표준이고 `CLAUDE.md` 는 Claude Code 만 읽는다.
> 링크라 **드리프트가 0** 이다 — 사본을 두면 갈라진다.

`main` 은 보호돼 있다. **브랜치 → PR → CI 초록 → 머지**로만 들어간다.
직접 푸시도 빨간불 머지도 `--admin` 강제도 거부된다 — 소유자도 못 넘는다.

```bash
uv sync --locked          # 락파일과 어긋나면 실패한다
uv run ruff check . && uv run ruff format --check .
uv run mypy .
uv run pytest
```

CI 는 이 넷을 **각각 별도 검사**로 돌린다. 로컬에서 통과시키고 PR 을 연다.

## 읽고 시작해라

- **설정의 정본은 [`pyproject.toml`](pyproject.toml)** — 줄길이 · ruff 규칙 · `mypy --strict` ·
  `filterwarnings`. **안 읽으면 lint 가 깨져서 알게 된다**
- **[`CONTRIBUTING.md`](CONTRIBUTING.md) 를 PR 열기 전에 읽어라** — 짧다. 테스트 정책 ·
  PR 크기의 근거 · `AC-n` 규칙이 거기 있다

## 규율

- **다음 할 일은 `gh issue list` 가 정본이다.** 백로그를 닫힌 이슈 안에 두지 않는다
- **인수기준은 이슈에 `AC-n` 으로 산다.** PR 은 어느 AC 를 닫는지 밝힌다.
- 증명할 검사를 못 정하겠으면 **`UNVERIFIABLE` 이라고 쓴다.** 조용히 넘기지 않는다.
- **동작이나 버그가 바뀌면 그 변화를 잡는 테스트를 같은 PR 에 넣는다. 해당하지 않으면 이유를 적는다.**
- **PR diff 는 200줄을 목표로, 400줄이 상한이다** — `ci / diff-size` 가 상한을 막는다
  (문서·락파일은 안 센다). 근거와 그 한정은 `CONTRIBUTING.md` 에 있다
- CI 로직은 여기 없다 — `coolbress/workflows` 에 있고 `ci.yml` 이 SHA 로 핀한다.

> ⚠️ **150줄을 넘기지 마라.** 실측(ETH Zurich · 138 repos · 5,694 PR): 컨텍스트 파일은
> 추론비용을 **20~159%** 올리고, **비관련 내용은 지시 전체의 무시**를 부른다.
> **상태(*"지금 어디까지"*)를 여기 넣지 마라** — 그건 열린 이슈가 갖는다.
