"""이 템플릿을 실제로 렌더해서 결과를 돌려준다.

왜 하네스가 따로 있나: `copier.yml` 을 **읽어서** 맞는지 보는 것과
**렌더해서** 되는지 보는 것은 다른 문장이다. 2026-08-28 까지 이 저장소의
시험은 앞엣것만 했고, 그래서 `.copier-answers.yml` 이 안 생기는 것과
심볼릭 링크가 사본이 되는 것을 **둘 다 놓쳤다**(둘 다 렌더는 성공했다).
"""

from __future__ import annotations

import warnings
from pathlib import Path
from typing import Any

#  src/template_render/__init__.py → src/template_render → src → 저장소 루트
TEMPLATE_ROOT = Path(__file__).resolve().parents[2]

DEFAULT_ANSWERS: dict[str, Any] = {
    "project_name": "probe",
    "license": "MIT",
    "archetype": "cli",
}


def render(dest: Path, **answers: Any) -> Path:
    """`dest` 에 템플릿을 렌더하고 그 경로를 돌려준다.

    ⚠️ `vcs_ref="HEAD"` 다. 로컬 경로라도 copier 는 git 저장소면 **태그를 고른다** —
    그대로 두면 이 저장소를 시험하면서 **v1.0.0 을 시험하게** 된다.
    """
    import copier
    from copier.errors import DirtyLocalWarning

    data = dict(DEFAULT_ANSWERS)
    data.update(answers)
    # 🔴 `filterwarnings = ["error"]` 아래에서 이 경고 하나만 좁게 통과시킨다.
    # copier 는 작업 트리가 더러우면 `DirtyLocalWarning` 을 내며 **커밋 안 된 변경을
    # 포함해서** 렌더한다. 여기서는 그게 정확히 원하는 동작이다 — 지금 고치고 있는
    # 템플릿을 시험하는 것이지 마지막 커밋을 시험하는 게 아니다.
    # CI 는 체크아웃이 깨끗해서 이 경고가 안 난다. 로컬에서만 난다.
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DirtyLocalWarning)
        copier.run_copy(
            str(TEMPLATE_ROOT),
            str(dest),
            data=data,
            defaults=True,
            quiet=True,
            unsafe=False,
            vcs_ref="HEAD",
        )
    return dest
