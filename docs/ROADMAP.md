# Roadmap

Status: **pre-alpha / planning.** The milestones are ordered by dependency. Dates are deliberately left out until hardware testing starts.

| | Milestone | Outcome | Exit criteria |
|---|---|---|---|
| **M0** | **Docs** | This repo: mission, architecture, hardware, install guide, models, backlog | Owner review; first hardware report filed |
| **M1** | **Reproducible Debian 13 install** | **Vanilla Debian 13 + trixie-backports + host Vulkan Ollama + the *stock upstream* Project N.O.M.A.D. installer pointed at the host Ollama.** One idempotent script (`pithos-install`) runs [INSTALL-DEBIAN13](INSTALL-DEBIAN13.md) steps 3-8 (BIOS stays manual). | On a fresh netinst: the script runs twice cleanly; the checklist passes (Vulkan RADV GFX1013, GTT 16 GiB, governor active, Ollama 100% GPU, N.O.M.A.D. up with no `nomad_ollama` running); benchmark numbers recorded |
| **M2** | **Mode switch** | Desktop (XFCE) / server / cluster targets, GRUB entries, `pithos-mode` CLI, per-mode model loading | Switching modes survives a reboot; desktop and server each hit their memory budgets |
| **M3** | **N.O.M.A.D. integration** | Still the stock installer: automated content-disk setup, remote-Ollama configuration, LAN-only firewall, embeddings pre-pulled, offline content pre-seeding. A Vulkan path for N.O.M.A.D.'s own container is proposed **upstream**. | A fresh box reaches a working N.O.M.A.D. + AI chat with no manual web-UI steps [UNVERIFIED that N.O.M.A.D. settings can be scripted] |
| **M4** | **Cluster** | llama.cpp Vulkan+RPC build, `pithos-cluster.target`, cluster network on the NETGEAR switch, head/worker roles | 2-3 boxes serve a model that one box can't fit; results documented honestly |
| **M5** | **Image builder** | Debian live-build image with layers 1-3, first-boot wizard, offline package cache | Flash USB → working box with no internet |
| **M6** | **Multi-distro** | Adopt **[nomad-unchained](https://github.com/BuboTheWise/nomad-unchained)** (BuboTheWise) for N.O.M.A.D. on non-Debian bases; package lists per distro family; CI matrix. Push changes upstream to N.O.M.A.D. wherever upstream will accept them. | At least one non-Debian family (e.g. Fedora or Arch) passes the M1 checklist |

## Principles for every milestone

- **Upstream first.** Fixes that help everyone go to N.O.M.A.D., llama.cpp, Ollama or the BC-250 community projects, not into a Pithos fork.
- **Debian behavior stays the reference.** Multi-distro work must not change the Debian 13 path.
- **Offline-capable.** Anything needed to rebuild a box should be archivable.
- **Mark what's unproven.** Use [UNVERIFIED] until a hardware report confirms it.
