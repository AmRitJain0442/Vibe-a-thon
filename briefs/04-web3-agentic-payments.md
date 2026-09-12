# Track 04 — Web3 agentic payments

**Team:** 2  
**Difficulty:** Medium  
**Chance of a working demo:** High  
**Chain:** Solana (devnet) or Base testnet. Fast and cheap. One chain only.

---

## Why this, not a token

AI agents are the first users who **structurally cannot** use cards and bank accounts: no KYC in their own name, no ₹0.30 card payment (fees eat it), no T+1. Stablecoins on a fast chain can. That is a reason a Postgres table plus Stripe does not suffice.

The pattern is HTTP **402 Payment Required** (unused in the spec since the 90s). Coinbase **x402**: request → 402 with price and payee → agent pays USDC → retry with proof → server verifies and serves. Docs: [Solana agentic payments](https://solana.com/docs/payments/agentic-payments). Check **current** docs; LLMs will suggest 2021 libraries.

The agent is the user. A human wallet UI is the opposite of the point.

## Must have by 21:30

- A server that gates a **useful** endpoint behind 402 (a tiny tool: summarise text, return a route length, run a toy eval — not “hello world”).
- An agent (LLM + tools, or a script that *acts* like one) that: gets 402 → pays → retries → succeeds **with no human clicking confirm**.
- A live balance that drops.
- A **spend cap**. Ask it to pay more than the cap. It **refuses**. Without this you rebuilt a stolen credit card.

**Devnet/testnet only.**

If the official facilitator is painful on a Saturday: implement the handshake yourself against a local ledger, same headers. Write “facilitator stubbed.” The shape matters more than Coinbase uptime.

## Nice to have

- Two agents: one sells, one buys. No human on either side.
- Seller raises price under load; buyer decides to stop.
- Cost table: this call on Solana vs UPI vs card at ₹0.50. The sub-rupee row is the argument.

## Out of scope

- Your own token. Anchor programs. Bridges. Multi-chain. A wallet app for humans.

## Warning

Budget **one hour** for environment. If setup blows the hour, stub chain, keep 402 + cap.

## Hour-by-hour

- 14:00–14:30 Read current x402/Solana page. Freeze the paid endpoint.
- 14:30–17:00 402 roundtrip.
- 17:00–19:00 Buyer loop + cap.
- 21:00 Glue a real tool behind it. Demo script.

## Demo (21:30)

Agent needs paid data. No API key. Screen: 402, tx, balance down, answer back. Then a hundred more, **stop at the cap**. Sentence: *Stripe could not have done that for an agent that does not exist at a bank.*
