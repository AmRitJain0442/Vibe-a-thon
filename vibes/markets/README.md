# Governor agent

Gemini agent infrastructure for the [Governor PRD](../../PRD.md).
Work lives on `vibes/markets` in `AmRitJain0442/Vibe-a-thon`.

Python 3.12 or newer. Configuration accepts Gemini Developer API credentials or
Google Cloud Application Default Credentials. Monetary limits are integer atomic
USDC units; Gemini cannot change them. Payment mode is currently simulation only.

```bash
cd vibes/markets
python3 -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
cp .env.example .env
pytest
```

The next pieces are the persistent budget ledger, explicit Gemini tool loop,
and a runnable offline scenario.
