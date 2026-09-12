# Track 01 — Cheap wearable cow health (Indian smallholder)

**Team:** 2  
**Difficulty:** Medium  
**Chance of a working demo:** High  
**Needs:** No prior farm. Public IMU data + a phone. Hardware is optional.

---

## The constraint

India has on the order of **300 million bovines**. The median owner has **two or three animals**, not two hundred. Western collars at $50–150/head plus a gateway plus a subscription are a feedlot product. At three animals they are absurd.

So: **build from very small, inside a hard BOM.** Target **₹800–1,500 per animal** in parts you can buy on a Saturday (MCU + IMU + battery + webbing). Not a smaXtec bolus. Not a FLIR van. A wearable the farmer can lose in a monsoon and replace.

That cost cap is the engineering problem. If you blow it, you have built the wrong company.

## What we are actually trying to catch

Ranked by money lost on an Indian smallholding (same ranking as the earlier vibeathon cow brief):

1. **Mastitis** — udder infection. Largest cause of milk loss. **Sub-clinical mastitis is invisible** and quietly destroys yield for weeks.
2. **Oestrus (heat)** — miss a cycle, wait ~21 days, delayed calving, lost income. Visible signs often happen **at night**.
3. **Lameness** — under-reported, painful, cuts feed intake and yield.
4. **Reduced rumination** — leading indicator for almost everything else. A cow that chews less is usually about to be sick **12–48 hours** before anything you can see.

The wearable does not “diagnose” these like a vet. It **classifies cheap signals** that correlate, with an honest confidence. Claiming mastitis from an accelerometer alone is how you get ignored.

## Sensor → problem (be strict)

| Problem | Cheap signal that is in BOM | What is *not* in BOM |
|---|---|---|
| Rumination | Neck IMU spectral / time-series (jaw–neck coupling). Hard on a ₹150 MPU6050; still the right first attempt | Rumen bolus, microphone on the jaw |
| Oestrus | Night activity spike, restlessness vs that animal’s own baseline | Pedometer folklore without a baseline |
| Lameness | Less walking than yesterday; optional step asymmetry | Computer-vision gait in a dark shed |
| Mastitis | **Temperature:** body vs a directed IR reading at milking. **Pulse:** only if a sensor actually couples (ear/tail PPG is experimental on cattle) | Somatic cell count, conductivity meter |

**Temperature and pulse are in scope if they fit the rupee cap**, because they are the only honest path at this price to mastitis-shaped alerts. IMU-only mastitis is out.

Suggested BOM (street prices, Bangalore):

| Part | Role | ~₹ |
|---|---|---|
| ESP32 (or equivalent) | MCU + BLE to phone | 250–400 |
| MPU6050 / MPU9250 | 6/9-axis IMU @ 10–25 Hz | 80–200 |
| 18650 + holder + TP4056 | Power | 150–250 |
| Webbing / 3D-printed collar | Wearable | 50–150 |
| **MLX90614** (optional, stay in cap) | Non-contact IR temp | 150–250 |
| **MAX30102** (optional, experimental) | PPG pulse — expect it to fail on a cow; still log it | 80–150 |

Stay **≤ ₹1,500**. No custom PCB tonight. Phone IMU is the live demo if nobody brought boards.

**Indian cows:** Gir, Sahiwal, HF-cross have different activity and heat-stress (THI) baselines. A model trained on Japanese Black or EU dairy will silently lie. Tonight: leave-one-animal-out, and a README note that field data must be **Indian animals, Indian climate**. Heat-stress makes **temperature** extra valuable here; a European rumination model without THI is half a product.

## Data (no cow required tonight)

Hunt datasets in the **first 30 minutes**:

- [Frontiers IoT collar IMU](https://www.frontiersin.org/journals/veterinary-science/articles/10.3389/fvets.2025.1630083/full) — MPU9250-class, walking / grazing / resting, 10 dairy cows. Copy this BOM.
- [Zenodo Japanese Black, 13 behaviours, 25 Hz](https://zenodo.org/records/5849025)

If you find an Indian open set, use it. If not, train on public IMU and **do not** put “validated on Gir” on the slide.

## Must have by 21:30

1. **Classifier from a cheap IMU**, 1–3 s windows, tiny features (mean, std, energy, dominant axis, one spectral band if you chase rumination). Classes at least: walking / active-or-grazing / resting. Macro-F1 on a **held-out animal**, not a random row split.
2. **A mapping file** `alerts.yml`: which of the four problems this signal is allowed to flag, and at what confidence. Example: `resting_night_down + activity_up → oestrus_suspect 0.4`. Mastitis only if temp (or pulse) is in the pipeline.
3. **Live path:** same features on phone `DeviceMotion`, or BLE from the ESP32. You walk / sit / mimic head-down. It is not a cow. It proves the loop.
4. **BOM table** with rupees, and a one-line false-positive story (“herder turns this off if it pings at 2 a.m. for a cow that is sleeping”).

## Nice to have

- IR temp: two numbers, “body-ish” vs “udder-ish”, delta flag as `mastitis_suspect` — labelled as a **screen**, not a diagnosis.
- Pulse log from MAX30102 on a human finger first (the sensor works), then one honest sentence that cattle PPG is unproven at this price.
- Cost model: ₹/animal/year at herd size 2, 20, 200 vs a $80 collar.
- Offline: model size vs a ₹10,000 Android.

## Out of scope

- Buying cattle. Training a video model. LoRaWAN for a district. SCC / conductivity. Claiming lameness because a paper mentioned it in passing. Anything over ₹1,500/head.

## Hour-by-hour

- 14:00–14:30 Dataset + leave-one-cow-out rule + freeze `alerts.yml`.
- 14:30–17:30 Features, model, confusion matrix.
- 17:30–19:00 Phone or ESP32 live path. Wire temp if the part is on the table.
- 21:00 BOM + alerts + demo script.

## Demo (21:30)

Phone (or collar) streams classes. A 6-hour synthetic trace trips **heat** (night restlessness) and **rumination-suspect** (activity spectral drop) with the confidence numbers from `alerts.yml`. Then the BOM: “three animals, ₹X, vs a feedlot collar.” Then the sentence: **sub-clinical mastitis is not this IMU; it is the IR delta if we have it.**

## Longer arc

Week 1: five collars, one gaushala, two Indian animals. Week 2: attachment (half the error). Mastitis: milking-time IR, not 24 Hz udder fantasy. Rumination vs rest on MPU6050 is the hard cheap problem — time-series or a second modality; do not promise it until measured on Gir/Sahiwal/HF-cross in Karnataka heat.
