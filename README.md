# project-template — copier 템플릿

`coolbress` 의 새 파이썬 저장소가 태어나는 곳. 바닥([`standards` direction/05](https://github.com/coolbress/standards/blob/main/direction/05-the-output-floor.md))이
요구하는 것들이 **처음부터 들어 있는 상태**로 만들어진다.

```bash
uvx copier copy gh:coolbress/project-template my-app
```

보통은 이걸 직접 부르지 않는다 — [`workflows/new-project.sh`](https://github.com/coolbress/workflows/blob/main/new-project.sh)
가 저장소 생성 · 룰셋 · CodeQL 까지 같이 세운다.

## 배치 — 루트와 `template/` 은 다른 물건이다

```
project-template/
├── copier.yml          ← 질문·조건·_subdirectory
├── pyproject.toml      ┐
├── src/template_render/│  **템플릿 자신의** 프로젝트.
├── tests/              │  하는 일은 하나 — 템플릿을 렌더해서 결과를 검사한다.
├── .github/workflows/  ┘  (이 저장소의 CI. 인스턴스로 안 간다)
└── template/           ← **인스턴스로 나가는 것은 여기뿐이다**
```

`_subdirectory: template` 이 그 경계다. copier 가 권하는 배치이고, 이유는
*"different dotfiles for your template and for the projects it generates"* 다.
이걸 안 쓰면 템플릿 자신의 CI·시험·`copier.yml` 이 인스턴스로 새거나,
반대로 인스턴스용 파일 이름에 `{{ }}` 가 들어가는 순간 템플릿 자신의 `pytest` 가 깨진다.

## 버전 — 태그를 읽는다

copier 는 **태그를 PEP 440 으로 비교해 최신을 고른다**(SemVer 가 아니다).
태그가 없으면 `HEAD` 로 떨어져 **안 익은 커밋으로 인스턴스를 끌고 간다.**

| | 무엇이 바뀌면 |
|---|---|
| **MAJOR** | `copier update` 를 돌린 인스턴스가 **손으로 뭔가 해야 한다** — 파일 이름 변경·삭제, 필수 질문 추가 |
| **MINOR** | 새 파일, 기본값 있는 새 질문, 새 시험 |
| **PATCH** | 문서·주석, 동작이 같은 고침 |

## 이미 만들어진 저장소를 따라잡히려면

```bash
uvx copier update            # 인스턴스에서. .copier-answers.yml 이 어디서 왔는지 기억한다
```

## 검사

```bash
uv sync --locked
uv run ruff check . && uv run ruff format --check .
uv run mypy .
uv run pytest                # 템플릿을 실제로 렌더해서 본다
```
