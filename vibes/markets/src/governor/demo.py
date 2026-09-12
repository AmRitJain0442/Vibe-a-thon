"""A scripted model drives the real runtime and gate without Gemini credentials."""

from google.genai import types

TASK = "Exercise paid summaries, price changes, a timeout, cap refusals, and a local fallback."


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
