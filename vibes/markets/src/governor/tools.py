"""Allowlisted tools with strict arguments and no access to keys or policy writes."""

from google.genai import types
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from governor.mock import extractive_summary
from governor.payments import PaymentGate


class NoArguments(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class TextArguments(NoArguments):
    text: str = Field(min_length=1, max_length=12000)


class PurchaseArguments(TextArguments):
    service_id: str = Field(min_length=1, max_length=64)


class ToolRegistry:
    def __init__(self, gate: PaymentGate):
        self.gate = gate
        self.schemas = {
            "list_services": (
                NoArguments,
                "List approved services and advertised atomic USDC prices.",
            ),
            "get_budget": (NoArguments, "Read the task's available, held, and settled budget."),
            "get_runway": (
                NoArguments,
                "Read advisory p50/p90 budget runway and the immutable caller task list. "
                "UNKNOWN means no supported projection. Advice never changes payment authority.",
            ),
            "purchase_service": (
                PurchaseArguments,
                "Purchase an approved service for input text through Governor. "
                "Identical service/text purchases in this session reuse the original result. "
                "Denials and pending payments are final for that attempt; use a fallback.",
            ),
            "summarize_local": (
                TextArguments,
                "Return up to three opening sentences locally, without a payment. "
                "This is an extractive fallback, not an LLM summary.",
            ),
        }

    def declarations(self) -> list[types.FunctionDeclaration]:
        return [
            types.FunctionDeclaration(
                name=name,
                description=description,
                parameters_json_schema=schema.model_json_schema(),
            )
            for name, (schema, description) in self.schemas.items()
        ]

    async def execute(self, name: str, arguments: dict) -> dict:
        if name not in self.schemas:
            return {"ok": False, "code": "UNKNOWN_TOOL"}
        schema, _ = self.schemas[name]
        try:
            parsed = schema.model_validate(arguments)
        except ValidationError as exc:
            return {
                "ok": False,
                "code": "INVALID_ARGUMENTS",
                "fields": [".".join(map(str, error["loc"])) for error in exc.errors()],
            }
        if name == "purchase_service":
            return await self.gate.purchase(parsed.service_id, parsed.text)
        if name == "list_services":
            data = {
                "services": [s.model_dump() for s in self.gate.services.values()],
                "simulation": True,
            }
        elif name == "summarize_local":
            data = {
                "summary": extractive_summary(parsed.text),
                "method": "local extractive",
                "payment_amount": "0",
                "completed_task_ids": self.gate.ledger.complete_local(
                    self.gate.session_id,
                    parsed.text,
                ),
            }
        elif name == "get_runway":
            data = {"task_plan": self.gate.ledger.plan(self.gate.session_id)}
        else:
            data = {}
        return {
            "ok": True,
            "code": "OK",
            "data": data,
            "budget": self.gate.ledger.snapshot(self.gate.session_id),
            "runway": self.gate.ledger.report(self.gate.session_id)["runway"],
        }
