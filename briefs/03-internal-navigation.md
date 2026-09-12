# Track 03 — Internal navigation (plans first, phones when there are none)

**Team:** 2  
**Difficulty:** Medium–hard  
**Chance of a working demo:** Medium  
**Needs:** Start **from scratch**. A Gemini (or similar) key helps the RERA step. Phones with a barometer help the second step.

---

## The product (one picture)

People already have outdoor maps. The missing product is **the last 80 metres inside a building**: which tower, which floor, which corridor, which door. Delivery and quick-commerce riders hit this every day. Residents hit it when guests cannot find 304.

Two supply regimes, **one stack**, built in that order:

```
[1] RERA / sanctioned floor plans
        → extract walls, doors, corridors, lifts
        → 3D + a walkable graph
        → turn-by-turn inside the plate

[2] No plan (most of Indian housing: pre-2017, renovated, never filed)
        → satellite / OSM / Open Buildings: footprint, height, tower count
        → a coarse interior (cores guessed, corridors approximate)
        → ship that to a rider phone anyway
        → GPS to the gate, then barometer + IMU + “I arrived”
        → traces tighten the graph
```

Step 1 is the clean geometry. Step 2 is **not** required to be perfect. A delivery app does not need millimetre walls. It needs “third floor, left corridor, last door” and a loop that gets less wrong every week.

**You are starting from zero tonight.** Do not assume a finished extractor or a finished society viewer exists. Public inputs (a RERA PDF you download, OSM, a satellite screenshot, the phones in this room) are fair game. Rebuilding a giant pipeline is not the demo; **one building, two modes, one graph schema** is.

## Why the phone loop is the product

Quick-commerce already puts a computer in every staircase. That is the survey team:

- **Barometer** (most iPhones, many Androids): floor changes in a lift or stair. This is the vertical key.
- **IMU / steps:** corridor length and turns (drift is real; loop closure and WiFi/RSSI later).
- **User / rider events:** “wrong floor”, “arrived”, “door on left” — sparse labels that beat another vision model.
- Outdoor GPS dies at the podium. Indoor **starts** there.

Each completed delivery is a labelled path. The approximate satellite interior is the prior. The traces are the likelihood. That is the validation loop. Without it, no-plan nav is a pretty box. With it, the map converges on the buildings you actually serve.

Elita Promenade (where you are sitting) is the no-plan case: possession ~2012, **RERA not applicable**. Use it for step 2. Use any **one** public sanctioned plan PDF you can legally download for step 1. Different buildings is fine. Same **schema** is not optional.

## Schema (freeze at 14:20)

Every number must carry source:

```json
{
  "corridor_width_m": { "value": 1.5, "source": "rera_label | satellite_guess | tape | phone_trace", "confidence": 0.2 }
}
```

`satellite_guess` and `phone_trace` must look different on screen from `rera_label`. If they look the same, you failed.

## Must have by 21:30

**Step 1 — RERA (first, even if rough).**

- One sanctioned floor-plan page in, a navigable plate out: at least corridor + two rooms + a lift or stair, in a simple 3D or 2.5D viewer (Three.js, or even extruded SVG). Path from lift to one room.
- A `confidence.json` with two checks you can compute without a human: polygons close; rooms touch a corridor.

**Step 2 — no plan, satellite prior + phone.**

- Footprint of **this** tower (OSM or a traced satellite outline) + storey count you **count in the stair** or read off the lift panel.
- A coarse graph: ground lobby → lift → one floor loop. Widths marked `satellite_guess` or `default`.
- **One recorded walk** (daylight, done by 16:30): timestamps at lobby, lift, your floor, your door. Barometer series if the phone has it; otherwise step count + floor taps.
- Overlay: guessed graph vs the walk. An **error number** (metres of loop closure, or floors the barometer got right). The number is the deliverable.

## Nice to have

- Rider-shaped UI: “go to tower / floor / door” on a phone browser.
- Fuse: if step 1’s building had a footprint, snap the extracted plate to satellite outline.
- `wrong_floor` button that writes a training row.

## Out of scope

- Photogrammetry, NeRF, Gaussian splats, city-scale scrape, a new mapping app store listing.
- Pretending satellite knows where the corridor is. It knows the **outside**. You infer the inside and you label the inference.
- Perfect metric maps for no-plan buildings. **Good enough for a rider is the bar.**

## Collect data early

**Walk Elita by 16:30**, not at 20:00. One floor loop that ends where it started (loop-closure test). One lift ride (barometer test). Marker taps at corners. Do not photograph other people’s doors; photograph circulation.

## Hour-by-hour

- 14:00–14:20 Schema + which RERA PDF + which Elita tower.
- 14:20–16:30 Person A: plan → viewer. Person B: walk + satellite footprint.
- 16:30–19:00 Graph + barometer plot + first path.
- 21:00 Error number on the TV. Same schema, two sources.

## Demo (21:30)

1. RERA building: “this is what we do when ink exists” — walk a path.
2. Elita: “this is the footprint from the sky; this dashed corridor is a guess; this line is my phone.”
3. One sentence: **quick-commerce phones are how the guess becomes a map.**

## Fallback at 21:00

If extraction is late: a **hand-traced** plate from the PDF still counts as step 1 if the schema and the path work. If the walk is late: show raw barometer + a satellite box and the intended loop. A diagnosed failure on step 2 is an acceptable demo.

## Longer arc

Week 1: ten rider-style walks in one tower. Week 2: floor classifier from barometer + lift detection. The product is not a perfect BIM. It is **outdoor map → indoor graph that pays for itself with delivery traces.**
