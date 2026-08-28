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


def test_service_archetype_includes_them(tmp_path: Path) -> None:
    out = render(tmp_path / "svc", archetype="service")
    assert (out / ".env.example").is_file()
    assert (out / "tests" / "test_env_example.py").is_file()


def test_floor_documents_are_present(rendered: Path) -> None:
    for name in ("AGENTS.md", "CONTRIBUTING.md", "CHANGELOG.md", "SECURITY.md", "LICENSE"):
        assert (rendered / name).is_file(), f"{name} 이 인스턴스에 없다 (바닥의 문서 묶음)"
