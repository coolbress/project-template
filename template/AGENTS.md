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
uv build          # 🔴 룰셋이 `ci / build` 를 필수로 요구한다
```

CI 는 이 다섯을 **각각 별도 검사**로 돌린다. 로컬에서 통과시키고 PR 을 연다.

## 읽고 시작해라

- **설정의 정본은 [`pyproject.toml`](pyproject.toml)** — 줄길이 · ruff 규칙 · `mypy --strict` ·
  `filterwarnings`. **안 읽으면 lint 가 깨져서 알게 된다**
- **[`CONTRIBUTING.md`](CONTRIBUTING.md) 를 PR 열기 전에 읽어라** — 짧다. 테스트 정책 ·
  PR 크기의 근거 · `AC-n` 규칙이 거기 있다

## 규율

- **다음 할 일은 `gh issue list` 가 정본이다.** 백로그를 닫힌 이슈 안에 두지 않는다
- **인수기준은 이슈에 `AC-n` 으로 산다.** 각 AC 에 **그것을 증명하는 검사**(시험 이름 · CI 잡)를 적는다.
  PR 은 어느 AC 를 닫는지 밝힌다. `/to-tickets` 가 만든 티켓도 같은 규칙이다
- 증명할 검사를 못 정하겠으면 **`UNVERIFIABLE` 이라고 쓰고 사람에게 말한다.** 조용히 넘기지 않는다
- **동작이나 버그가 바뀌면 그 변화를 잡는 테스트를 같은 PR 에 넣는다. 해당하지 않으면 이유를 적는다.**
- **`/implement` 는 커밋에서 끝난다.** 그 **전에** 브랜치(`git switch -c feat/<슬러그>`), 그 **뒤에**
  `gh pr create`. `main` 직접 푸시는 룰셋이 거부한다
- **PR diff 는 200줄을 목표로, 400줄이 상한이다** — `ci / diff-size` 가 상한을 막는다
  (문서·락파일은 안 센다). 근거와 그 한정은 `CONTRIBUTING.md` 에 있다
- **PR 제목은 `type(scope): 요약`** — `ci / pr-title` 이 막는다. 타입은 표준 11종뿐이고
  🔴 **새 타입을 만들지 마라.** 남는 의미는 scope 로 쓴다(`docs(research):`·`refactor(layout):`)
- CI 로직은 여기 없다 — `coolbress/workflows` 에 있고 `ci.yml` 이 SHA 로 핀한다.

## 기획할 때 (`/grill-with-docs`)

- **첫 라운드에 묻는다: 같은 걸 푸는 것이 이미 있나** — 제품 · 라이브러리 · 이 저장소 안. 없다고 하기 전에 찾아본다
- **유도 질문 금지.** 가정(*"~하고 싶으시죠?"*)이 아니라 **과거의 구체적 행동**을 묻는다
- **"안 만들 것"** 을 반드시 받는다. 비워두면 범위가 조용히 넓어진다
- **개인정보를 다루게 되면 멈추고 사람에게 묻는다**(`decision:approval`). 공개 여부 · 라이선스는 `/new-project` 가 이미 받았다

## Agent skills

### Issue tracker

GitHub Issues — `gh` 로 읽고 쓴다. See [`docs/agents/issue-tracker.md`](docs/agents/issue-tracker.md).

### Triage labels

기본 다섯(`needs-triage` · `needs-info` · `ready-for-agent` · `ready-for-human` · `wontfix`) 그대로 — `new-project.sh` 가 만든다.
See [`docs/agents/triage-labels.md`](docs/agents/triage-labels.md).

### Domain docs

single-context — 루트 `CONTEXT.md` + `docs/adr/`. See [`docs/agents/domain.md`](docs/agents/domain.md).

> ⚠️ **150줄을 넘기지 마라.** 실측(ETH Zurich · 138 repos · 5,694 PR): 컨텍스트 파일은
> 추론비용을 **20~159%** 올리고, **비관련 내용은 지시 전체의 무시**를 부른다.
> **상태(*"지금 어디까지"*)를 여기 넣지 마라** — 그건 열린 이슈가 갖는다.
