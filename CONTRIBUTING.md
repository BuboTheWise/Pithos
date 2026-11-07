# Contributing to Pithos

Thank you for helping. Pithos is in **pre-alpha / planning**. Right now the most valuable contributions are **real hardware results** and **careful corrections**.

## Ways to help

1. **Hardware reports.** Built a box or tried a step? File a *Hardware report* issue, including what didn't work. Reports are how `[UNVERIFIED]` marks get cleared.
2. **Benchmarks.** Run `tools/ollama-bench.sh` (needs `curl` and `jq`; set `OLLAMA_HOST` for a remote box) and post the output with your kernel, Mesa, governor and Ollama versions.
3. **Docs.** Fix errors, add measurements, simplify steps. Keep it plain and checkable.
4. **Code.** Pick an item from [docs/BACKLOG.md](docs/BACKLOG.md). Open an issue before large changes.

## Ground rules

- **Upstream first.** If a fix belongs in Project N.O.M.A.D., nomad-unchained, llama.cpp, Ollama, or a BC-250 community project, send it there and link it here.
- **Keep Debian 13 as the reference path.** Changes for other distros must not alter Debian behavior.
- **Verify links and commands.** Every URL in the docs should load. Every `ollama pull` should resolve. Don't add guessed links.
- **Mark the unproven.** Use `[UNVERIFIED]` for anything not tested on real hardware, and `[EST]` for estimates.
- **Safety first.** Any change touching power, mains wiring or the PCIe 8-pin connector needs a clear warning and a second reviewer.
- **Licenses.** Code and docs are Apache-2.0. Don't commit model weights, firmware blobs or copyrighted content. Link to the source instead.

## Pull requests

- Keep PRs small and focused. Explain *why*, and how you tested (hardware, distro, versions).
- Shell scripts: `bash`, `set -euo pipefail`, `shellcheck`-clean, idempotent, with a `--dry-run` where they change the system.
- By contributing, you agree your work is licensed under Apache-2.0 (see [LICENSE](LICENSE)).

## Conduct

This project follows the [Code of Conduct](CODE_OF_CONDUCT.md).
