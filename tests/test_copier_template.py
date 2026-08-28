"""`copier.yml` 이 **실제로 동작하는 설정인지** 검사한다.

이 시험은 추측이 아니라 **이 세션에서 실제로 두 번 틀린 것**에서 나왔다:

1. **`{{ _copier_conf.answers_file }}.jinja` 을 안 만들었다** → 인스턴스에 `.copier-answers.yml`
   이 안 생겼고, 그러면 **`copier update` 가 아예 안 된다.** copier 를 쓰는 이유가 통째로 사라진다.
2. **`_preserve_symlinks` 를 안 켰다** → `CLAUDE.md` 가 심볼릭 링크에서 **사본**이 됐다.
   링크로 둔 이유가 *"사본을 두면 갈라진다"* 인데 정확히 그걸 되돌렸다.

둘 다 **렌더는 성공하고 조용히 망가지는** 형태다. 그래서 검사로 둔다.

⚠️ 렌더 자체는 여기서 안 돌린다(copier + 네트워크). **설정이 맞는지만** 본다.
`copier.yml` 은 인스턴스로 안 가므로 인스턴스에서는 건너뛴다.
"""

from __future__ import annotations

from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "copier.yml"
ANSWERS_TEMPLATE = ROOT / "{{ _copier_conf.answers_file }}.jinja"

pytestmark = pytest.mark.skipif(
    not CONFIG.exists(), reason="copier.yml 은 인스턴스로 안 간다"
)


def _config() -> str:
    return CONFIG.read_text(encoding="utf-8")


def test_answers_file_template_exists() -> None:
    """없으면 인스턴스가 `.copier-answers.yml` 을 못 받고 `copier update` 가 죽는다."""
    assert ANSWERS_TEMPLATE.is_file(), (
        "`{{ _copier_conf.answers_file }}.jinja` 이 없다. "
        "이게 없으면 인스턴스가 어느 판에서 태어났는지 기억하지 못해 update 가 불가능하다."
    )
    body = ANSWERS_TEMPLATE.read_text(encoding="utf-8")
    assert "_copier_answers" in body, "답을 실제로 써넣지 않는다"


def test_symlinks_are_preserved() -> None:
    """`CLAUDE.md` → `AGENTS.md` 링크가 사본이 되면 둘이 갈린다."""
    assert "_preserve_symlinks: true" in _config(), (
        "_preserve_symlinks 가 꺼져 있다. CLAUDE.md 심볼릭 링크가 사본이 된다."
    )


def test_archetype_question_exists_with_the_narrow_default() -> None:
    cfg = _config()
    assert "archetype:" in cfg, "아키타입 질문이 없다 — 조건부 항목에 입력이 없어진다"
    assert "default: cli" in cfg, (
        "기본값이 가장 좁은 것이 아니다. 넓히는 것은 파일을 더하는 일이고 "
        "좁히는 것은 안 쓰는 파일을 지우는 일이라 스텁으로 남는다."
    )


def test_service_only_files_are_conditional() -> None:
    """`.env.example` 은 service 맥락이다 (12-Factor · 바닥의 처분)."""
    cfg = _config()
    for path in (".env.example", "tests/test_env_example.py"):
        assert path in cfg, f"{path} 에 아키타입 조건이 안 걸려 있다"
    assert "archetype not in" in cfg, "조건이 jinja 로 안 쓰여 있다"


def test_template_does_not_ship_itself() -> None:
    assert "copier.yml" in _config(), "copier.yml 이 인스턴스로 복사된다"
