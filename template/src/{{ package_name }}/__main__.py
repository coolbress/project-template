"""컨테이너의 진입점.

🔴 **프레임워크를 고르지 않았다.** 서비스를 무엇으로 띄울지는 이 프로젝트가 정한다 —
여기서 `uvicorn` 이나 `flask` 를 박으면 안 쓰는 프로젝트에 **스텁**이 남는다.

`python -m <패키지>` 로 돌고, `Dockerfile` 의 `CMD` 가 이것을 부른다.
서버를 붙일 땐 아래 `main()` 안을 바꾼다.
"""

from __future__ import annotations

from . import greet


def main() -> None:
    print(greet("world"))


if __name__ == "__main__":
    main()
