# Hardware: the Pithos briefcase

Each Pithos box is a **self-contained briefcase**: a BC-250 in a 3D-printed case with its own PSU, carried and run inside a hard case. It has one AC inlet and runs from any 120 V source.

Boxes are **identical and standalone**. Each one is a complete library and assistant on its own. Put several on a gigabit switch and they can share load as a [cluster](ARCHITECTURE.md#6-clustering).

Legend: **[UNVERIFIED]** = not yet confirmed on a built unit. **[EST]** = estimate. **TBD** = placeholder for a community-confirmed value.

## The board: ASRock/AMD BC-250

| | |
|---|---|
| APU | AMD "Cyan Skillfish": 6 Zen 2 cores, RDNA-class GPU (`gfx1013`), 24 CU stock (40 CU with the optional unlock) |
| Memory | 16 GB GDDR6, shared between CPU and GPU (512 MB UMA carve-out; the GPU uses the rest through 16 GiB GTT) |
| Storage | One M.2 NVMe slot (PCIe 2.0 x2, so any cheap NVMe works) |
| Power | One PCIe 8-pin 12 V input |
| Outputs | DisplayPort, gigabit Ethernet, USB |

References: [BC-250 community docs](https://elektricm.github.io/amd-bc250-docs/), [specifications](https://elektricm.github.io/amd-bc250-docs/hardware/specifications/), [mothenjoyer69/bc250-documentation](https://github.com/mothenjoyer69/bc250-documentation), [akandr/bc250 (LLM benchmarks)](https://github.com/akandr/bc250).

## Bill of materials (reference build)

Prices are owner snapshots from late October 2026 and change constantly. Some retailer pages block automated link checks, so they're named here without links. Search by name or part number.

| # | Part | Notes | Price (USD) |
|---|---|---|---|
| 1 | ASRock/AMD BC-250 board | Used/surplus market | TBD |
| 2 | nyacom "AMD BC-250 Industrial Style Case for FlexATX" (Printables model **1737913**) | 3D-printed, designed around the Apevia PSU. Print in PETG (PLA softens at ~55-60 °C). Optional handle part. | filament TBD |
| 3 | Apevia ITX-PFC500W FlexATX PSU | 12 V ~33 A. Has headroom for the 40-CU unlock. | ~49.99 |
| 4 | Apache 4800 hard case (Harbor Freight) | Interior ~454 × 327 × 168 mm. Lid fan ports allow lid-closed running. | ~59.99 |
| 5 | Lid intake and exhaust ports with filters, plus printed plenums | Ports sit over the fan end and the hot end, 300 mm or more apart, with a divider so air doesn't recirculate. **[UNVERIFIED] thermal performance with the lid closed.** | TBD |
| 6 | Fused IEC **C14** panel inlet | The **only** power entry. 5×20 mm **6.3 A slow-blow** fuse. Earth bonded to PE. | TBD |
| 7 | 120 mm high-static-pressure PWM fan(s) and filters | Per the nyacom design | TBD |
| 8 | NVMe SSD, 1 TB | OS and models | TBD |
| 9 | Content disk (2 TB+ HDD or SSD) | N.O.M.A.D. library, mounted at `/opt/project-nomad/storage` | TBD |
| 10 | Panel pass-throughs: RJ45 bulkhead (with cap), USB, video | | TBD |
| 11 | Thermal pads/plate for the GDDR6 on the back of the board | The board has **no VRAM/VRM sensors** | TBD |
| | **Complete box target** | | **~550-600 [EST]** |

### Shared kit (one per group, not per box)

| Part | Purpose |
|---|---|
| NETGEAR Plus (smart managed) gigabit switch, 5- or 8-port | Connects briefcases for clustering, plus a laptop client |
| Short Cat6 patch cables | One per box |
| Inverter: **Victron Phoenix 12/800** (120 V, pure sine) | Runs a box from any 12 V battery or vehicle. Stored in the kit. **[UNVERIFIED]: check the continuous rating against the peaks below.** |
| Power station: e.g. **Segway Cube** plus **200-400 W** of portable solar | Off-grid power through the station's **AC outlet** |
| Display (optional): NexDock lapdock and cables | For desktop mode |

## Power

| State | Wall draw | Source |
|---|---|---|
| Idle, governor installed | ~65-85 W **[EST]** | Community reports |
| Sustained LLM inference (stock 24 CU) | ~220-280 W | Community reports, [bc-250.com PSU guide](https://bc-250.com/wiki?article=hardware%2F03-power-supply-guide) |
| Peaks (FurMark/LLM, unlocked) | up to ~370 W | [bc-250.com cooling guide](https://bc-250.com/wiki?article=hardware%2F04-cooling-guide), [BC-250 docs: power](https://elektricm.github.io/amd-bc250-docs/hardware/power/) |

**Off-grid notes**

- The box has **no DC input and no internal battery**, by design. A DC/Powerpole input was considered and rejected to keep one simple, fused entry point. Every source has to deliver 120 V AC into the C14.
- **Segway Cube:** use its **AC outlet**. Its DC outputs (13.6 V, 10 A max on a single port) can't run the board ([Cube manual](https://store.segway.com/media/codebaby/product-file-uploads/3085/Segway_Cube_series_user_manual_US_version__1.pdf)). Its Anderson port is an *input*.
- **Solar budget [EST]:** at ~250 W average under load and ~75 W idle, a 1 kWh station gives roughly 3-4 hours of heavy use, or a day or more of mostly-idle library use. 200-400 W of panels can roughly keep up with light use in good sun. Measure your own numbers and add them to the docs.
- Fit the duty cycle to the power you have. Server mode with the model unloaded, or desktop mode with a small model, uses far less energy than sustained generation.

## Safety

> **PCIe 8-pin polarity can kill the board.** The BC-250's 12 V input is a PCIe 8-pin connector fed from the PSU. Reversed 12 V/GND wiring will destroy it. Check pinout and polarity with a multimeter **before** the first power-on.

- Use **16 AWG minimum** for 12 V wiring. **No SATA or Molex-to-PCIe adapters.**
- **Mains:** the C14 inlet carries 120 V into the case. Insulate the terminals (heat shrink or boots), add strain relief, bond earth, use the correct slow-blow fuse, and fit a printed finger guard over any exposed mains terminals. If you aren't qualified to wire mains, get help.
- **Heat:** 220-370 W has to leave a closed case. Never block the ports. Test under sustained load (e.g. `tools/ollama-bench.sh` in a loop, or llama.cpp) with the lid **open**, then closed, and watch temperatures (`sensors`, the governor, and an IR thermometer on the backplate) before trusting lid-closed operation.
- **GDDR6 and VRM on the back side** get hot and have no sensors. Use pads plus a plate or airflow.
- **GPU governor:** never set the minimum voltage below **700 mV**.
- **BIOS flashing:** verify SHA256 first and have a SPI programmer recovery path ([flashing docs](https://elektricm.github.io/amd-bc250-docs/bios/flashing/)).
- **Lithium power stations:** follow the manufacturer's instructions. Don't charge inside a closed case or in a hot vehicle.

## Clients and other tiers

Pithos boxes serve any device on the LAN through a browser (N.O.M.A.D.) or the Ollama API. Bigger machines can join as tiers that share the same [model archive](MODELS.md):

- **Laptop (e.g. Framework):** a client, or a mid-tier with its own models.
- **Desktop with RTX 3090 (24 GB):** a high tier for larger or higher-quality quantizations.

## Display (desktop mode)

A NexDock works as a portable screen and keyboard. Owner notes: use an *active* DP-to-HDMI adapter (or passive, at about 1080p/1440p) into the NexDock's mini-HDMI, plus USB for the keyboard and touchpad. Power the NexDock from its own USB-C PD charger. Plain DP-to-USB-C into the NexDock doesn't work. **[UNVERIFIED across NexDock models.]**
