# Architecture

Pithos is built in layers. Each layer depends only on the ones below it, so each can be swapped, upstreamed or ported without touching the rest.

```
┌──────────────────────────────────────────────────────────────┐
│ 6. Clustering       llama.cpp RPC across 2-3 briefcases (M4) │
├──────────────────────────────────────────────────────────────┤
│ 5. Mode switching   desktop / server / cluster targets (M2)  │
├──────────────────────────────────────────────────────────────┤
│ 4. Knowledge        Project N.O.M.A.D., stock installer (M3) │
│                     → AI Assistant uses host Ollama          │
├──────────────────────────────────────────────────────────────┤
│ 3. Inference        host-native Ollama + llama.cpp, Vulkan   │
├──────────────────────────────────────────────────────────────┤
│ 2. BC-250 enablement  backports kernel/Mesa, ttm/GTT,        │
│                       GPU governor, sensors, (40-CU unlock)  │
├──────────────────────────────────────────────────────────────┤
│ 1. Base OS          vanilla Debian 13 trixie + backports     │
└──────────────────────────────────────────────────────────────┘
          hardware: BC-250 briefcase (docs/HARDWARE.md)
```

## 1. Base OS

- **Reference:** vanilla Debian 13 "trixie" netinst with no desktop, plus `trixie-backports`. Debian is stable, needs no account, has a long support life, and has good offline mirroring tools.
- **Distro-independent by design.** Layers 2-6 are written as plain systemd units, config drop-ins and shell, with per-distro package lists kept in one place. Debian 13 is just the first target. Other distros arrive at [M6](ROADMAP.md).
- No Ubuntu-specific tooling (no snaps, no PPAs).

## 2. BC-250 enablement

Everything needed to make the GPU usable:

| Piece | Why |
|---|---|
| Backports kernel 7.2.x + Mesa 26.1.x + firmware | Stock trixie Mesa (25.0.7) can't drive gfx1013 with RADV |
| Kernel params `amdgpu.sg_display=0 ttm.pages_limit=4194304 ttm.page_pool_size=4194304` | Display stability; 16 GiB GTT for the GPU |
| modprobe.d + tmpfiles.d ttm settings, `update-initramfs` | Makes the GTT size stick (tmpfiles.d wins last) |
| 16 GiB swapfile | Headroom when loading models |
| `cyan-skillfish-governor-smu` (.deb) | Without it the GPU is stuck at 1500 MHz |
| BIOS: 512 MB UMA, IOMMU off, Secure Boot off | Required memory layout; unsigned optional modules |
| Optional: nct6687d sensors, ACPI fix, 40-CU unlock | Monitoring and performance |

All of this is specific to the hardware and owned by Pithos. Where community projects already exist (the governor, bc250_memcfg, the ACPI fix), Pithos packages or references them instead of forking.

## 3. Inference

- **Host-native Ollama with the Vulkan backend**, running as a systemd service on `0.0.0.0:11434` and firewalled to the LAN and Docker bridges. Defaults: flash attention on, `q8_0` KV cache, keep-alive forever, up to 2 loaded models (chat + embeddings).
- **llama.cpp** built with `-DGGML_VULKAN=ON -DGGML_RPC=ON` for cluster mode and benchmarking ([build docs](https://github.com/ggml-org/llama.cpp/blob/master/docs/build.md)).
- Why on the host and not in a container: N.O.M.A.D.'s bundled AMD container is ROCm-based, and ROCm doesn't support gfx1013, so it runs on the CPU. The standard `ollama/ollama` Docker image does include Vulkan ([Ollama Docker docs](https://docs.ollama.com/docker)), so a containerized Vulkan path is possible later. That's a change for **N.O.M.A.D. upstream**, not for Pithos M1.

## 4. Knowledge: Project N.O.M.A.D.

- **M1 to M5: the stock upstream installer, unmodified** ([Crosstalk-Solutions/project-nomad](https://github.com/Crosstalk-Solutions/project-nomad)). Pithos adds nothing inside N.O.M.A.D. It only:
  1. prepares the content disk at `/opt/project-nomad/storage` (and makes Docker wait for that mount);
  2. runs the upstream `install_nomad.sh`;
  3. sets N.O.M.A.D.'s AI Assistant **remote Ollama URL** to `http://<LAN IP>:11434`, so N.O.M.A.D. stops its own `nomad_ollama` container.
- **N.O.M.A.D. has no authentication**, so Pithos keeps it on the LAN.
- **M6 (multi-distro):** adopt **[nomad-unchained](https://github.com/BuboTheWise/nomad-unchained)** (BuboTheWise's fork with apt/dnf/pacman support) for non-Debian bases, while working to get those changes merged upstream. Pithos should never need its own N.O.M.A.D. fork.

```
 browser ──► N.O.M.A.D. (Docker, :8080) ──► host Ollama (:11434, Vulkan) ──► BC-250 GPU
                  │                                   ▲
                  └── content disk                    └── other LAN clients (laptop, Home Assistant, ...)
                      /opt/project-nomad/storage
```

## 5. Mode switching

One box, three roles, picked at boot (and switchable later):

| Mode | systemd target | Runs | Stops |
|---|---|---|---|
| **Desktop** | `graphical.target` (XFCE) | Ollama with the small model, N.O.M.A.D., optional Steam | big model |
| **Server** | `pithos-server.target` | Ollama with the big model (`pithos-ollama-big.service`), N.O.M.A.D. | display manager |
| **Cluster** | `pithos-cluster.target` | `llama-server` (head) or `ggml-rpc-server` (worker) | Ollama (frees GPU memory) |

- Implemented as GRUB menu entries passing `systemd.unit=<target>`, plus a `pithos-mode` CLI that uses `grub-reboot` for one-shot switches and `systemctl isolate` where safe.
- Units and the CLI use the `pithos-` prefix (package name `pithos-os` or similar) to avoid clashing with Debian's existing `pithos` package, which is an unrelated Pandora radio client.
- **Status:** design only (M2).

## 6. Clustering

Two or three identical briefcases on a gigabit switch can pool memory to run models too big for one box.

```
 head box                                  worker boxes
 llama-server --rpc w1:50052,w2:50052 ◄──► ggml-rpc-server -H <cluster IP> -p 50052 -c
   :8081 (OpenAI-compatible API)
```

- Uses llama.cpp RPC ([tools/rpc README](https://github.com/ggml-org/llama.cpp/blob/master/tools/rpc/README.md)). `-c` enables the local tensor cache on workers.
- **Security:** upstream describes RPC as fragile and insecure. Bind it **only** to the dedicated cluster network or interface, never the general LAN or the internet.
- **Expectations:** clustering adds **capacity** (a bigger model or a higher-quality quant), not speed. Over gigabit Ethernet, generation is usually slower than one box running a model that fits. **[UNVERIFIED on BC-250]**
- Ollama is stopped on all cluster nodes. Clients use the head's `:8081` endpoint, and N.O.M.A.D. can keep using a single box's Ollama.
- **Status:** design only (M4).

## Clients and tiers

Laptops, phones and other machines reach a box through a browser or API. Bigger machines (e.g. an RTX 3090 desktop) can serve higher tiers and share the same [model archive](MODELS.md#the-archive).

## Image builder (later)

[M5](ROADMAP.md) wraps layers 1-3 (and the N.O.M.A.D. pre-seed) into a flashable Debian image using [live-build](https://live-team.pages.debian.net/live-manual/), so a new box can be set up from a single USB stick, offline.
