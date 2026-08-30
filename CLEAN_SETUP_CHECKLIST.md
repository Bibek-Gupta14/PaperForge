# Clean Setup & Reproducibility Checklist

## Requirements
- Python 3.10+ (Tested on Python 3.13)
- `pip`

## Quick Start (Clean Checkout)
1. Clone the repository:
   ```bash
   git clone <REPO_URL>
   cd PaperForge
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the automated pytest suite:
   ```bash
   python -m pytest tests/test_baseline.py -v
   ```
4. Run the minimal paper reproduction benchmark script:
   ```bash
   python -m scripts.reproduce_minimal
   ```

## Reproducibility Guarantees
- No local file paths or absolute machine references.
- Zero API key requirements (uses deterministic local graph logic and SQLite).
- Pinned graph state signatures in `PAPER_SPEC.md`.
