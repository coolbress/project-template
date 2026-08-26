#!/usr/bin/env bash
# 템플릿 자리표시자를 실제 프로젝트 이름으로 바꾼다. 한 번만 돌린다.
#   사용법: ./bootstrap.sh <프로젝트-이름>
#
# 왜 템플릿 안에 있나: 파일 배치를 아는 것은 템플릿 자신이다.
# new-project.sh 는 "저장소 생성 + 서버 바닥" 이 책임이라 여기까지 알 필요가 없다.
# (감사 §6.4 — "이름 치환과 선택지가 몇 개뿐이면 작은 bootstrap adapter 로 끝낸다")
set -euo pipefail

name="${1:?사용법: ./bootstrap.sh <프로젝트-이름>}"
pkg="$(printf '%s' "$name" | tr '[:upper:]-' '[:lower:]_')"   # 패키지는 소문자·언더스코어
[ -d src/app ] || { echo "이미 bootstrap 된 것 같다 (src/app 이 없다)" >&2; exit 1; }

git mv src/app "src/$pkg"
git mv tests/test_app.py "tests/test_$pkg.py"
python3 - "$pkg" "$name" <<'PY'
import pathlib, sys
pkg, name = sys.argv[1], sys.argv[2]
for path, old, new in (
    ("pyproject.toml", 'name = "app"', f'name = "{pkg}"'),
    ("README.md", "# app", f"# {name}"),
    (f"tests/test_{pkg}.py", "from app import", f"from {pkg} import"),
):
    p = pathlib.Path(path); t = p.read_text()
    assert old in t, f"{path}: '{old}' 를 찾지 못했다"
    p.write_text(t.replace(old, new, 1))
PY
git add -A

echo "완료 — 패키지 이름은 $pkg 다."
echo "남은 것: pyproject.toml 의 description 이 아직 자리표시자다. 실제 설명으로 바꿔라."
echo "그리고 이 파일(bootstrap.sh)은 한 번만 쓰는 것이니 지워도 된다."
