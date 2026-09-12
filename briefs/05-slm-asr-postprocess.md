# Track 05 — SLM post-processing after Hex / Musly (Mac and Windows)

**Team:** 2  
**Difficulty:** Medium  
**Chance of a working demo:** High  
**Needs:** One Mac and one Windows machine in the pair, or borrow for the last hour. The **same** model must run on both.

---

## The job

[Hex](https://github.com/kitlangton/Hex) is voice → text (macOS hotkey dictation; WhisperKit / Parakeet). [Muesli](https://github.com/Muesli-HQ/muesli) (you’ll hear **Musly**) is dictation with a pipeline that already thinks in **raw ASR vs filtered text**.

ASR is the easy half. The painful half is what you see after:

- `um / uh / like / you know`
- false starts: “send it to Rahul no wait Rohan”
- no punctuation, Indian names, code identifiers, rupee amounts
- “nine a.m. sorry ten thirty” → `10:30`

That cleanup is a **small language model**, not a 70B chat model and not a regex. Hex and Musly should stay the microphone + ASR. **You build the post-processor they can both call.**

Reference-shaped models: [superwhisper/s1-mini](https://huggingface.co/superwhisper/s1-mini) (Qwen3 ~0.6B, filler / stutter / spoken numbers) or a **GGUF ≤ 1B** (Qwen2.5-0.5B-Instruct). Run **locally** after one download. No cloud on the demo path.

## Cross-platform rule (non-negotiable)

| OS | How the SLM runs |
|---|---|
| macOS | `llama.cpp` Metal, or MLX if you must — still expose the **same HTTP API** |
| Windows | `llama.cpp` Vulkan/CPU (CUDA if they have it) via the **same** binary interface |

Implementation that usually survives both: a tiny **Python or Go server** wrapping `llama-cpp-python` / `llama.cpp` HTTP, `POST /v1/clean`. Hex/Musly (or a mock) POST raw ASR, get cleaned text. If you cannot plug into Hex tonight, a CLI + a notepad hotkey is enough — but **run the identical server on both laptops.**

Latency target: **< 300 ms** for a tweet-length utterance on CPU is ideal; **< 1 s** is acceptable. If you need 8B to sound smart, you failed the product.

## Must have by 21:30

1. `POST /v1/clean` `{ "text": "...", "style": "chat|email|code" }` → cleaned text. Deterministic-ish (`temperature` 0).
2. A **fixture file** of 20 ugly ASR lines (Indian names, INR, code, self-corrections). Before/after table in the README.
3. **Same server** started on Mac and on Windows. Screenshot or a 20-second recording of both returning the same cleanup on one fixture.
4. `PRESERVE.md`: what the model must **not** invent (facts, recipients). One adversarial example: ASR says “mail Priya”; model must not add an email address.

## Nice to have

- Side-by-side UI: raw | cleaned (Muesli already wants this).
- Streaming tokens for long rants.
- Quantisation note: Q4 GGUF size on disk, RAM, tokens/s on the two machines.
- A Hex-shaped mock: hold a key, dump mic to Whisper (or paste), then clean.

## Out of scope

- Training a 7B. Sending audio to OpenAI as the only path. macOS-only Swift. Replacing Hex or Musly. Shipping an unsigned driver.

## Hour-by-hour

- 14:00–14:30 Pick the GGUF. Write 20 fixtures. Freeze the JSON schema.
- 14:30–17:00 Server + one OS green.
- 17:00–19:00 Second OS. Latency. PRESERVE cases.
- 21:00 Fixture table on the TV. Both laptops.

## Demo (21:30)

Speak (or paste) a messy sentence with a self-correction and a name. Raw ASR on the left, SLM on the right. Then: “this process is the same binary on Windows.” Then one failure you kept (hallucinated recipient) and how you blocked it.

## Longer arc

Week 1: wire as a local OpenAI-compatible `chat/completions` so Hex/Musly can point at `localhost`. Week 2: Hindi+English code-mix fixtures. The product is a **sidecar**, not another dictation app.
