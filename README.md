# Vibe-a-thon

Elita, JP Nagar. 12 Sept.

`main` is the shared floor — briefs, this readme, empty vibe folders. **Do not build on `main`.**

Each vibe has a folder under `vibes/` and a branch `vibe/<name>`. You live on your branch. You only touch your folder. After the demo (tonight, tomorrow, next week — whenever it is actually worth keeping) you open a PR into `main`. That is how this becomes one repo without five people overwriting each other today.

## The five

| Branch | Folder | Brief |
|---|---|---|
| `vibe/cow-health` | [vibes/cow-health](vibes/cow-health) | [briefs/01-cow-health.md](briefs/01-cow-health.md) |
| `vibe/fractional` | [vibes/fractional](vibes/fractional) | [briefs/02-fractional-tokenisation.md](briefs/02-fractional-tokenisation.md) |
| `vibe/indoor-nav` | [vibes/indoor-nav](vibes/indoor-nav) | [briefs/03-internal-navigation.md](briefs/03-internal-navigation.md) |
| `vibe/agent-payments` | [vibes/agent-payments](vibes/agent-payments) | [briefs/04-web3-agentic-payments.md](briefs/04-web3-agentic-payments.md) |
| `vibe/slm` | [vibes/slm](vibes/slm) | [briefs/05-slm-asr-postprocess.md](briefs/05-slm-asr-postprocess.md) |

Code goes in `vibes/<name>/`. Nowhere else.

## How you start (once)

```bash
git clone https://github.com/Shaurya-M002/Vibe-a-thon.git
cd Vibe-a-thon
git checkout vibe/cow-health    # or vibe/fractional / vibe/indoor-nav / vibe/agent-payments / vibe/slm
```

Build inside `vibes/…`. Push to **your** branch:

```bash
git add vibes/cow-health
git commit -m "cow: first classifier"
git push -u origin HEAD
```

Two people on the same vibe: same branch. Pull before you push (`git pull --rebase`) so you do not fight.

## How it comes back together

Do not merge during the day. Tonight is for demos, not git hygiene.

When a vibe is worth keeping:

1. Still on your branch. Folder still only yours.
2. Open a pull request into `main`.
3. Someone glances at it (no secrets, no mainnet keys, no 4GB model files) and merges.

That is the “slowly together” part. One PR per vibe. Not five people committing to `main` at 9pm.

## Please do not

- Commit `.env`, private keys, mainnet wallets, other people’s audio, cow data you do not have rights to, or a GGUF.
- Edit another team’s `vibes/` folder “to help”.
- Open a personal branch (`shaurya-wip`, `fix-2`) unless you are actually stuck. One branch per vibe is the whole point.

Laptop, charger, phone. Something has to run on a screen.
