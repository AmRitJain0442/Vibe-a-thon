"""A scripted model drives the real runtime and gate without Gemini credentials."""

from google.genai import types

TASK = "Exercise paid summaries, price changes, a timeout, cap refusals, and a local fallback."

RUNWAY_TASK = (
    "Summarize the ten caller-listed items in priority order. Local extractive fallback is "
    "approved. React to budget runway before the cap is exhausted, then demonstrate an "
    "overpriced refusal separately. All purchases are simulated."
)
RUNWAY_PLAN = [
    {
        "id": f"item-{i:02}",
        "type": "summary",
        "text": f"Article {i}. Governor keeps spending "
        "within its allowance. Planning can finish the job before the budget is exhausted.",
        "allow_local": True,
    }
    for i in range(1, 11)
]


class RunwayDemoModel:
    """A deterministic planner that reads actual forecast output before routing."""

    def __init__(self):
        self.started = False
        self.refusal_checked = False
        self.warning_state = None

    async def generate(self, history, tools, instruction) -> types.GenerateContentResponse:
        responses = [
            part.function_response.response
            for message in history
            for part in message.parts or []
            if part.function_response
        ]
        latest = responses[-1] if responses else {}
        runway = latest.get("runway", {})
        pending = runway.get("pendingTaskIds", [])
        calls = []
        if not self.started:
            self.started = True
            calls = [("list_services", {}), ("get_runway", {})]
        elif pending:
            local = next(
                (
                    o
                    for o in runway.get("options", [])
                    if o["action"] == "route-local" and not o.get("requiresApproval")
                ),
                None,
            )
            items = [t for t in RUNWAY_PLAN if t["id"] in pending]
            if local:
                self.warning_state = runway["state"]
                calls = [
                    ("summarize_local", {"text": t["text"]})
                    for t in items
                    if t["id"] in local["taskIds"]
                ]
            else:
                calls = [("purchase_service", {"service_id": "summary", "text": items[0]["text"]})]
        elif not self.refusal_checked:
            self.refusal_checked = True
            calls = [
                (
                    "purchase_service",
                    {
                        "service_id": "overpriced",
                        "text": "Separate hard-cap refusal check.",
                    },
                )
            ]
        if calls:
            parts = [
                types.Part(function_call=types.FunctionCall(name=name, args=args))
                for name, args in calls
            ]
        else:
            budget = latest["budget"]
            parts = [
                types.Part.from_text(
                    text=(
                        f"Runway demo finished: {runway['tasksCompleted']} of 10 tasks complete. "
                        f"Runway warning: {self.warning_state or 'none'}. "
                        "Local extraction was caller-approved. "
                        f"Simulated spend: {budget['settled']} atomic USDC; "
                        f"remaining: {budget['available']}. "
                        f"Separate overpriced check: {latest['code']}. "
                        "No cap or task scope was changed."
                    )
                )
            ]
        return types.GenerateContentResponse(
            candidates=[
                types.Candidate(
                    content=types.Content(role="model", parts=parts),
                    finish_reason=types.FinishReason.STOP,
                )
            ]
        )


class DemoModel:
    def __init__(self):
        self.step = 0

    async def generate(self, history, tools, instruction) -> types.GenerateContentResponse:
        steps = [
            [("list_services", {}), ("get_budget", {})],
            [
                (
                    "purchase_service",
                    {"service_id": "summary", "text": "Document A. Useful context."},
                )
            ],
            [("purchase_service", {"service_id": "overpriced", "text": "A costly document."})],
            [("purchase_service", {"service_id": "price-change", "text": "A changed quote."})],
            [("purchase_service", {"service_id": "timeout", "text": "A lost response."})],
            [
                ("purchase_service", {"service_id": "summary", "text": f"Document {letter}."})
                for letter in ("B", "C", "D", "E")
            ],
            [("summarize_local", {"text": "Document E. Completed with a local excerpt."})],
        ]
        if self.step < len(steps):
            parts = [
                types.Part(
                    function_call=types.FunctionCall(
                        name=name,
                        args=args,
                        id=f"demo-{self.step}-{index}",
                    )
                )
                for index, (name, args) in enumerate(steps[self.step])
            ]
        else:
            parts = [
                types.Part.from_text(
                    text=(
                        "Offline simulation finished. All paid summaries are simulated. "
                        "Denied purchases produced no authorization. "
                        "The lost-response attempt remains held. "
                        "A local excerpt completed the fallback. See the audit for decisions."
                    )
                )
            ]
        self.step += 1
        return types.GenerateContentResponse(
            candidates=[
                types.Candidate(
                    content=types.Content(role="model", parts=parts),
                    finish_reason=types.FinishReason.STOP,
                )
            ]
        )
