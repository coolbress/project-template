"""구조화 로깅 — 서비스 아키타입의 **트리에 사는** 관측성.

🔴 **세 기둥 중 이것만 저장소에 산다.** 코퍼스 측면 19 의 claim 이 직접 말한다 —
*"instrument services for the three pillars (structured logs, RED/USE metrics, distributed
traces) … and **treat live monitoring/SLO targets as out-of-repo posture**"*.
메트릭·트레이스·SLO·대시보드는 Datadog/Grafana/PagerDuty 에 있지 트리에 없다
(실측: observability-as-code **~17%**). 그것들을 여기 넣으면 **스텁**이 된다.

로그는 다르다. **어떤 모양으로 찍을지는 코드가 정한다.** 사람이 읽는 한 줄로 찍으면
수집기가 못 파싱하고, 그건 배포한 뒤에야 안다.

⚠️ **의존성을 안 늘린다** — 표준 라이브러리만 쓴다. `structlog`·`loguru` 를 박으면
그걸 안 쓰는 프로젝트에 짐이 된다.
"""

from __future__ import annotations

import json
import logging
import sys
from typing import Any


class JsonFormatter(logging.Formatter):
    """한 줄에 하나의 JSON 객체. 컨테이너 표준 출력이 그대로 수집된다."""

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "time": self.formatTime(record, "%Y-%m-%dT%H:%M:%S%z"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        # 🔴 `logger.info("...", extra={"order_id": 7})` 로 넘긴 것을 살린다.
        # 이게 없으면 구조화의 값이 절반이다 — 문맥이 message 문자열에 녹아버린다.
        reserved = set(logging.LogRecord("", 0, "", 0, "", None, None).__dict__) | {"message", "asctime"}
        payload.update({k: v for k, v in record.__dict__.items() if k not in reserved})
        return json.dumps(payload, ensure_ascii=False, default=str)


def configure(level: int = logging.INFO) -> None:
    """루트 로거를 JSON·stdout 으로 맞춘다. 여러 번 불러도 핸들러가 안 쌓인다."""
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())
    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(level)
