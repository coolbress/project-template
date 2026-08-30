"""로그가 **기계가 읽을 수 있는 모양**으로 나오는가.

`presence ≠ adequacy` — 로깅 설정 파일이 있다는 것과 수집기가 파싱할 수 있다는 것은 다르다.
사람이 읽는 한 줄로 찍으면 **배포한 뒤에야** 안다.

🔴 세 기둥 중 이것만 검사한다. 메트릭·트레이스·SLO 는 **트리에 안 산다** —
코퍼스 측면 19 의 claim 이 *"out-of-repo posture"* 라고 못박는다.
"""

from __future__ import annotations

import json
import logging
import tomllib
from io import StringIO
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent


def _pkg() -> str:
    data = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    name: str = data["project"]["name"]
    return name.replace("-", "_")


@pytest.fixture
def emitted() -> list[str]:
    """루트 로거를 잡아 실제로 찍힌 줄을 모은다."""
    mod = __import__(f"{_pkg()}._logging", fromlist=["configure", "JsonFormatter"])
    buf = StringIO()
    handler = logging.StreamHandler(buf)
    handler.setFormatter(mod.JsonFormatter())
    log = logging.getLogger("probe")
    log.handlers.clear()
    log.addHandler(handler)
    log.setLevel(logging.INFO)
    log.propagate = False
    log.info("hello", extra={"order_id": 7})
    try:
        raise ValueError("boom")
    except ValueError:
        log.exception("failed")
    return [ln for ln in buf.getvalue().splitlines() if ln]


def test_every_line_is_one_json_object(emitted: list[str]) -> None:
    for line in emitted:
        json.loads(line)  # 못 파싱하면 여기서 터진다


def test_the_fields_a_collector_needs_are_there(emitted: list[str]) -> None:
    first = json.loads(emitted[0])
    for key in ("time", "level", "logger", "message"):
        assert key in first, f"{key} 가 없다 — 수집기가 이 줄을 분류하지 못한다"
    assert first["message"] == "hello"


def test_extra_context_survives(emitted: list[str]) -> None:
    """🔴 이게 없으면 구조화의 값이 절반이다 — 문맥이 message 문자열에 녹아버린다."""
    assert json.loads(emitted[0]).get("order_id") == 7


def test_exceptions_carry_their_traceback(emitted: list[str]) -> None:
    last = json.loads(emitted[-1])
    assert "exception" in last, "예외가 로그에 안 실린다 — 사후에 원인을 못 찾는다"
    assert "ValueError" in last["exception"]


def test_configure_is_idempotent() -> None:
    """훅·프레임워크가 두 번 부를 수 있다. 핸들러가 쌓이면 줄이 중복된다."""
    mod = __import__(f"{_pkg()}._logging", fromlist=["configure"])
    mod.configure()
    n = len(logging.getLogger().handlers)
    mod.configure()
    assert len(logging.getLogger().handlers) == n
