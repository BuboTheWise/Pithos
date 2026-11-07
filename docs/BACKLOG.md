# Starter backlog

Issues are drafted here first and will be filed once the GitHub repo exists. Each one is tied to a [milestone](ROADMAP.md). Labels: `good first issue`, `hardware`, `docs`, `upstream`.

| # | Milestone | Title | Summary | Labels |
|---|---|---|---|---|
| 1 | M0 | First hardware report: BC-250 on Debian 13 + backports | Run [INSTALL-DEBIAN13](INSTALL-DEBIAN13.md) by hand and file a hardware report. Clear the [UNVERIFIED] marks on kernel 7.2.11, Mesa 26.1.6 and the governor. | hardware |
| 2 | M0 | Benchmark the two BC-250 model picks | Run `tools/ollama-bench.sh` on the fast pick (i1-IQ2_M) and the quality pick (IQ3_XXS) at 4K/16K context, and add the numbers to MODELS.md. | hardware, good first issue |
| 3 | M0 | Measure power draw per mode | Measure watts at the wall for idle, desktop, and sustained server load. Validate the solar/Segway Cube estimates in HARDWARE.md. | hardware |
| 4 | M1 | `pithos-install`: idempotent installer for INSTALL steps 3-8 | Bash with `set -euo pipefail`, a dry-run flag, and a re-run-safe file writer. Calls the **stock** N.O.M.A.D. installer unmodified. | |
| 5 | M1 | Verification script (`pithos-check`) | Automate the checklist (kernel, RADV, GTT, governor, Ollama Vulkan, N.O.M.A.D. containers) with pass/fail output. | good first issue |
| 6 | M1 | nftables profile: Ollama/N.O.M.A.D. LAN-only | Allow 11434/8080 from RFC1918 + 172.16.0.0/12 only. Document that Docker bypasses ufw. | |
| 7 | M1 | Confirm stock N.O.M.A.D. on Debian 13 | Run the upstream installer on trixie. If anything breaks, file it **upstream** with a minimal fix. Record the N.O.M.A.D. version tested. | upstream |
| 8 | M2 | Systemd targets for desktop/server/cluster + GRUB entries | `pithos-server.target`, `pithos-cluster.target`, `pithos-ollama-big.service`, generated `/etc/grub.d` entry. | |
| 9 | M2 | `pithos-mode` CLI | `pithos-mode {desktop,server,cluster} [--once]` using `grub-reboot` and `systemctl isolate`. | |
| 10 | M2 | Choose the desktop-mode small model | Choose the model that fits next to XFCE + Firefox + N.O.M.A.D., with measured memory use. | hardware |
| 11 | M3 | Script N.O.M.A.D.'s remote Ollama URL | Find a supported way (API/config) to set the AI Assistant remote URL without the web UI. If none exists, propose one upstream. | upstream |
| 12 | M3 | Propose a Vulkan Ollama option in N.O.M.A.D.'s AMD container path | Upstream feature request/PR: use the standard `ollama/ollama` image with `/dev/dri` (Vulkan) where ROCm doesn't support the GPU (e.g. gfx1013). | upstream |
| 13 | M4 | llama.cpp Vulkan+RPC build and cluster units | Pinned build recipe, `ggml-rpc-server` worker unit bound to the cluster interface, head `llama-server` unit. | |
| 14 | M4 | Cluster benchmark: 1 vs 2 vs 3 boxes | Measure tokens/s and maximum model size, and document capacity versus speed honestly. | hardware |
| 15 | M5 | `pithos-archive`: fetch, hash and record model provenance | Fetch to `archive/models/...` with README, LICENSE, SOURCE.txt and SHA256SUMS. Add a verify command. | good first issue |
| 16 | M5 | live-build image prototype | Minimal trixie image with backports, governor and Ollama preinstalled. | |
| 17 | M6 | Adopt nomad-unchained for non-Debian bases | Integrate [BuboTheWise/nomad-unchained](https://github.com/BuboTheWise/nomad-unchained) behind a distro check. Debian keeps the stock installer. | upstream |
| 18 | M6 | Per-distro package map and CI matrix | Map Debian/Fedora/Arch package names for layers 1-3, and run container-based install tests. | |
