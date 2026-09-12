# Vibe-a-thon

Elita, JP Nagar. 12 Sept.

`main` is the shared floor — briefs, this readme, empty project folders. **Do not build on `main`.**

Each project has a folder and a branch with the same name. You live on your branch. You only touch your folder. After the demo (tonight, tomorrow, next week — whenever it is actually worth keeping) you open a PR into `main`. That is how this becomes one repo without five people overwriting each other today.

## The five

| Branch / folder | Brief |
|---|---|
| `01-cow-health` | [briefs/01-cow-health.md](briefs/01-cow-health.md) |
| `02-fractional` | [briefs/02-fractional-tokenisation.md](briefs/02-fractional-tokenisation.md) |
| `03-indoor-nav` | [briefs/03-internal-navigation.md](briefs/03-internal-navigation.md) |
| `04-agent-payments` | [briefs/04-web3-agentic-payments.md](briefs/04-web3-agentic-payments.md) |
| `05-slm` | [briefs/05-slm-asr-postprocess.md](briefs/05-slm-asr-postprocess.md) |

Code goes in `projects/<that-name>/`. Nowhere else.

## How you start (once)

```bash
git clone https://github.com/Shaurya-M002/Vibe-a-thon.git
cd Vibe-a-thon
git checkout 01-cow-health    # or 02-fractional / 03-indoor-nav / 04-agent-payments / 05-slm
```

Build inside `projects/…`. Push to **your** branch:

```bash
git add projects/01-cow-health
git commit -m "cow: first classifier"
git push -u origin HEAD
```

Two people on the same project: same branch. Pull before you push (`git pull --rebase`) so you do not fight.

## How it comes back together

Do not merge during the day. Tonight is for demos, not git hygiene.

When a project is worth keeping:

1. Still on your branch. Folder still only yours.
2. Open a pull request into `main`.
3. Someone glances at it (no secrets, no mainnet keys, no 4GB model files) and merges.

That is the “slowly together” part. One PR per project. Not five people committing to `main` at 9pm.

## Please do not

- Commit `.env`, private keys, mainnet wallets, other people’s audio, cow data you do not have rights to, or a GGUF.
- Edit another team’s `projects/` folder “to help”.
- Open a personal branch (`shaurya-wip`, `fix-2`) unless you are actually stuck. One branch per project is the whole point.

Laptop, charger, phone. Something has to run on a screen.
