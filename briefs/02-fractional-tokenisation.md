# Track 02 — Fractionalisation / tokenisation (any asset)

**Team:** 2  
**Difficulty:** Medium  
**Chance of a working demo:** Medium  
**Needs:** If you are new to crypto, do the **Friday primer** below. This idea is new for most people in the room. Do not sit here cold.

---

## Friday primer (90 minutes, before Saturday)

Read in this order. The point is vocabulary, not becoming a trader.

1. What a **wallet**, a **token**, a **transaction**, and a **stablecoin** are. One chain for the weekend: **Solana devnet** (or Base testnet). No mainnet.
2. A token is a **ledger entry** other people’s software can move without your database’s permission. That sentence is the whole track.
3. Banks already fractionalise: mutual funds, REITs, securitised loans, carbon desks at large institutions. Write down: *what do they already do well?*
4. Then: *what does a chain add that their core banking system does not?* If you cannot answer before 14:00, pick another track.

You do **not** need to have built a contract before. You do need to have seen a block explorer once.

## Banks can already slice assets. Why bother with crypto?

Be **positive and specific**, not cynical and not naive.

Large banks and institutions already fractionalise:

- Real estate via REITs / SM REITs  
- Credit via securitisation  
- Funds via unit registries  
- Increasingly **carbon** (voluntary and compliance lots) via registries (Verra, Gold Standard, national systems)

They are good at **origination, KYC, legal wrappers, custody of the underlying, and regulators**. That layer does not go away. Crypto does not replace the bank. It changes the **rail after the claim exists**.

What Web3 uniquely enables (this is the demo thesis):

| Property | Bank / registrar database | Token on a public (or permissioned) chain |
|---|---|---|
| Transfer at 03:00 to a stranger | Bilateral, office hours, a ticket | Atomic, if the token’s rules allow it |
| Ticket size | Floor set by ops cost per investor | Can drop toward rupees once issued |
| Compose with other money | New legal agreement each time | Same token can be collateral, streamed, split again |
| Distribution of a coupon / tonne / royalty | Batch file, reconciliation | One program, holders whoever they are *now* |
| Secondary exit | Internal bulletin board, illiquid | Anyone who may hold (allowlist or open) can bid |

**The asset can be anything that has a claim:** a flat, a parking bay, an invoice, a **tonne of CO₂e**, a future harvest, a machine’s uptime. Real estate is one example, not the definition. Carbon is a good second example because the “thing” is already abstract and already lives in a registry — tokenisation is a **duplicate, programmable registry**, not a deed to land.

Honest constraint (say it in the demo): India retail + VDA tax + securities law still apply if the token is an investment. Tonight is a **mechanism prototype**, not a product you sell on Telegram.

## Pick one asset at 14:15 and freeze

Not “tokenise the world.” One:

- **A. Carbon.** 1 token = 1 kg CO₂e of a named vintage (fake project ID is fine). Retire = burn. Transfer = trade the leftover. This shows fractionalisation of a **future / environmental** asset, not a building.
- **B. Cashflow.** Monthly rent or a solar PPA slice. Coupon to current holders.
- **C. Real-world unit.** One parking bay or one flat *as an example of the same machinery*, not as the only story.

Same program for all three: **mint → allowlisted transfer (or open, with a comment) → distribute or retire.**

## Must have by 21:30

1. **`WHY_CHAIN.md` (≤ 500 words).** Banks already fractionalise X. Crypto adds Y (use the table). One paragraph on carbon (or invoices) so nobody thinks this is only real estate.
2. **A token on Solana devnet (or a local chain)** whose supply maps to the asset (1000 tokens = 1 tonne, or 100 tokens = one bay).
3. **A secondary move:** Alice sells some to Bob on-chain. Balances update. This is the property databases hate.
4. **A programmatic event:** either `distribute()` (coupon) or `retire()` (carbon burn). No spreadsheet reconciliation step in the demo.

## Nice to have

- Allowlist: Mallory cannot receive. (Securities-shaped assets.) Carbon might be open; say why.
- Stream a tiny coupon every N seconds (Sablier-shaped) to show “future cashflow” rather than a monthly batch.
- One slide: ticket ₹100 vs SM REIT ₹10 lakh — ops cost, not magic.

## Out of scope

- Mainnet. Real money. Your own meme ticker. “DAO of the atmosphere.” Solving SEBI tonight. Pretending a token *is* a khata or a Verra certificate.

## Hour-by-hour

- 14:00–14:30 Primer recap + freeze asset A/B/C.
- 14:30–17:30 Mint + transfer on devnet. First explorer link.
- 17:30–19:00 Distribute or retire + `WHY_CHAIN.md`.
- 21:00 Alice→Bob live. Mallory fails if you built allowlist.

## Demo (21:30)

“A bank can already split this asset for 200 rich clients. Watch 1% move to Bob in ten seconds with no ticket, then watch the coupon (or a carbon retire). That rail is what crypto is for. The legal wrapper is still a job.”

## Longer arc

Origination stays with whoever is allowed to create the claim (developer, carbon project, lender). The chain is the **transfer and distribution bus**. If you ever take rupees from the public, you are in securities / CIS land — stop and get counsel.
