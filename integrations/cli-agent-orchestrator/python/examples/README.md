# CAO AG-UI example server (keyless)

A four-feature AG-UI Dojo server backed by CAO's merged run plane over a
deterministic `mock_cli` fleet. **No API keys, no tmux, no browser.**

| Feature | Route | What it shows |
|---|---|---|
| `agentic_chat` | `/agentic-chat` | Baseline run: `RUN_STARTED → STATE_SNAPSHOT → STEP_* → RUN_FINISHED(success)` |
| `shared_state` | `/shared-state` | Fleet `STATE_SNAPSHOT` + RFC-6902 `STATE_DELTA` (read path) |
| `human_in_the_loop` | `/human-in-the-loop` | Allow-listed `approval_card` generative-UI affordance |
| `interrupt` **(flagship)** | `/interrupt` | Real permission prompt → `RUN_FINISHED outcome={type:"interrupt"}` → `resume[]` |

## Run

```sh
uv sync
uv run dev            # serves on http://localhost:8024 (PORT overrides)
curl -s localhost:8024/health
```

Each feature is a stock AG-UI endpoint (`POST /<feature>/`) emitting official
`ag-ui-protocol` `EventEncoder` frames — drive it with `@ag-ui/client` or
`@ag-ui/cli-agent-orchestrator`.

### The flagship interrupt round-trip

```sh
# 1) Start a run — closes with an interrupt outcome carrying an interrupt id.
curl -sN localhost:8024/interrupt/ -H 'content-type: application/json' \
  -d '{"threadId":"t","runId":"r","state":{},"messages":[],"tools":[],"context":[],"forwardedProps":{}}'

# 2) Approve it (or deny with {"interruptId": ID, "status":"cancelled"}).
curl -sN localhost:8024/interrupt/ -H 'content-type: application/json' \
  -d '{"threadId":"t","runId":"r2","state":{},"messages":[],"tools":[],"context":[],"forwardedProps":{},
       "resume":[{"interruptId":"<ID>","status":"resolved","payload":{"approved":true}}]}'
```

## Contract tests (keyless, fail-closed)

```sh
uv run --extra test pytest        # asserts the wire contract of all four features
```

`tests/test_server.py` asserts the frame sequence each feature produces —
including the interrupt approve/deny resume and the metadata-only privacy
boundary — independent of any LLM or the Dojo frontend. These are the
secret-free assertions the CI matrix runs.
