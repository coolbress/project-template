"""템플릿을 **실제로 렌더해서** 결과를 검사한다.

이 시험이 왜 이 모양인가 (2026-08-28):

전판은 `copier.yml` 을 **읽어서** 맞는지만 봤다. 그 방식으로는 안 잡히는 것이 있다 —
실제로 두 번 놓쳤고 둘 다 **렌더는 성공하고 조용히 망가지는** 형태였다:

1. **`{{ _copier_conf.answers_file }}.jinja` 을 안 만들었다** → 인스턴스에 `.copier-answers.yml`
   이 안 생겼고, 그러면 **`copier update` 가 아예 안 된다.** copier 를 쓰는 이유가 통째로 사라진다.
2. **`_preserve_symlinks` 를 안 켰다** → `CLAUDE.md` 가 심볼릭 링크에서 **사본**이 됐다.

🔵 그래서 이제 **렌더한다.** 설정을 읽는 것과 렌더가 되는지 보는 것은 다른 문장이다.
`template_render.render()` 가 그 하네스다.

⚠️ 이 파일은 **인스턴스로 안 간다.** `_subdirectory: template` 이라 렌더 대상이
`template/` 뿐이기 때문이다 — 전판에서는 이 파일이 인스턴스로 새고 있었다(죽은 파일이었다).
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
from pathlib import Path

import pytest

from template_render import TEMPLATE_ROOT, render

CONFIG = TEMPLATE_ROOT / "copier.yml"
SUBDIR = TEMPLATE_ROOT / "template"


@pytest.fixture(scope="module")
def rendered(tmp_path_factory: pytest.TempPathFactory) -> Path:
    return render(tmp_path_factory.mktemp("cli"))


# ── 설정 자체 ────────────────────────────────────────────────


def test_render_target_is_the_subdirectory() -> None:
    """`_subdirectory` 가 빠지면 루트(템플릿 자신의 CI·시험·`copier.yml`)가 통째로 복사된다."""
    assert "_subdirectory: template" in CONFIG.read_text(encoding="utf-8")
    assert SUBDIR.is_dir()


def test_answers_file_template_exists() -> None:
    """없으면 인스턴스가 `.copier-answers.yml` 을 못 받고 `copier update` 가 죽는다."""
    template = SUBDIR / "{{ _copier_conf.answers_file }}.jinja"
    assert template.is_file(), (
        "`{{ _copier_conf.answers_file }}.jinja` 이 없다. "
        "이게 없으면 인스턴스가 어느 판에서 태어났는지 기억하지 못해 update 가 불가능하다."
    )
    assert "_copier_answers" in template.read_text(encoding="utf-8"), "답을 실제로 써넣지 않는다"


def test_archetype_question_exists_with_the_narrow_default() -> None:
    cfg = CONFIG.read_text(encoding="utf-8")
    assert "archetype:" in cfg, "아키타입 질문이 없다 — 조건부 항목에 입력이 없어진다"
    assert "default: cli" in cfg, (
        "기본값이 가장 좁은 것이 아니다. 넓히는 것은 파일을 더하는 일이고 "
        "좁히는 것은 안 쓰는 파일을 지우는 일이라 스텁으로 남는다."
    )


# ── 렌더 결과 ────────────────────────────────────────────────


def test_answers_file_is_actually_written(rendered: Path) -> None:
    answers = rendered / ".copier-answers.yml"
    assert answers.is_file(), "설정은 맞는데 실제로는 안 써졌다 — 렌더해야만 보이는 실패다"
    body = answers.read_text(encoding="utf-8")
    assert "_src_path:" in body, "인스턴스가 어느 템플릿에서 왔는지 안 적힌다"


def test_claude_md_stays_a_symlink(rendered: Path) -> None:
    """사본이 되면 둘이 갈린다 — 링크로 둔 이유가 그것이다."""
    link = rendered / "CLAUDE.md"
    assert link.is_symlink(), "CLAUDE.md 가 심볼릭 링크가 아니다 (_preserve_symlinks 확인)"
    assert link.readlink().name == "AGENTS.md"


def test_template_internals_do_not_ship(rendered: Path) -> None:
    """루트의 것들이 인스턴스로 새면 안 된다."""
    for leaked in ("copier.yml", "tests/test_copier_template.py", "src/template_render"):
        assert not (rendered / leaked).exists(), f"{leaked} 이 인스턴스로 샜다"


def test_cli_archetype_omits_service_only_files(rendered: Path) -> None:
    """`.env.example` 은 service 맥락이다 (12-Factor · 바닥의 처분). 지우는 게 아니라 안 만든다."""
    assert not (rendered / ".env.example").exists()
    assert not (rendered / "tests" / "test_env_example.py").exists()


@pytest.mark.parametrize("archetype", ["backend", "data-ml"])
def test_service_archetypes_include_them(tmp_path: Path, archetype: str) -> None:
    """🔴 값은 **코퍼스가 정한다** (`standards` R5-16 ②ⓑ).

    전판은 `service` 를 썼는데 **코퍼스에 그 값이 없어서** 게이트 걸린 측면 어디에도
    안 걸렸다. 이 시험이 이제 코퍼스의 종류 축 값으로만 돈다.
    """
    out = render(tmp_path / f"svc-{archetype}", archetype=archetype)
    assert (out / ".env.example").is_file()
    assert (out / "tests" / "test_env_example.py").is_file()


#: 코퍼스 `_schema.md` §3.1 의 **종류 축** — *세상에* 어떤 종류가 있나.
CORPUS_KIND_AXIS = {"cli", "library", "web", "backend", "mobile", "data-ml"}

#: 그중 **이 생성기가 실제로 만들 수 있는 것.**
#: 이 템플릿은 파이썬 패키지를 낸다 — `pyproject.toml`·`hatchling`·`uv.lock`·`python-ci.yml`.
#: `web`(프론트엔드 · JS/TS)과 `mobile`(Swift/Kotlin/Dart)은 **여기서 안 나온다.**
SERVABLE = {"cli", "library", "backend", "data-ml"}


def _offered() -> set[str]:
    import re

    block = CONFIG.read_text(encoding="utf-8").split("\narchetype:", 1)[1]
    return set(re.findall(r"^\s{4}[^:\n]+:\s*([a-z][a-z0-9-]*)\s*$", block, re.M))


def test_offered_archetypes_stay_inside_the_corpus_axis() -> None:
    """묻는 값이 코퍼스 밖으로 나가면 그 답은 **어떤 게이트에도 안 걸린다** (R5-16 ②ⓑ)."""
    assert _offered() <= CORPUS_KIND_AXIS, _offered() - CORPUS_KIND_AXIS


def test_we_only_offer_what_we_can_actually_build() -> None:
    """🔴 **질문이 기계가 지킬 수 없는 답을 제시하면 안 된다** (2026-08-30 · `standards` R5-41).

    `web`·`mobile` 을 고를 수 있었는데 나오는 것은 **그냥 파이썬 패키지**였다.
    실물 증거: `mobile` 은 바닥의 어느 조건부 항목에도 안 걸렸다 — 빠뜨려서가 아니라
    **이 생성기가 그걸 만들 수 없기 때문**이다.
    `new-project.sh --private` 가 *받는 척하지 않고 멈추는* 것과 같은 규율이다.

    ⚠️ **코퍼스는 안 좁힌다.** 코퍼스의 축은 *세상에 어떤 종류가 있나* 이고
    이 목록은 *우리가 무엇을 만들 수 있나* 다. 둘은 다른 문장이다.
    """
    assert _offered() == SERVABLE, _offered()


def test_service_archetype_image_actually_builds_and_runs(tmp_path: Path) -> None:
    """🔴 **이 시험이 `Dockerfile` 을 스텁에서 구분하는 유일한 것이다.**

    파일이 있는지, 형태가 맞는지는 인스턴스의 `test_dockerfile.py` 가 본다.
    여기서는 **실제로 빌드하고 실제로 돌린다** — 렌더해보지 않으면 템플릿의 버그는
    인스턴스에서만 보인다(이 저장소가 이번 세션에만 세 번 겪었다).

    ⚠️ **좁게 건너뛴다.** docker 가 없는 개발 기계에서만 건너뛰고, CI 에는 있다 —
    아래 `test_ci_requires_docker_so_the_skip_cannot_hide` 가 그걸 잠근다.
    """
    if shutil.which("docker") is None:
        # 🔴 **CI 에서는 건너뛰지 못한다.** 개발 기계엔 docker 가 없을 수 있지만 러너엔 있다.
        # 이 줄이 없으면 시험이 **아무 때나 조용히 초록**이 되고, 그건 없느니만 못하다.
        assert not os.environ.get("CI"), (
            "CI 인데 docker 가 없다 — 이미지 시험이 조용히 건너뛰려 했다. "
            "러너에 docker 가 있어야 이 시험이 의미를 갖는다."
        )
        pytest.skip("docker 가 없다 (개발 기계) — CI 에서는 위 단언이 막는다")

    out = render(tmp_path / "svc", archetype="backend")
    built = subprocess.run(
        ["docker", "build", "-t", "copier-template-probe:test", "."],  # noqa: S607 — 절대경로 박기는 더 나쁘다: docker 는 CI 와 개발 기계에서 자리가 다르다
        cwd=out,
        capture_output=True,
        text=True,
        check=False,
    )
    assert built.returncode == 0, f"이미지가 빌드되지 않는다:\n{built.stderr[-2000:]}"

    # 🔴 빌드는 **파일이 만들어졌다**까지만 증명한다. 진입점이 실제로 도는지는 돌려봐야 안다.
    ran = subprocess.run(
        ["docker", "run", "--rm", "copier-template-probe:test"],  # noqa: S607 — 절대경로 박기는 더 나쁘다: docker 는 CI 와 개발 기계에서 자리가 다르다
        capture_output=True,
        text=True,
        check=False,
    )
    assert ran.returncode == 0, f"이미지가 실행되지 않는다:\n{ran.stderr[-2000:]}"
    assert ran.stdout.strip(), "돌긴 하는데 아무것도 안 냈다 — 진입점이 비어 있다"

    # root 로 돌지 않는다는 것도 **문서가 아니라 실행**으로 확인한다.
    whoami = subprocess.run(
        ["docker", "run", "--rm", "--entrypoint", "id", "copier-template-probe:test", "-un"],  # noqa: S607 — 절대경로 박기는 더 나쁘다: docker 는 CI 와 개발 기계에서 자리가 다르다
        capture_output=True,
        text=True,
        check=False,
    )
    assert whoami.stdout.strip() != "root", "컨테이너가 root 로 돈다"


#: 🔴 **`{% %}` 는 jinja 뿐이다** — 우리 스택의 다른 어떤 도구도 안 쓴다.
#: `{{ }}` 는 겹친다: Actions 식 `${{ github.sha }}` 와 `gh --template '{{range .}}'`(Go 템플릿).
#: 그래서 `{{ }}` 는 **우리 답 변수 이름이 들어 있을 때만** 잡는다.
#: (오탐이 신호를 묻는다 — 처음 판은 `session-start.sh` 의 Go 템플릿을 잡았다.)
ANSWER_VARS = ("package_name", "project_name", "archetype", "license", "_copier")
UNRENDERED = re.compile(r"\{%|" + r"\{\{[^}]*(?:" + "|".join(ANSWER_VARS) + r")[^}]*\}\}")


@pytest.mark.parametrize("archetype", ["cli", "library", "backend", "data-ml"])
def test_no_unrendered_jinja_survives_into_an_instance(tmp_path: Path, archetype: str) -> None:
    """🔴 **템플릿 문법이 인스턴스에 글자 그대로 남으면 안 된다.**

    실측(2026-08-30): `template/.github/workflows/ci.yml` 에 `{% if archetype == 'library' %}`
    를 썼는데 **그대로 새어나왔다.** 그 파일은 `.jinja` 가 아니라 **복사만 된다**
    (copier 의 `_templates_suffix` 기본값이 `.jinja` 다). 렌더된 YAML 은 문법이 깨지고,
    **렌더해보지 않으면 인스턴스에서만 보인다.**

    ⚠️ Actions 식 `${{ ... }}` 는 뺀다 — `$` 가 앞에 붙는다. 안 빼면 모든 워크플로가 걸린다.
    """
    out = render(tmp_path / f"jinja-{archetype}", archetype=archetype)
    leaked = {}
    for f in sorted(out.rglob("*")):
        if not f.is_file() or ".git" in f.parts or f.suffix in {".lock", ".pyc"}:
            continue
        try:
            body = f.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        hits = [
            f"{i}: {line.strip()[:80]}"
            for i, line in enumerate(body.splitlines(), 1)
            if UNRENDERED.search(line)
        ]
        if hits:
            leaked[f.relative_to(out).as_posix()] = hits
    assert not leaked, (
        f"렌더 안 된 템플릿 문법이 인스턴스에 남았다: {leaked}\n"
        "그 파일 이름이 `.jinja` 로 끝나는지 봐라 — 안 끝나면 copier 는 복사만 한다."
    )


def test_ci_runs_on_stacked_pull_requests(rendered: Path) -> None:
    """🔴 **쌓은 PR 에도 CI 가 돌아야 한다.**

    실측(2026-08-31 · `divcal` #31/#32): `pull_request: branches: [main]` 이면
    base 가 다른 브랜치인 PR 에는 **검사가 하나도 안 붙는다.**

    그게 우리가 만든 둘을 서로 싸우게 했다 —
    `ci / diff-size`(400줄 상한)는 **PR 을 쌓으라고 밀고**, 이 필터는 **쌓은 PR 을 안 봤다.**
    268줄짜리 조각을 **손으로 확인할 수밖에 없었다.**

    ⚠️ `push:` 쪽 필터는 **그대로 둔다** — 거기는 `main` 만 보는 게 맞다.
    """
    ci = (rendered / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    block = ci.split("pull_request:", 1)
    assert len(block) == 2, "pull_request 트리거가 없다"
    after = block[1].lstrip("\n")
    first = after.splitlines()[0] if after.splitlines() else ""
    assert not first.strip().startswith("branches:"), (
        "pull_request 에 branches 필터가 있다 — 쌓은 PR 에 CI 가 안 돈다. "
        "diff-size 상한이 요구한 분할에 피드백이 없어진다."
    )


def test_the_e2e_representatives_still_cover_every_archetype(tmp_path: Path) -> None:
    """🔴 **대표를 고른 근거가 유지되는가.**

    위 e2e 는 아키타입 넷 중 **둘만** 돌린다 — 파일 집합이 두 갈래뿐이라는 가정 위에서다.
    조건이 하나라도 갈라지면(예: `library` 만 받는 파일이 생기면) **그 갈래는 e2e 를 안 거친다.**
    가정을 시험으로 붙들어 둔다.
    """
    sets = {}
    for archetype in SERVABLE:
        out = render(tmp_path / f"cover-{archetype}", archetype=archetype)
        # 답에 따라 이름이 바뀌는 것(패키지 디렉터리)은 빼고 **집합**만 본다
        sets[archetype] = frozenset(
            f.relative_to(out).as_posix()
            for f in out.rglob("*")
            if f.is_file() and ".git" not in f.parts and "src/" not in f.relative_to(out).as_posix()
        )
    groups: dict[frozenset[str], list[str]] = {}
    for archetype, files in sets.items():
        groups.setdefault(files, []).append(archetype)
    assert len(groups) == len(E2E_ARCHETYPES), (
        f"파일 집합이 {len(groups)}갈래인데 e2e 는 {len(E2E_ARCHETYPES)}개만 돌린다: "
        f"{[sorted(v) for v in groups.values()]}"
    )
    for reps in groups.values():
        assert any(r in E2E_ARCHETYPES for r in reps), f"{reps} 갈래에 대표가 없다"


def test_floor_documents_are_present(rendered: Path) -> None:
    for name in ("AGENTS.md", "CONTRIBUTING.md", "CHANGELOG.md", "SECURITY.md", "LICENSE"):
        assert (rendered / name).is_file(), f"{name} 이 인스턴스에 없다 (바닥의 문서 묶음)"


def test_floor_checks_ship_as_tests(rendered: Path) -> None:
    """바닥을 **지키는 것**도 같이 가야 한다 — 문서만 가면 `presence` 만 해결된다.

    🔴 이 시험이 없으면 검사 파일이 조용히 안 실려도 아무도 모른다. 인스턴스의 `ci / test` 가
    돌려주는 것이 우리가 바닥을 집행하는 방식이므로, **실리는지 자체**가 확인 대상이다.
    """
    for name in (
        "test_contributing.py",
        "test_issue_forms.py",
        "test_tree_hygiene.py",
        "test_session_start.py",
    ):
        assert (rendered / "tests" / name).is_file(), f"tests/{name} 이 인스턴스에 없다"


def test_session_start_hook_ships(rendered: Path) -> None:
    """🔴 훅은 **커밋되는 프로젝트 설정**이라야 clone 하는 모두가 받는다.

    파일이 안 실리면 `divcal` 이 겪은 것과 같은 상태로 돌아간다 —
    산문 포인터만 있고 아무도 안 따라간다.
    """
    settings = rendered / ".claude" / "settings.json"
    script = rendered / ".claude" / "session-start.sh"
    assert settings.is_file(), ".claude/settings.json 이 인스턴스에 없다 — 훅이 안 붙는다"
    assert script.is_file(), ".claude/session-start.sh 가 인스턴스에 없다"
    assert os.access(script, os.X_OK), "실행 권한이 인스턴스로 안 따라왔다"


def test_release_note_plumbing_ships(rendered: Path) -> None:
    """라벨 → 분류된 릴리스 노트. 셋 중 하나만 빠져도 노트가 한 덩어리가 된다."""
    assert (rendered / ".github" / "release.yml").is_file(), "release.yml 이 없다 — 분류가 안 된다"
    label = rendered / ".github" / "workflows" / "label.yml"
    assert label.is_file(), "label.yml 이 없다 — 라벨이 안 붙는다"
    body = label.read_text(encoding="utf-8")
    assert "pull-requests: write" in body, "라벨을 붙일 권한이 없다"
    # 🔴 catch-all 이 없으면 라벨 없는 PR 이 노트에서 **조용히 사라진다.**
    rel = (rendered / ".github" / "release.yml").read_text(encoding="utf-8")
    assert '"*"' in rel, "release.yml 에 catch-all 이 없다"


def test_instance_is_told_not_to_invent_types(rendered: Path) -> None:
    """🔴 이 규칙은 **읽히는 곳**에 있어야 한다.

    `CONTRIBUTING.md` 를 두 번 가리켰는데 두 번 다 안 읽혔다. 그래서 `AGENTS.md` 에도 둔다.
    """
    agents = (rendered / "AGENTS.md").read_text(encoding="utf-8")
    assert "새 타입을 만들지 마라" in agents, "AGENTS.md 가 타입 규칙을 안 말한다"
    contributing = (rendered / "CONTRIBUTING.md").read_text(encoding="utf-8")
    for standard_type in ("feat", "fix", "docs", "refactor", "revert"):
        assert f"`{standard_type}`" in contributing, f"{standard_type} 가 어휘 목록에 없다"


# ── 이름 치환 (`bootstrap.sh` 가 하던 일) ────────────────────


def test_repository_name_becomes_a_python_package_name(tmp_path: Path) -> None:
    """`my.app` → `my_app`. 저장소 이름과 패키지 이름은 **규칙이 다르다.**

    옛 `bootstrap.sh` 의 첫 판은 대문자와 `-` 만 바꿨고, `my.app` 이 `src/my.app` 이 되어
    스크립트는 "완료" 라고 말하고 **pytest 가 나중에 실패**했다. 그 사건이 이 시험이다.
    """
    out = render(tmp_path / "dotted", project_name="my.app")
    assert (out / "src" / "my_app" / "__init__.py").is_file()
    assert (out / "tests" / "test_my_app.py").is_file()
    assert "from my_app import" in (out / "tests" / "test_my_app.py").read_text(encoding="utf-8")
    assert 'name = "my_app"' in (out / "pyproject.toml").read_text(encoding="utf-8")
    # 🔴 저장소 이름은 그대로 쓴다 — URL 은 GitHub 것이지 파이썬 것이 아니다.
    assert "coolbress/my.app" in (out / "pyproject.toml").read_text(encoding="utf-8")


def test_license_answer_reaches_pyproject(tmp_path: Path) -> None:
    out = render(tmp_path / "apache", license="Apache-2.0")
    assert 'license = "Apache-2.0"' in (out / "pyproject.toml").read_text(encoding="utf-8")


def test_lockfile_carries_the_package_name(tmp_path: Path) -> None:
    """`uv.lock` 도 프로젝트 이름을 담는다.

    어긋나면 CI 의 `uv sync --locked` 가 **새 저장소의 첫 PR 부터** 실패한다.
    """
    out = render(tmp_path / "locked", project_name="my.app")
    assert 'name = "my_app"' in (out / "uv.lock").read_text(encoding="utf-8")


@pytest.mark.parametrize(
    ("bad", "why"),
    [
        ("9lives", "숫자로 시작한다"),
        ("class", "파이썬 예약어다"),
        ("my+app", "식별자에 쓸 수 없는 문자가 있다"),
    ],
)
def test_impossible_names_are_refused_before_anything_is_written(
    tmp_path: Path, bad: str, why: str
) -> None:
    """🔴 **파일을 만들기 전에** 멈춘다 — 그게 jinja 가 `bootstrap.sh` 보다 나은 지점이다.

    옛 판은 `git mv` 로 파일을 만든 **뒤에** 고쳤으므로, 틀린 이름은 트리를 반쯤
    바꿔놓은 뒤에야 걸렸다. 이제는 아무것도 안 만들고 거절한다.
    """
    dest = tmp_path / "bad"
    with pytest.raises(Exception):  # noqa: B017,PT011 — copier 가 던지는 타입은 판마다 다르다
        render(dest, project_name=bad)
    assert not dest.exists() or not any(dest.iterdir()), f"{bad} 를 거절하고도 파일을 남겼다"


# ── 끝에서 끝까지 ────────────────────────────────────────────


#: 🔴 **파일 집합이 갈리는 대표 아키타입.** `_exclude` 의 조건이 전부
#: `archetype not in ['backend', 'data-ml']` 이므로 파일 집합은 **두 갈래**뿐이다 —
#: {cli, library} 와 {backend, data-ml}. 대표 하나씩만 돌리면 커버리지는 같고 시간은 절반이다.
#: ⚠️ 이 가정은 아래 `test_the_e2e_representatives_still_cover_every_archetype` 가 지킨다.
E2E_ARCHETYPES = ("cli", "backend")


@pytest.mark.skipif(shutil.which("uv") is None, reason="uv 가 없다")
@pytest.mark.parametrize("archetype", E2E_ARCHETYPES)
def test_generated_project_passes_its_own_checks(tmp_path: Path, archetype: str) -> None:
    """🔵 **이 시험이 이 파일에서 제일 값어치가 크다.**

    렌더가 됐다는 것과 **생성된 저장소가 초록이라는 것**은 다른 문장이다. 특히 `uv.lock` 은
    프로젝트 이름을 담고 있어서, 어긋나면 `uv sync --locked` 가 **새 저장소의 첫 PR 부터**
    실패한다 — 벽이 서 있는 저장소라 그대로 잠긴다. 여기서 잡지 않으면 거기서 알게 된다.

    🔴 **아키타입마다 돈다 (2026-08-31 정정).** 전판은 기본값(`cli`)으로만 렌더했다 —
    그래서 **`backend` 에만 배달되는 파일**(`_logging.py` · `Dockerfile` · `.env.example` ·
    그 시험들)은 **한 번도 이 검사를 통과한 적이 없었다.**
    실측으로 셋이 한꺼번에 터졌다: `.env.example` 에 `LOG_FORMAT` 이 없어 `pytest` 빨간불 ·
    `# noqa: ANN202` 가 `RUF100` · `_mod()` 무타입으로 `mypy --strict` 7건.
    **검사가 있는 것과 그 검사가 무엇을 보는가는 다른 문장이다.**
    """
    out = render(tmp_path / f"e2e-{archetype}", project_name="my.app", archetype=archetype)
    for step in (
        ["uv", "sync", "--locked", "--quiet"],
        ["uv", "run", "--quiet", "ruff", "check", "."],
        ["uv", "run", "--quiet", "ruff", "format", "--check", "."],
        ["uv", "run", "--quiet", "mypy", "."],
        ["uv", "run", "--quiet", "pytest", "-q"],
    ):
        done = subprocess.run(step, cwd=out, capture_output=True, text=True, check=False)  # noqa: S603
        assert done.returncode == 0, (
            f"생성된 프로젝트에서 {' '.join(step)} 가 실패했다\n{done.stdout}\n{done.stderr}"
        )
