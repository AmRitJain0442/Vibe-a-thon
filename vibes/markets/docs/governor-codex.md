# Run Codex inside Governor

`governor-codex` opens an orange-and-black interactive terminal with a prompt,
streaming Codex replies, expandable tool calls and live service-budget totals.
Codex runs inside it through its persistent app-server with ten native Governor
MCP tools. Codex remains the reasoning agent. The first prompt creates one
Governor budget session; follow-up prompts reuse that budget and conversation.

## Start

Install the updated package from `vibes/markets`:

```bash
.venv/bin/pip install -r requirements.lock
.venv/bin/pip install -e . --no-deps
.venv/bin/governor-web
```

In another terminal:

```bash
# Open the interactive terminal and type a prompt.
governor-codex

# Or start with a prompt already supplied.
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

## Terminal controls

- **Enter** sends your prompt; **Up/Down** recalls earlier prompts.
- Replies stream as Codex writes. Expand a tool row to inspect its arguments,
  command output, result or error. The budget refreshes every 1.5 seconds.
- **Esc** or `/stop` interrupts the current Codex turn. Existing payment holds stay.
- **Ctrl+O** or `/app` opens the same session in the web app.
- `/budget` shows ledger totals; `/help` lists commands.
- `/finish` saves the latest answer and closes the budget session. An interrupted
  turn is saved as `STOPPED`, rather than reported as a successful completion.
- **Ctrl+Q** or `/quit` exits, leaving the session open for later work.

Codex command and file-change approvals appear as explicit **Allow once / Deny**
prompts. User-input questions appear as forms. Unsupported app-server requests
are refused with an explanation; `--native` uses Codex's own UI for those workflows.
The terminal inherits your Codex login, model, sandbox and approval policy.
It respects `NO_COLOR` when set in your environment.

The app shows prompts and assistant messages when each message completes,
including intermediate commentary. Token deltas and command output stream inside
the terminal. Shell commands and Codex inference charges are outside Governor's
service-payment ledger. The service-budget panel labels that distinction.

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
- `--session codex-ID` reopens an existing open Governor budget, preserving spend,
  holds and its original task plan. In the default terminal, it also resumes the
  saved Codex thread on this machine and restores mirrored messages from the app.
  Use the same app URL and `--cwd`. The thread mapping lives in Governor's local
  user-state directory, with owner-only file permissions.
- `--native` launches Codex's original terminal UI with Governor tools loaded.
  This fallback and `--exec` attach to the Governor budget without resuming the
  custom terminal's conversation; `get_session` supplies prior ledger evidence.

Stable `call_id` arguments preserve the existing plugin's retry protection. The
same ID and arguments return the saved result or pending state. Signed payment
uncertainty retains its hold. Receipt reconciliation only reads existing evidence.
Changing call IDs cannot bypass the purchase identity or cap checks.

In interactive mode, the session remains open for follow-up work until you use `/finish` or explicitly ask Codex to call
`finish_session`. Closing the TUI without finishing preserves the budget for a
later `--session` attachment. In `--exec` mode, Codex is instructed to submit its
final answer; if it exits successfully without doing so, the launcher saves its
last message as the session result. A failed or interrupted child does not clear
holds, reset the budget or invent a successful result.

Closing the terminal does not close its budget. A lost create response retains
the same session ID and request payload, so retrying cannot allocate a fresh cap.
An unavailable web app is reported inside the terminal; start `governor-web`
and retry your prompt.

## Verification

The interactive terminal was exercised with real Codex CLI 0.154.0: native
`get_budget` and `list_services` calls, streamed answers, and a second prompt
that recalled the first prompt's word on the same Codex thread. `/finish` saved
the final answer. The budget stayed at 10,000 atomic USDC, with zero spend or holds.
Terminal tests cover typed prompts, deltas, tool rows, explicit approvals,
interruption, prompt history, compact layout, persisted thread resume, lost-create
response recovery and immutable payment mode. Conversation messages have durable,
idempotent app records and never consume a payment-tool allowance.

The terminal uses the official
[Codex app-server protocol](https://learn.chatgpt.com/docs/app-server) over stdio.


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
