# Install: Debian 13 (trixie) on the BC-250 (Milestone 1)

This is the **Milestone 1** reference path:

> **vanilla Debian 13 + trixie-backports + host-native Vulkan Ollama + the stock upstream Project N.O.M.A.D. installer, pointed at the host Ollama.**

Pithos M1 doesn't modify N.O.M.A.D. or use a fork. Fork-based multi-distro support (nomad-unchained) is planned for [M6](ROADMAP.md).

Legend: **[UNVERIFIED]** = not yet confirmed on a BC-250 running this exact stack. **[EST]** = estimate. Versions were checked on 2026-11-03.

M1 will turn these steps into a reproducible script ([BACKLOG](BACKLOG.md)). Until that exists, follow them by hand and file a [hardware report](../.github/ISSUE_TEMPLATE/hardware_report.yml).

---

## Why backports is mandatory

| | trixie (stock) | trixie-backports |
|---|---|---|
| Kernel (`linux-image-amd64`) | 6.12.113 | **7.2.11-1~bpo13+1** |
| Mesa (`mesa-vulkan-drivers`) | 25.0.7 (**too old**: no usable RADV on gfx1013) | **26.1.6-1~bpo13+1** |
| `firmware-amd-graphics` | stock | 20260916-1~bpo13+1 |

Sources: [linux-image-amd64 (backports)](https://packages.debian.org/trixie-backports/linux-image-amd64), [mesa-vulkan-drivers (backports)](https://packages.debian.org/trixie-backports/mesa-vulkan-drivers), [mesa-vulkan-drivers (stock)](https://packages.debian.org/trixie/mesa-vulkan-drivers), [backports instructions](https://backports.debian.org/Instructions/).

The community BC-250 docs require Mesa 25.1.3 or newer. Their [Debian page](https://elektricm.github.io/amd-bc250-docs/linux/debian/) still says testing/sid or experimental is needed. That was written before trixie-backports carried Mesa 26.x, so ignore that part.

**Kernel versions to avoid** (per the [BC-250 docs](https://elektricm.github.io/amd-bc250-docs/)): 6.15.0-6.15.6 and 6.17.8-6.17.10. Backports 7.2.11 is newer than the docs' tested list **[UNVERIFIED on BC-250 + Debian]**. Keep the stock 6.12 kernel installed as a fallback.

---

## 0. Hardware prerequisites

1. **PCIe 8-pin polarity:** get 12 V vs GND right. Reversed polarity can kill the board. See [HARDWARE.md](HARDWARE.md#safety).
2. NVMe in the M.2 slot holds the OS and Ollama models. Put N.O.M.A.D. content on a separate disk (e.g. a 3.5" HDD on USB 3) or a second partition.
3. Wired Ethernet.
4. You only need a screen for the install. N.O.M.A.D. and Ollama are used from a browser or API.

## 1. BIOS

- **VRAM split without flashing:** [fanoush/bc250_memcfg](https://github.com/fanoush/bc250_memcfg), `sudo ./bc250memcfg UMA_SIZE 512` (setting 2 GB won't boot; a CMOS clear resets it).
- **Or flash the chipset-menu BIOS** (`BC250_3.00_CHIPSETMENU.ROM`, SHA256 `48fbe5d366e6a56e2fdffdca848426216ba1f083610dab63db89d2f4e6c940b5`; check it before flashing), following [the BC-250 docs' flashing page](https://elektricm.github.io/amd-bc250-docs/bios/flashing/). Afterwards, **clear CMOS** (pull the CR2032 for 60 s), then set:
  - Chipset > GFX Configuration: Integrated Graphics Controller = Forced, UMA Mode = UMA_SPECIFIED, UMA Frame Buffer Size = **512 MB**
  - Advanced > CPU Configuration: **IOMMU = Disabled**
- **Secure Boot: off.** The optional 40-CU unlock and the nct6687d sensor driver build unsigned modules.
- Have a recovery path before flashing: a CH347T (or 3.3 V-modded CH341A) plus a SOIC8 clip. Read the chip twice and compare before writing.

## 2. Install Debian 13 (netinst)

1. Write the amd64 netinst ISO from [debian.org](https://www.debian.org/distrib/netinst) to USB.
2. Black screen? At the boot menu press `e`, append `nomodeset` to the `linux` line, then F10. Use this only for install and first boot.
3. UEFI install, NVMe, ext4 (with btrfs, run `chattr +C` on the swapfile).
4. In tasksel, **untick** "Debian desktop environment" and GNOME, and **tick** "SSH server" and "standard system utilities". The desktop gets added in section 11.
5. On Debian 12 and later, non-free firmware is enabled by default in the installer.

## 3. Backports kernel, Mesa and firmware

```sh
echo 'deb http://deb.debian.org/debian trixie-backports main contrib non-free non-free-firmware' \
  | sudo tee /etc/apt/sources.list.d/backports.list
sudo apt update
sudo apt install -t trixie-backports linux-image-amd64 linux-headers-amd64 firmware-amd-graphics \
  mesa-vulkan-drivers libgl1-mesa-dri mesa-va-drivers vulkan-tools
sudo reboot
```

- Keep `linux-image-6.12.*-amd64` installed (don't autoremove it). It's the GRUB "Advanced options" fallback.
- Checks: `uname -r` should show 7.2.x. `vulkaninfo --summary` should show **RADV GFX1013**, not llvmpipe. `apt policy mesa-vulkan-drivers` should show `~bpo13`.

## 4. Kernel parameters

In `/etc/default/grub`:

```
GRUB_CMDLINE_LINUX_DEFAULT="quiet amdgpu.sg_display=0 ttm.pages_limit=4194304 ttm.page_pool_size=4194304"
```

Then run `sudo update-grub`. The ttm values give a 16 GiB GTT. Don't use the deprecated `amdgpu.gttsize`.

## 5. GPU governor (required)

Without it, the GPU stays stuck at 1500 MHz.

```sh
wget https://github.com/filippor/cyan-skillfish-governor/releases/download/v0.4.14/cyan-skillfish-governor-smu_0.4.14-1_amd64.deb
sudo apt install ./cyan-skillfish-governor-smu_0.4.14-1_amd64.deb   # enables and starts the service
```

- v0.4.14 was the latest release as of 2026-11-03 ([releases](https://github.com/filippor/cyan-skillfish-governor/releases)). The config lives at `/etc/cyan-skillfish-governor-smu/config.toml`. **Never set minimum voltage below 700 mV.** Restart the service after edits.
- Check with `cat /sys/class/drm/card*/device/pp_dpm_sclk`: the `*` should move under load.
- Optional CPU C/P-state ACPI fix: [bc250-collective/bc250-acpi-fix](https://github.com/bc250-collective/bc250-acpi-fix).

## 6. Memory tuning

```sh
echo "options ttm pages_limit=4194304 page_pool_size=4194304" | sudo tee /etc/modprobe.d/ttm-gpu-memory.conf
printf 'w /sys/module/ttm/parameters/pages_limit - - - - 4194304\nw /sys/module/ttm/parameters/page_pool_size - - - - 4194304\n' \
  | sudo tee /etc/tmpfiles.d/gpu-ttm-memory.conf
sudo update-initramfs -u
```

- After rebooting, `cat /sys/module/ttm/parameters/pages_limit` should be `4194304`. (`3145728` means a silent 12 GiB cap; tmpfiles.d is applied last and wins.) `cat /sys/class/drm/card*/device/mem_info_gtt_total` should be `17179869184`.
- 16 GiB swapfile on NVMe:
  ```sh
  sudo fallocate -l 16G /swapfile && sudo chmod 600 /swapfile && sudo mkswap /swapfile && sudo swapon -p 10 /swapfile
  echo '/swapfile none swap sw,pri=10 0 0' | sudo tee -a /etc/fstab
  ```
- **Practical ceiling: about 13 GiB for model plus KV cache** (16 GB physical, shared with the CPU).

Steps 4-6 follow [akandr/bc250](https://github.com/akandr/bc250), translated from Fedora to Debian.

## 7. Ollama on the host (Vulkan)

```sh
curl -fsSL https://ollama.com/install.sh | sh
sudo usermod -aG render,video ollama
sudo setcap cap_perfmon+ep /usr/local/bin/ollama   # lets Vulkan report real free VRAM
sudo systemctl edit ollama
```

Override:

```ini
[Service]
Environment=OLLAMA_VULKAN=1
Environment=OLLAMA_HOST=0.0.0.0:11434
Environment=OLLAMA_FLASH_ATTENTION=1
Environment=OLLAMA_KV_CACHE_TYPE=q8_0
Environment=OLLAMA_KEEP_ALIVE=-1
Environment=OLLAMA_MAX_LOADED_MODELS=2
Environment=OLLAMA_NUM_PARALLEL=1
Environment=OLLAMA_CONTEXT_LENGTH=16384
OOMScoreAdjust=-1000
```

- `MAX_LOADED_MODELS=2` lets N.O.M.A.D.'s embedding model (`nomic-embed-text:v1.5`) stay loaded next to the chat model.
- Use KV cache `q8_0`. `q4_0` can break models that have few KV heads.
- Check: `journalctl -u ollama -b | grep -i 'inference compute'` should show `library=Vulkan`, and `ollama ps` should show 100% GPU. ROCm init errors in the log are expected. References: [Ollama GPU docs](https://docs.ollama.com/gpu), [Ollama Linux docs](https://docs.ollama.com/linux).
- **Firewall (nftables):** allow 11434 only from your LAN and from Docker bridges (`172.16.0.0/12`). Don't rely on ufw alone, because Docker bypasses it for published ports.
- Pull a model (see [MODELS.md](MODELS.md)):
  ```sh
  ollama pull hf.co/mradermacher/Qwen3.6-35B-A3B-uncensored-heretic-i1-GGUF:i1-IQ2_M
  ```

## 8. Project N.O.M.A.D. (stock upstream installer)

M1 uses the **unmodified upstream installer** from [Crosstalk-Solutions/project-nomad](https://github.com/Crosstalk-Solutions/project-nomad) (latest release v1.35.1, 2026-10-05). See also the [official install guide](https://www.projectnomad.us/install).

1. **Content disk first.** Mount it by UUID at `/opt/project-nomad/storage` *before* running the installer:
   ```
   UUID=<uuid>  /opt/project-nomad/storage  ext4  defaults,nofail  0 2
   ```
   Then run `sudo systemctl edit docker` and add:
   ```ini
   [Unit]
   RequiresMountsFor=/opt/project-nomad/storage
   ```
   This stops Docker from writing content onto the NVMe if the content disk is missing.
2. **Install (stock):**
   ```sh
   sudo apt-get install -y curl
   curl -fsSL https://raw.githubusercontent.com/Crosstalk-Solutions/project-nomad/refs/heads/main/install/install_nomad.sh -o install_nomad.sh
   less install_nomad.sh      # read it before running it
   sudo bash install_nomad.sh
   ```
   The installer checks for a Debian-based x86_64 system, installs Docker via get.docker.com (which supports trixie) and sets up `/opt/project-nomad`. It detects the AMD GPU and plans a ROCm container. **Ignore that**: the next step replaces it with the host Ollama.
   **[UNVERIFIED]** Upstream names Ubuntu 26.04/24.04 and Debian 12 as supported. Debian 13 is expected to work but isn't on that list.
3. **Point N.O.M.A.D. at the host Ollama.** Open `http://<box LAN IP>:8080` and go to Easy Setup (or AI Assistant settings later). Choose the remote/existing Ollama option and enter **`http://<box LAN IP>:11434`**. Don't use `localhost`, because inside the container that refers to the container itself. N.O.M.A.D. tests the URL, saves it, and stops its own `nomad_ollama` container.
   - Why: N.O.M.A.D.'s bundled AI Assistant uses the `ollama/ollama:rocm` image for AMD, and ROCm doesn't support gfx1013, so it would run **CPU-only**. Host Vulkan Ollama uses the GPU. Getting a Vulkan path into N.O.M.A.D.'s container setup is upstream work tracked in the [BACKLOG](BACKLOG.md); it isn't needed for M1.
   - N.O.M.A.D. needs `nomic-embed-text:v1.5` for search over your documents, and it can pull it through the remote Ollama.
4. **N.O.M.A.D. has no authentication.** Keep it on the LAN and never port-forward it.
5. **Disk sizing** (N.O.M.A.D. FAQ and install guide): N.O.M.A.D. itself takes about 5 GB, full Wikipedia about 95 GB (125 GB with pictures), Khan Academy about 50 GB, and state maps 2-3 GB each. A 2 TB+ content disk is comfortable **[EST]**.

## 9. Sensors (optional)

[Fred78290/nct6687d](https://github.com/Fred78290/nct6687d) via DKMS, with `nct6683` blacklisted. There are no VRAM or VRM sensors, so check the backplate temperature by touch or with an IR thermometer.

## 10. Optional 40-CU unlock

[duggasco/bc250-40cu-unlock](https://github.com/duggasco/bc250-40cu-unlock) (archived). It must be rebuilt after every kernel update (no DKMS). Running it on the backports 7.2 kernel is **[UNVERIFIED]**. Do this only after everything else is stable.

## 11. Desktop vs server (manual until M2)

- Server: `sudo systemctl set-default multi-user.target` (saves about 1 GB of RAM).
- Desktop: `sudo apt install task-xfce-desktop`. For optional Steam, enable contrib and non-free, then `sudo dpkg --add-architecture i386 && sudo apt update && sudo apt install steam-installer`.
- M2 automates switching between modes (see [ARCHITECTURE](ARCHITECTURE.md#5-mode-switching)).

## 12. Verification checklist

```sh
uname -r                                            # 7.2.x-amd64 (bpo)
vulkaninfo --summary | grep -i deviceName           # RADV GFX1013
apt policy mesa-vulkan-drivers                      # 26.1.x~bpo13
cat /sys/module/ttm/parameters/pages_limit          # 4194304
cat /sys/class/drm/card*/device/mem_info_gtt_total  # 17179869184
systemctl status cyan-skillfish-governor-smu
journalctl -u ollama -b | grep 'inference compute'  # library=Vulkan
ollama ps                                           # 100% GPU
curl http://<LAN IP>:11434/v1/models
docker ps                                           # nomad_* up, no running nomad_ollama
OLLAMA_HOST=http://<LAN IP>:11434 tools/ollama-bench.sh --loaded
```

## Gotchas

- Stock trixie Mesa leaves you with llvmpipe. Backports Mesa is mandatory.
- Don't let N.O.M.A.D.'s `nomad_ollama` container and host Ollama both bind 11434.
- The remote Ollama URL must use the LAN IP.
- tmpfiles.d silently overrides `pages_limit`, so always check the live value.
- Suspend isn't documented as working on the BC-250. Leave it disabled.
