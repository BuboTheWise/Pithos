# Pithos

**An offline AI and knowledge box that you own, and that keeps working when the grid and the internet don't.**

A *pithos* is the large Greek storage jar from the story usually told as "Pandora's box". When everything else had escaped the jar, hope was still inside. This project tries to build that kind of container: a sturdy box that holds what a community needs when things go wrong.

## Mission

Pithos helps people and communities keep a capable AI assistant and a deep offline library under their own control, on hardware they can afford, powered by whatever electricity is available.

- **Works when things are down.** Power outages, wildfire evacuations, Santa Ana wind shutoffs, a dead cell tower, a cabin running on solar. The library and the assistant don't depend on a connection.
- **Owned, not rented.** It runs on your hardware and your network, with no accounts and no cloud. No one can switch it off remotely, change the terms, or read your questions.
- **Local AI as something people keep.** Open models get pulled, gated and relicensed. Pithos keeps verified local copies of models and knowledge so access doesn't depend on a hosting site's decisions.
- **Built to be shared.** Every box is built the same way. Neighbors can swap parts, copy each other's archives, and link boxes together to run models none of them could run alone.

## What it is

Pithos is a reproducible software stack and build guide for a portable "briefcase" AI node:

- **Base OS:** vanilla **Debian 13 (trixie)** plus trixie-backports. It's not Ubuntu, and the long-term goal is to support any distro.
- **Inference:** host-native **Ollama** and **llama.cpp** on Vulkan.
- **Knowledge:** [Project N.O.M.A.D.](https://github.com/Crosstalk-Solutions/project-nomad) for offline Wikipedia, medical references, maps, courses and an AI chat front end.
- **Modes:** a light desktop, a headless server, or a node in a small cluster.
- **Clustering:** identical boxes link over gigabit Ethernet (llama.cpp RPC) to run larger models together.

## Who it's for

- Households and neighborhoods in outage-prone areas (wildfire country, rural grids, storm paths).
- Preparedness and mutual-aid groups, CERT teams, and off-grid builders.
- Self-hosters who want a private assistant that isn't tied to a subscription.
- Anyone who believes local AI should stay in people's hands.

You should be comfortable with a Linux terminal and with basic electrical safety. Pithos is not a consumer product.

## Reference hardware

| Part | Reference choice |
|---|---|
| Compute | ASRock/AMD **BC-250**: Cyan Skillfish APU (GPU gfx1013), 16 GB shared GDDR6, stock heatsink |
| Inner case | nyacom "Industrial Style Case for FlexATX" ([Printables 1737913](https://www.printables.com/model/1737913) • [printed kit on eBay](https://www.ebay.com/itm/236997099720?var=537406080449)), 3D printed |
| Power supply | Apevia ITX-PFC500W FlexATX, inside the printed case |
| Outer case | Apache 4800 hard case with filtered lid fan ports, so it can run with the lid closed |
| Power entry | One fused IEC C14 AC inlet. Runs from any 120 V source: grid, a power station (e.g. Segway Cube with 200-400 W of portable solar), or the kit inverter on a 12 V battery |
| Network | Onboard gigabit Ethernet; a NETGEAR Plus gigabit switch in the shared kit links boxes together |
| Display (optional) | NexDock lapdock (video plus USB; exact cabling [UNVERIFIED]) |

A complete box costs roughly **US $550-600** (late-2026 prices, owner's estimate). See [docs/HARDWARE.md](docs/HARDWARE.md).

Other machines can join as clients or bigger tiers. For example, a laptop (Framework) or a desktop with an RTX 3090 can share the same model archive and point at the same services. See [docs/MODELS.md](docs/MODELS.md).

## Modes

| Mode | What runs | Model |
|---|---|---|
| **Desktop** | XFCE (light), N.O.M.A.D., Ollama, optional Steam; NexDock as screen and keyboard | A small, fast model sized to leave room for the desktop (choice open, see [MODELS](docs/MODELS.md)) |
| **Server** (headless) | No desktop; Ollama with the big model; N.O.M.A.D. | Best model that fits in ~13 GiB |
| **Cluster** (2-3 boxes) | llama.cpp `llama-server` on one box, RPC workers on the others | Larger or higher-quality quantizations split across boxes |

## Quick start (outline)

> **Status: pre-alpha / planning.** No Pithos box has been built and tested end to end yet. The steps below are the planned Milestone 1 path. Read [docs/INSTALL-DEBIAN13.md](docs/INSTALL-DEBIAN13.md) before touching hardware.

1. **Build and power the hardware safely.** Pay special attention to PCIe 8-pin polarity ([HARDWARE](docs/HARDWARE.md)).
2. **Set up the BIOS** for VRAM split and IOMMU ([INSTALL §1](docs/INSTALL-DEBIAN13.md#1-bios)).
3. **Install Debian 13** from netinst, without a desktop.
4. **Install the backports kernel and Mesa** (trixie-backports: kernel 7.2.x, Mesa 26.1.x), set kernel parameters and memory tuning, and install the `cyan-skillfish-governor-smu` GPU governor.
5. **Install Ollama on the host** with Vulkan and pull a model, e.g.
   `ollama pull hf.co/mradermacher/Qwen3.6-35B-A3B-uncensored-heretic-i1-GGUF:i1-IQ2_M`
6. **Install Project N.O.M.A.D. with its standard upstream installer**, then point its AI Assistant at the host Ollama: `http://<box LAN IP>:11434`.
7. **Verify** with the checklist in the install guide, and run `tools/ollama-bench.sh` to record speeds.

Milestone 2 adds desktop/server mode switching, and Milestone 4 adds clustering. See the [ROADMAP](docs/ROADMAP.md).

## Status

**Pre-alpha, planning stage.** This repository currently contains design and install documentation. Many details are marked **[UNVERIFIED]** until someone confirms them on real hardware. Prices and package versions are snapshots from late October and early November 2026.

## Relationship to Project N.O.M.A.D.

- **[Project N.O.M.A.D.](https://github.com/Crosstalk-Solutions/project-nomad)** (Crosstalk Solutions, Apache-2.0) supplies the offline library and the AI chat front end. Upstream targets Debian-based systems, with Ubuntu recommended. **Pithos Milestone 1 uses the stock upstream installer, unmodified, on Debian 13.** Debian 13 isn't on upstream's named support list, so this is [UNVERIFIED] until tested.
- **Upstream first.** Wherever a change helps everyone, such as a Vulkan GPU path in N.O.M.A.D. or installer fixes, Pithos aims to get it merged upstream instead of carrying a fork. The fork is a bridge, not a destination.
- Pithos owns the parts specific to this hardware: kernel and Mesa versions, the GPU governor, memory tuning, host Vulkan inference, mode switching, clustering, the hardware build and, later, a flashable image.

Pithos is an independent community project. It isn't affiliated with Crosstalk Solutions, ASRock or AMD.

## Documentation

| Doc | Contents |
|---|---|
| [ARCHITECTURE](docs/ARCHITECTURE.md) | The layers, from base OS to clustering |
| [HARDWARE](docs/HARDWARE.md) | Briefcase bill of materials, power, safety |
| [HARDWARE-SINGLE](docs/HARDWARE-SINGLE.md) | Single-unit hardware (one BC-250 in an Apache 5800), measured nyacom case, closed-case cooling, BOM, clustering units over default 1G direct cable (optional 5GbE; a 5GBASE-T switch for three or more), test protocol (draft) |
| [INSTALL-DEBIAN13](docs/INSTALL-DEBIAN13.md) | Step-by-step Milestone 1 install |
| [MODELS](docs/MODELS.md) | Model tiers, picks per machine, the archive approach |
| [ROADMAP](docs/ROADMAP.md) | Milestones M0-M6 |
| [BACKLOG](docs/BACKLOG.md) | Starter issues tied to milestones |
| [CONTRIBUTING](CONTRIBUTING.md) | How to help, including hardware reports |

## Meatspace to-do

Physical-world build and verification work — not software issues. These need a real box, hands, and tools. Check them off as you go. Details live in [`docs/HARDWARE.md`](docs/HARDWARE.md) and [`docs/HARDWARE-SINGLE.md`](docs/HARDWARE-SINGLE.md).

### Build and assembly
- [ ] Confirm the nyacom case cover variant (neo vs classic) for the BC-250 and document the choice (was issue #22)
- [ ] Fit-check the Apache 5800 vs 4800 enclosure and pick the better fit (was issue #27)
- [ ] Verify cable and plug clearance at I/O, PSU, and fan points before first power-on (was issue #28)
- [ ] Design, print, and fit-test hold-down brackets, bumper pads, and the external deflector hood (was issue #29)

### Thermal and cooling
- [ ] Run closed-case thermal + recirculation testing; confirm lid-closed temperature deltas are acceptable (was issue #23)

### Power
- [ ] Measure real wall power draw at idle, desktop, and sustained server load; validate the solar / Segway Cube estimates (was issue #5)
- [ ] Confirm Apevia ITX-PFC500W spare availability and qualify at least one FlexATX alternative PSU (was issue #26)

### Benchmarking and qualification
- [ ] Run the first full hardware report (BC-250 on Debian 13) and clear the [UNVERIFIED] marks on kernel 7.2.x, Mesa 26.1.x and the GPU governor (was issue #3)
- [ ] Benchmark the fast pick (i1-IQ2_M) and the quality pick (IQ3_XXS) at 4K/16K context; record numbers in MODELS.md (was issue #4)
- [ ] Cluster benchmark: 1 vs 2 vs 3 boxes — tokens/s and max model size, documented honestly (was issue #16)
- [ ] Benchmark default 1G interlink vs optional 5GbE; qualify the faster path only if prefill actually saturates 1G (was issue #24)
- [ ] Qualify a 5GBASE-T switch for clusters of three or more units (~$100–200) (was issue #25)

### Model selection
- [ ] Choose the desktop-mode small model and record measured memory use next to XFCE + Firefox + N.O.M.A.D. (was issue #12)

### Monitoring and safety
- [ ] Add pull-fan tachometer monitoring and over-temperature alerts for the GDDR6 hot side and other unmonitored areas (was issue #31)

## Safety

This project involves mains wiring, high-current 12 V power, lithium power stations and hot electronics inside a closed case. Get help if you aren't qualified, and test everything with the lid open before trusting it closed. Nothing here is a substitute for real emergency services.

## License

[Apache License 2.0](LICENSE), the same license as Project N.O.M.A.D. Third-party models, firmware and content keep their own licenses.