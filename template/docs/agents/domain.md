# Domain docs

엔지니어링 스킬이 코드베이스를 살피기 **전에** 읽는 도메인 문서. (`mattpocock-skills` 의 seed, MIT.)

## Before exploring, read these

- 루트의 **`CONTEXT.md`** — 용어집. 구현 세부는 안 들어간다.
- **`docs/adr/`** — 손대는 영역의 ADR.

없으면 **조용히 넘어간다.** 없다고 말하지도, 미리 만들라고 하지도 않는다.
`/domain-modeling`(`/grill-with-docs` 가 안에서 부른다)이 용어나 결정이 실제로 정해질 때 **그때** 만든다.

## File structure

single-context (이 저장소):

```
/
├── CONTEXT.md
├── docs/adr/
│   ├── 0001-….md
│   └── 0002-….md
└── src/
```

ADR 은 셋이 다 참일 때만: **되돌리기 어렵다** · **맥락 없이는 놀랍다** · **진짜 트레이드오프의 결과다.**
