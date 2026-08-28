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


@pytest.mark.parametrize("archetype", ["web", "backend", "data-ml"])
def test_service_archetypes_include_them(tmp_path: Path, archetype: str) -> None:
    """🔴 값은 **코퍼스가 정한다** (`standards` R5-16 ②ⓑ).

    전판은 `service` 를 썼는데 **코퍼스에 그 값이 없어서** 게이트 걸린 측면 어디에도
    안 걸렸다. 이 시험이 이제 코퍼스의 종류 축 값으로만 돈다.
    """
    out = render(tmp_path / f"svc-{archetype}", archetype=archetype)
    assert (out / ".env.example").is_file()
    assert (out / "tests" / "test_env_example.py").is_file()


def test_archetype_choices_are_the_corpus_kind_axis() -> None:
    """묻는 값이 코퍼스 밖으로 나가면 그 답은 **어떤 게이트에도 안 걸린다.**"""
    import re

    body = CONFIG.read_text(encoding="utf-8")
    block = body.split("\narchetype:", 1)[1]
    offered = set(re.findall(r"^\s{4}[^:\n]+:\s*([a-z][a-z0-9-]*)\s*$", block, re.M))
    assert offered == {"cli", "library", "web", "backend", "mobile", "data-ml"}, offered


def test_floor_documents_are_present(rendered: Path) -> None:
    for name in ("AGENTS.md", "CONTRIBUTING.md", "CHANGELOG.md", "SECURITY.md", "LICENSE"):
        assert (rendered / name).is_file(), f"{name} 이 인스턴스에 없다 (바닥의 문서 묶음)"


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


@pytest.mark.skipif(shutil.which("uv") is None, reason="uv 가 없다")
def test_generated_project_passes_its_own_checks(tmp_path: Path) -> None:
    """🔵 **이 시험이 이 파일에서 제일 값어치가 크다.**

    렌더가 됐다는 것과 **생성된 저장소가 초록이라는 것**은 다른 문장이다. 특히 `uv.lock` 은
    프로젝트 이름을 담고 있어서, 어긋나면 `uv sync --locked` 가 **새 저장소의 첫 PR 부터**
    실패한다 — 벽이 서 있는 저장소라 그대로 잠긴다. 여기서 잡지 않으면 거기서 알게 된다.
    """
    out = render(tmp_path / "e2e", project_name="my.app")
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
