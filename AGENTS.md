# 이 저장소에서 일하는 법

**`coolbress` 의 새 파이썬 저장소가 태어나는 copier 템플릿이다.**
`CLAUDE.md` 는 이 파일을 가리키는 심볼릭 링크다 — **정본은 `AGENTS.md`.**

## 🔴 루트와 `template/` 을 헷갈리지 마라

| 고칠 것 | 어디 |
|---|---|
| **인스턴스가 받는 것** (CI·문서·`pyproject`·시험) | `template/` |
| **이 저장소 자신** (렌더 하네스·자기 CI·자기 시험) | 루트 |

`_subdirectory: template` 이라 **렌더 대상은 `template/` 뿐이다.**

## 검사

```bash
uv sync --locked
uv run ruff check . && uv run ruff format --check .
uv run mypy .
uv run pytest
```

## 규율

- **⚠️ 잡 이름 `ci` 를 바꾸지 마라.** 검사 이름이 `{호출잡}/{피호출잡}` 이라
  룰셋의 `ci / lint`·`ci / test`·… 와 묶여 있다. 바꾸면 **저장소가 조용히 머지 불가로 잠긴다**
- **템플릿을 고쳤으면 `pytest` 가 실제로 렌더해서 본다.** 설정을 읽는 것과
  렌더가 되는지 보는 것은 **다른 문장**이다 — 그걸 몰라서 두 번 조용히 망가뜨렸다.
  그리고 렌더가 된다는 것과 **생성된 저장소가 초록이라는 것**도 다른 문장이다:
  `test_generated_project_passes_its_own_checks` 가 렌더한 뒤 `uv sync --locked`·`ruff`·`mypy`·`pytest` 를 거기서 돌린다
- **이름 치환은 `copier.yml` 의 jinja 다.** `bootstrap.sh` 는 없다 —
  jinja 는 파일을 **만들기 전에** 정하고, `validator` 가 못 만들 이름을 **아무것도 만들기 전에** 막는다
- **인스턴스에 영향이 가면 태그를 올린다.** 판정 기준은 하나 —
  *`copier update` 를 돌린 인스턴스가 손으로 뭔가 해야 하는가*
- `main` 은 보호돼 있다. **브랜치 → PR → CI 초록 → squash 머지**
