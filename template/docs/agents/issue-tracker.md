# Issue tracker: GitHub

이 저장소의 이슈·스펙·티켓은 **GitHub Issues** 에 산다. 전부 `gh` CLI 로 읽고 쓴다.
(`mattpocock-skills` 의 `setup-matt-pocock-skills` 가 쓰는 파일이다 — 템플릿이 미리 채웠으므로
그 스킬을 돌릴 필요가 없다. 트래커를 바꾸고 싶을 때만 돌린다. 원본: mattpocock/skills, MIT.)

## Conventions

- **Create an issue**: `gh issue create --title "..." --body "..."`. 여러 줄 본문은 heredoc.
- **Read an issue**: `gh issue view <number> --comments`
- **List issues**: `gh issue list --state open --json number,title,body,labels,comments --jq '[.[] | {number, title, body, labels: [.labels[].name], comments: [.comments[].body]}]'` (`--label` · `--state` 로 거른다)
- **Comment**: `gh issue comment <number> --body "..."`
- **Labels**: `gh issue edit <number> --add-label "..."` / `--remove-label "..."`
- **Close**: `gh issue close <number> --comment "..."`

저장소는 `git remote -v` 에서 안다 — 클론 안에서 돌리면 `gh` 가 알아서 한다.

## Pull requests as a triage surface

**PRs as a request surface: no.** _(외부 PR 을 기능 요청으로 다루려면 `yes` 로 바꾼다 — `/triage` 가 이 줄을 읽는다.)_

## When a skill says "publish to the issue tracker"

GitHub 이슈를 만든다. 인수기준은 `AC-n → 검사` 규칙을 따른다(`AGENTS.md`).

## When a skill says "fetch the relevant ticket"

`gh issue view <number> --comments`

## Wayfinding operations

`/wayfinder` 가 쓴다. **map** 은 이슈 하나, 티켓은 그 **child** 이슈다.

- **Map**: `wayfinder:map` 라벨이 붙은 이슈 하나. `gh issue create --label wayfinder:map`
- **Child ticket**: map 의 sub-issue (`gh api` 의 sub-issues 엔드포인트). sub-issue 가 안 되면 map 본문의 task list 에 넣고 child 본문 첫 줄에 `Part of #<map>`. 라벨: `wayfinder:<type>` (`research` / `prototype` / `grilling` / `task`). 잡으면 담당자를 건다.
- **Blocking**: GitHub **native issue dependencies**. `gh api --method POST repos/<owner>/<repo>/issues/<child>/dependencies/blocked_by -F issue_id=<blocker-db-id>` — `<blocker-db-id>` 는 숫자 **database id** (`gh api repos/<owner>/<repo>/issues/<n> --jq .id`), `#번호`·`node_id` 가 아니다. 안 되면 child 본문 첫 줄에 `Blocked by: #<n>, #<n>`. 막는 것이 전부 닫히면 unblocked.
- **Frontier query**: map 의 열린 children 중 열린 blocker 가 없고 담당자가 없는 것. map 순서에서 첫 것.
- **Claim**: `gh issue edit <n> --add-assignee @me` — 세션의 첫 쓰기.
- **Resolve**: `gh issue comment <n> --body "<answer>"` → `gh issue close <n>` → map 의 Decisions-so-far 에 한 줄(gist + link).
