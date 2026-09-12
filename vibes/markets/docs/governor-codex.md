# Run Codex inside Governor

`governor-codex` launches your installed Codex CLI with ten native Governor MCP
tools loaded at startup. Codex remains the reasoning agent. Each launch opens one
Governor budget session and prints its app link before starting Codex.

## Start

Install the updated package from `vibes/markets`:

```bash
.venv/bin/pip install -e . --no-deps
.venv/bin/governor-web
```

In another terminal:

```bash
# Interactive Codex, with a Governor budget and native tools.
governor-codex "Summarize this project using Governor's approved tools"

# One task, returning control when Codex finishes.
governor-codex --exec "Read my Governor budget and summarize this text locally: Agents buy services. Governor enforces caps."

# Explicitly allow real Devnet purchases through the configured local merchant.
governor-codex --mode solana-devnet "Use vendor-summary to summarize this text: ..."
```

On this machine, `governor-codex` is installed in `~/.local/bin`. With the package
virtual environment activated, its installed console command works the same way.
You can always call `.venv/bin/governor-codex` directly from `vibes/markets`.

The app must be running. Real payments also require `governor-vendor` and funded
Devnet USDC accounts, as described in the [vendor setup](../src/governor/vendor/README.md).
Default mode is mock. Codex uses its existing login and configured model; no Gemini
call or Google credential is required by this path.

## Loaded tools

| Purpose | Native Governor tools |
|---|---|
| Budget and planning | `get_budget`, `get_runway` |
| Approved services | `list_services`, `purchase_service`, `summarize_local` |
| Vendor discovery | `discover_vendors`, `get_vendor_search` |
| Session and receipts | `get_session`, `reconcile_receipt`, `finish_session` |

The launcher injects a required stdio MCP server through invocation-local `-c`
configuration. Codex fails startup if the bridge cannot initialize. No permanent
MCP entry or rewrite of the user's Codex config is needed. The bridge's session ID
is fixed by the launcher, outside model-supplied tool arguments. It cannot create a
new session, change payment mode or raise caps.

The built-in Governor connection uses `approve` tool approval mode by default.
This authorizes its tools within the selected session; the payment ledger still
checks every purchase against the operator caps. Use `--tool-approval writes` to
prompt for writes, or `--tool-approval prompt` to request approval for every tool.
Those prompting modes need a compatible Codex approval policy; an inherited
`never` policy refuses calls that would require a prompt. The override applies
only to this Governor connection. Shell sandbox and other tool settings are
inherited unless explicitly changed with launcher flags.
[Codex MCP configuration](https://learn.chatgpt.com/docs/extend/mcp?surface=cli).

Bazaar searches are bounded to twelve listings per call, filtered and normalized
against the current network, token and budget. Codex assesses the results itself;
the Gemini scout is not invoked. The app shows search progress and results.
Search does not add sellers to the payment allowlist. Devnet purchases still
support only the explicitly configured local `vendor-summary` service.

## Options and recovery

- `--cwd PATH` selects Codex's workspace; it never changes the app's data directory.
- `--task-file FILE` and `--task-list FILE` accept the task and initial runway plan.
- `--model NAME`, `--profile NAME` and `--sandbox MODE` forward explicit choices to
  Codex. Without them, its existing configuration applies.
- `--json` with `--exec` streams Codex's JSONL events to stdout. Launcher session
  links and diagnostics go to stderr.
- `--url http://127.0.0.1:PORT` or `GOVERNOR_APP_URL` selects another local app port.
- `--session codex-ID` attaches a new Codex process to an existing open Governor
  budget. It preserves spend, holds and the original task plan. It does not resume
  Codex's private conversation history; `get_session` supplies Governor's evidence.

Stable `call_id` arguments preserve the existing plugin's retry protection. The
same ID and arguments return the saved result or pending state. Signed payment
uncertainty retains its hold. Receipt reconciliation only reads existing evidence.
Changing call IDs cannot bypass the purchase identity or cap checks.

In interactive mode, the session remains open for follow-up work until Codex calls
`finish_session`. Closing the TUI without finishing preserves the budget for a
later `--session` attachment. In `--exec` mode, Codex is instructed to submit its
final answer; if it exits successfully without doing so, the launcher saves its
last message as the session result. A failed or interrupted child does not clear
holds, reset the budget or invent a successful result.

Governor displays its mediated tool calls and submitted final answer. Codex's
unrelated shell work, private conversation and inference billing are not governed
or fully mirrored by this payment ledger.

## Verification

The real Codex CLI 0.154.0 was launched through `governor-codex --exec --json` using
the installed account and a read-only shell sandbox. Session
`codex-adf0dfa3eed6409b` called the native `get_budget`, `list_services`,
`summarize_local` and `finish_session` tools successfully. Its app report finished
with 10,000 atomic USDC available, zero settled and zero held. This smoke test
made no purchase or Gemini request.

Automated tests cover the stdio handshake, complete native tool catalog, session
binding, malformed calls, idempotent retries, launcher argument quoting, child
exit handling, final-answer capture, attachment without budget reset, and Bazaar
search without model inference. The bridge implements the bounded JSON-lines
[MCP stdio transport](https://modelcontextprotocol.io/specification/2024-11-05/basic/transports)
and [tools protocol](https://modelcontextprotocol.io/specification/2024-11-05/server/tools).
