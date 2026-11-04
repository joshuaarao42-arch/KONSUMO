# Contributing to Konsumo

Thanks for helping out!

## Development setup

```bash
git clone <your-fork-url> && cd konsumo
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -m konsumo.cli seed
python run.py
```

## Coding standards

- PEP 8, 4-space indentation, 100-character lines
- Type hints on public functions
- Docstrings on all modules and functions
- All SQL stays in `repository.py` and `database.py`
- Business logic stays out of `web/`

## Branch naming

`feature/<short-desc>`, `fix/<short-desc>`, `docs/<short-desc>`, `chore/<short-desc>`

## Commit messages

Use conventional commits: `feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`.
Write the subject in the imperative mood, at most 72 characters.

## Workflow

1. Fork the repository and create a branch.
2. Make your change and add tests.
3. Make sure `python -m unittest discover tests -v` passes.
4. Open a pull request against `main`.

## Pull request guidelines

- Describe what changed and why, and link the related issue
- Include screenshots for UI changes
- Note anything changelog-worthy
- One logical change per PR

## Code of conduct

Be respectful and constructive. Harassment or discrimination of any kind is not tolerated.
