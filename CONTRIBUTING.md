# Contributing

Thanks for considering a contribution. This template is intentionally small (~150 LoC) — quality of patterns > number of features.

## Welcomed

- Bug fixes / typo fixes
- Tighter type hints / mypy fixes
- Better docs (especially explaining *why* a pattern is there)
- Additional production patterns IF they earn their LoC (e.g. structured retries, OpenTelemetry tracing) — open an issue first to discuss
- Cost-tracker pricing updates as Anthropic ships new models

## Out of scope

- Wrapping the Anthropic SDK in another abstraction layer (langchain etc.) — that's a different project
- Adding a UI framework — minimal `static/index.html` is intentional
- Multi-provider support — keep this Claude-specific, single-purpose

## PR checklist

- [ ] Code formatted (use `black .` if installed)
- [ ] Type hints preserved
- [ ] README updated if behavior visible to users
- [ ] No new runtime deps without explicit justification in PR description

## Reporting bugs

Open an issue with:
- Python version
- `pip show anthropic fastapi` output
- Minimal reproduction
- Expected vs actual behavior

## Discuss before building

For non-trivial changes, open a GitHub Issue first. Saves both our time if the direction is wrong.
