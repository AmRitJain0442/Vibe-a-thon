# Governor — Spending Control for Autonomous Agent Payments

**Status:** Draft v0.1 · Hackathon Track 4
**Owner:** *(you)*
**Last updated:** 12 Sep 2026

> *Governor* is a working name — the mechanical device that caps an engine's speed regardless of how hard you press the throttle. Rename freely.

---

## 1. Summary

Governor is a client-side spending control layer for AI agents that pay for services autonomously over x402. The agent discovers a price, checks it against a hard budget held in its own code, and either authorizes payment or refuses — with no human approving each transaction and no reliance on the seller behaving honestly.

The current implementation is an agent that buys real services (FX rates, summarization) on Base Sepolia with testnet USDC, enforces a session cap and a per-call cap, shows its balance falling in real time, and stops cleanly when a payment would breach the cap.

---

## 2. Problem

x402 makes it trivial for an agent to pay for an API call. That is the entire point, and it is also the entire problem.

**Nothing in the protocol limits spending.** A server can demand any amount in its 402 challenge. A naive client signs whatever it is handed. There is no monthly invoice to review, no spending alert, no chargeback, and no bank to call. Stablecoin settlement is final.

The failure modes are not hypothetical:

| Failure | Cause | Today's outcome |
|---|---|---|
| Runaway loop | Retry bug, bad termination condition | Wallet drained overnight |
| Price manipulation | Seller quotes $0.001, charges $0.30 in the 402 | Agent pays, nobody notices |
| Cost drift | 10,000 calls at $0.001 each | $10 spent with no single alarming transaction |
| Compromised endpoint | Legitimate service replaced or hijacked | Agent trusts it, pays it |

Every one of these is invisible to the seller, the facilitator, and the chain. They can only be caught in the buyer's own code, before a signature exists.

**Thesis:** spending control is not a feature on top of agentic payments. It is the precondition for anyone deploying them.

---

## 3. Why now

- Per-request payment is newly practical. L2 stablecoin settlement costs a rounding error, so an API can charge per call instead of per month. HTTP 402 was reserved in 1997 and sat unused for ~30 years because no settlement layer was cheap enough.
- Agents increasingly run unattended, across many services, with no per-action human approval.
- Account-based controls don't transfer. There is no API key to revoke, no subscription to cancel, no rate limit tied to an identity. The wallet *is* the identity.

---

## 4. Users and jobs

**Primary — the agent developer.** *"Let my agent buy what it needs without risking my wallet."* Wants a cap they can reason about, and evidence afterwards of what was bought and why.

**Secondary — the finance or platform owner.** *"Show me what the agents spent, and prove the limits held."* Wants an audit trail, not a screenshot.

**Tertiary — the seller.** Benefits indirectly: buyers with enforced budgets are buyers who can be given access without a contract.

---

## 5. Principles

1. **Refuse before signing.** A refused payment must never produce a signature. Not cancelled — never created. There is nothing to replay and nothing to revoke.
2. **Never trust the seller's arithmetic.** Advertised price, quoted price, and the 402 challenge are three separate claims. Enforce against the challenge.
3. **Integers only.** Atomic token units throughout. No floating point anywhere near money.
4. **Fail closed.** Corrupt state, unreachable RPC, ambiguous challenge → refuse.
5. **Every decision is loggable.** A choice that cannot be explained afterwards is indistinguishable from a bug.
6. **Degrade before you stop.** Prefer a cheaper or local path over failing the task — but stop honestly when no acceptable path exists.

---

## 6. Scope

### V0 — shipped tonight

Single agent, single seller, hard caps, live demo.

- Session cap and per-call cap enforced in code before authorization
- Three-phase ledger: reserve → commit / release
- On-chain USDC balance shown before and after
- Refusal path demonstrated live, with no signature produced
- Persisted ledger state so a crash does not free a hold
- Mock facilitator fallback so the demo cannot be killed by a dry faucet

### V1 — the trust boundary

Makes client-side enforcement *necessary* rather than merely present.

- **Adversarial seller suite.** A second service that quotes $0.001 publicly and demands $0.30 in the 402; another that re-challenges after payment to double-charge. Agent detects and refuses both.
- **Velocity cap.** Spend-per-minute limit on top of the total cap, to catch runaway loops that individually clear every check.
- **Crash recovery.** Kill the agent mid-payment; on restart the hold is still on disk and the cap still holds.
- **Expense report.** CSV of every settled payment with explorer links, emitted on exit.

### V2 — routing and choice

Turns enforcement into optimization.

- **Local-vs-paid routing** with amortized cost modelling (§8)
- **Decision log** with counterfactuals (§8)
- **Multi-seller comparison** — read several 402 challenges, buy the cheapest that fits
- **Marketplace discovery** via x402's Bazaar layer *(API details not yet verified — see §12)*

### V3 — delegation

- **Signed spending authority.** A human signs an EIP-712 grant (max $X, until time T, these payees only). Every payment references it, so "who authorized this?" has a cryptographic answer.
- **Budget slicing.** A parent agent with $1 spawns children with $0.20 each; children cannot exceed their slice, and the parent cannot exceed the envelope.

---

## 7. Core architecture

```
Agent ──1── request ──────────────▶ Service
      ◀──2── 402 + PAYMENT-REQUIRED ──
      │
      3. BUDGET GATE  ◀── the product
      │   price vs remaining vs per-call cap
      │   ├── refuse → stop. no signature exists.
      │   └── authorize → hold funds, then sign
      │
      ──4── retry + PAYMENT-SIGNATURE ─▶
                                    verify + settle via facilitator
      ◀──5── 200 + PAYMENT-RESPONSE ────
      │
      6. commit hold at settled amount
```

**The gate is the whole product.** Steps 1, 2, 4 and 5 are x402; step 3 and 6 are Governor.

### The ledger

Three phases, because a payment can fail *after* it is authorized:

| Phase | Effect | When |
|---|---|---|
| `reserve(amount)` | Funds held; remaining drops immediately | Before signing |
| `commit(id, actual)` | Hold becomes a settled spend | Settlement confirmed |
| `release(id, reason)` | Hold returns to budget | Settlement failed |

Holds persist to disk. If the agent dies between signing and settlement, the funds stay held rather than becoming silently re-spendable.

`commit` clamps the settled amount to the reserved amount. A seller cannot charge more than was authorized, even if the facilitator reports a larger figure.

Caps are always read from configuration, never from the state file — otherwise anyone who can write that file can raise the agent's own limit.

---

## 8. Cost routing and the decision log *(V2)*

### Local is not free

An idle GPU is the most expensive inference there is. Local cost is amortized, not zero:

```
local marginal cost   = instance $/hr ÷ requests/hr actually served
break-even throughput = instance $/hr ÷ API price per call
```

*Illustrative:* an L4-class instance at roughly $0.80/hr against a $0.001 API call breaks even near 800 req/hr. Below that, paying the API is strictly cheaper. Verify current cloud pricing before quoting these numbers.

Two states behave very differently:

- **Cold** — nothing running. Include spin-up, model load, and minimum billing increment. One request routed local might cost $0.02.
- **Warm** — already running and not shuttable for N minutes. Marginal cost approaches zero; route local until saturation.

So the correct answer to "local or paid?" legitimately changes minute to minute. The agent must show its working.

### Decision log entry

```json
{
  "task": { "kind": "summarize", "tokens": 1200 },
  "candidates": [
    { "id": "x402:seller-a", "cost": "1000", "source": "402-challenge",
      "latency": 480, "quality": 0.92 },
    { "id": "local:slm", "cost": "220", "source": "amortized", "warm": true,
      "basis": { "usdPerHour": 0.80, "observedReqPerHour": 3600 },
      "latency": 1400, "quality": 0.74 }
  ],
  "constraints": { "qualityFloor": 0.70, "budgetRemaining": "39000" },
  "chosen": "local:slm",
  "why": "warm; 3600 req/hr vs 800 break-even; quality 0.74 clears floor",
  "wouldFlipIf": "throughput <800/hr, quality floor >0.74, or instance cold",
  "saved": "780",
  "ledgerRef": null
}
```

`wouldFlipIf` is what separates an audit record from a rationalization — it states the conditions under which the same agent would decide differently. `ledgerRef` links a paid decision to its hold and settlement hash, so there is one continuous trail: **decision → authorization → receipt.**

---

## 9. Functional requirements

Numbered so they can be tested individually.

**Enforcement**

- **FR-1** Every payment is checked against the ledger before any signature is created. *Test: refuse a payment; assert no payload was produced.*
- **FR-2** A payment exceeding the per-call cap is refused with code `PER_CALL_CAP_EXCEEDED`.
- **FR-3** A payment exceeding remaining session budget is refused with code `SESSION_CAP_EXCEEDED`.
- **FR-4** Refusals are recorded in the ledger as `DENIED` entries with price, remaining, and reason.
- **FR-5** Enforcement is performed by Governor's own ledger, not delegated to the payment SDK's built-in controls. SDK controls may act as a secondary backstop only, configured loosely enough that they never pre-empt the primary gate.
- **FR-6** All monetary comparison uses integer atomic units.

**Accounting**

- **FR-7** Funds are held at authorization and released if settlement fails.
- **FR-8** Settled amount is clamped to the reserved amount.
- **FR-9** Ledger state survives process restart, including outstanding holds.
- **FR-10** Caps are sourced from configuration, never from persisted state.

**Observability**

- **FR-11** Remaining budget is displayed after every payment attempt.
- **FR-12** On-chain balance is readable before and after a session.
- **FR-13** A complete audit trail is emitted at session end.

**Resilience**

- **FR-14** An unreachable RPC degrades gracefully; it does not crash the agent or bypass a check.
- **FR-15** A malformed or missing 402 challenge results in refusal, not a guess.

---

## 10. Non-goals

- **Mainnet.** Testnet only. No real-funds code path exists, deliberately.
- **Being a wallet or custody solution.** Governor holds no keys beyond the agent's own.
- **Replacing the facilitator.** Verification and settlement stay with x402 infrastructure.
- **Fraud detection or seller reputation.** Governor enforces *the buyer's* limits; it does not judge sellers beyond price.
- **Human-in-the-loop approval.** The explicit requirement is that no person approves each payment.

---

## 11. Success metrics

**Demo (tonight)**

- Multiple payments settle; balance visibly decreases
- At least one payment refused, with zero signature produced
- Audit trail reconciles: settled total = starting budget − remaining

**Product**

- Zero cap breaches across adversarial-seller and runaway-loop test suites
- Every payment traceable to a decision record
- Overhead per call small relative to payment latency
- *(V2)* Measurable spend reduction from routing, with the counterfactual logged

---

## 12. Risks and open questions

| Risk | Assessment | Mitigation |
|---|---|---|
| SDK controls pre-empt our gate | **Confirmed** — observed in testing; SDK spend controls fire before the ledger hook, so the refusal is attributed to the library and never logged | FR-5: loosen SDK caps so the ledger is the primary gate |
| Hold leaks on crash | Real | Persisted holds; reconciliation on startup |
| Seller quotes one price, charges another | Real, easy to execute | V1 adversarial suite; enforce against the challenge only |
| x402 adoption is early | Genuine uncertainty — I have not verified current adoption levels | Protocol-agnostic ledger; the gate is reusable |
| Bazaar marketplace API | **Unverified** — seen referenced in seller docs, not tested | Check docs before building V2 discovery |
| Cloud pricing figures | **Illustrative only** | Verify live pricing before any public claim |
| Marketplace listings are self-declared | By design, listing ≠ verification | Strengthens the case for client-side enforcement |

**Open questions**

1. Should velocity caps be time-windowed or token-bucket?
2. How should quality scores for routing be obtained — declared, benchmarked, or observed?
3. Does a signed spending grant need on-chain revocation, or is expiry enough?
4. Per-agent budgets, or per-task budgets that expire with the task?

---

## Appendix A — verified technical facts

Confirmed by reading installed package internals (`@x402/*` v2.25.0), not from documentation alone.

- Network identifiers use CAIP-2: Base Sepolia is `eip155:84532`
- The 402 challenge travels in the **`PAYMENT-REQUIRED`** response header; **the response body is empty**
- The client retries with a **`PAYMENT-SIGNATURE`** header; the server replies with **`PAYMENT-RESPONSE`**
- `PaymentRequirements.amount` is a string in atomic units (USDC: 6 decimals)
- `onBeforePaymentCreation` returning `{ abort: true }` throws **before** `createPaymentPayload` is called — **no EIP-3009 signature is ever produced.** This is the technical basis of Principle 1.
- Facilitator wire protocol: `GET /supported`, `POST /verify`, `POST /settle`
- The testnet facilitator at `https://x402.org/facilitator` covers Base Sepolia and Solana devnet
- Under the `exact` scheme the buyer pays no gas; the facilitator broadcasts

## Appendix B — current state

**Working:** 402 handshake end to end · ledger reserve/commit/release · persistence · balance display · mock facilitator with real signature recovery · free price-list endpoint.

**Open:** first paid call after startup can return 500 (suspected facilitator `initialize()` race) · refusal is currently attributed to SDK spend controls rather than the ledger, so denials are not logged (see FR-5).
