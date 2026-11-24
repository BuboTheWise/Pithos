# ASRock / AMD BC-250: Hardware Reference

A one-page reference for the BC-250 mining blade as used in Pithos. It covers the layout, connectors, LEDs, power, thermals and Linux quirks.

**How to read this file**

- **[CAD]**: read directly from the ASRock GenCAD boardview `ASRock AMD BC-250_ISL_X5R r1.00.cad`, published by the bc-250.com hub (<https://bc-250.com/cad.php>). The file gives exact part numbers, positions and net names. It is a boardview, not a schematic, so some nets are missing.
- **[PHOTO]**: confirmed by looking at a real board photo.
- **[DOC]**: from a community documentation project (links in [Sources](#sources)).
- **[COMMUNITY]**: reported by owners on forums. Treat these as observations, not specs.
- **[UNVERIFIED]**: plausible but not confirmed. Check it before you rely on it.

Coordinates are in mm from the boardview origin. The origin is the lower-left corner with the rear I/O edge on the left, as in the images.

Images in this folder:

| File | What it shows |
|---|---|
| `bc250-leds-annotated.png` | Every LED on the board, on a real photo |
| `bc250-layout-annotated.png` | Top-side layout on a real photo (34 numbered callouts) |
| `bc250-boardview-top.png` | Top side drawn from the CAD boardview, with dimensions and hole coordinates |
| `bc250-boardview-bottom.png` | Bottom side (GDDR6, debug footprint), seen through the board from the top and not mirrored |

> Photo licensing: the two photo-based images use a photo from `mothenjoyer69/bc250-documentation`, a repo with no license file. Credit it, and for a public repo ask the author or use only the boardview renders, which are drawn from data.

---

## 1. Board identity

| Item | Value | Basis |
|---|---|---|
| Board silkscreen | `AMR001 REV 1.00` | [PHOTO] |
| Boardview name | `BC-250_ISL_X5R r1.00` | [CAD] |
| APU part marking | `100-000000656`. The CAD part text reads "AMD ROBIN". | [CAD] [PHOTO] |
| APU codenames in circulation | "Ariel" (mothenjoyer69 docs), "Oberon" (elektricm docs, the PS5 SoC family), GPU IP "Cyan Skillfish" / `gfx1013` | [DOC]. The names disagree; `gfx1013` is the one that matters for drivers. |
| Original use | 12 blades per 4U ASRock Rack mining chassis | [DOC] |

## 2. Physical

| Item | Value | Basis |
|---|---|---|
| PCB outline (bounding box) | **304.66 x 139.98 mm** (11994.41 x 5510.83 mil) | [CAD] |
| Outline shape | Not a full rectangle: there is a notch at the lower right, beside the power connectors | [PHOTO] |
| Other published sizes | "340 / 310 mm x ~115 mm" | [DOC] elektricm. **Conflicts with the CAD; trust the CAD for PCB size.** |
| Weight | ~400 g with heatsink | [DOC] (unmeasured here) |
| Component count | 2163 parts, top and bottom | [CAD] |

### Mounting holes in the boardview

| Hole | Centre (mm) | Notes | Basis |
|---|---|---|---|
| H8 | (7.5, 128.9) | Rear I/O end, near the M.2 slot | [CAD] |
| H9 | (7.5, 28.9) | Rear I/O end, near TPMS1. **H8 to H9 = 100.0 mm.** | [CAD] |
| H15 | (298.8, 122.7) | Far end, under the metal bracket | [CAD] |
| H16 | (298.8, 112.7) | Far end. **H15 to H16 = 10.0 mm.** | [CAD] |

The heatsink and backplate holes around the APU are **not** listed as parts in the boardview, so their spacing is not verified here. Measure them, or take them from the community CAD model ("ASRock BC250 Complete-ish CAD Model" on Printables, by MandicReally).

## 3. Silicon

| Block | Spec | Basis |
|---|---|---|
| CPU | 6 Zen 2 cores enabled (8 present; 2 can be re-enabled per community), ~3.5 GHz. AVX2 present with a halved 256-bit datapath. | [DOC] |
| GPU | RDNA 2-class, **24 CUs** enabled (community "40 CU unlock" exists), `gfx1013`. 1500 MHz locked without a governor, 2000 MHz on stock kernels, up to ~2230 MHz with patches. | [DOC] |
| Memory | **8x Micron MT61K512M32KPA-14** GDDR6 (16 Gb each), all on the **bottom** side around the APU. 8 x 2 GB = **16 GB**, rated 14 Gbps, 8 x 32-bit = **256-bit**, about **448 GB/s**. | [CAD] (part numbers and count). Bandwidth is calculated. |
| Memory model | Unified: CPU and GPU share the 16 GB. The VRAM carve-out is set in BIOS or CMOS (see section 8). | [DOC] |
| Video engine | VCN (hardware encode and decode) **not usable**: the firmware is unavailable | [DOC] |
| FCH / chipset | **AMD Bolton-D2H (A68H)**, `218-0844029`, SU1. Provides USB, SATA, LPC and SPI. | [CAD] |
| Super I/O | **Nuvoton NCT6686D**, UIO1. Handles fans, sensors and the button LEDs (Linux sees chip ID `0xd441`). | [CAD] [DOC] |
| NIC | **Realtek RTL8111H-CG**, U30, PCIe x1, 1 GbE | [CAD] |
| M.2 lane switch | NXP **CBTL04083B**, M2U2: a PCIe Gen3 2:1 mux that switches the M.2 slot between PCIe and SATA | [CAD] |
| BIOS flash | 16 MiB SPI, SOP-8, BIOS_A1. The CAD lists Macronix MX25L12872F; a photographed board has a Winbond 25Q128JV. The footprint includes a socket outline (BIOS_S_A1). | [CAD] [DOC]: the part varies by build |
| Super I/O flash | 512 KiB SPI, SIO1_R. The CAD lists MX25V4035F; docs report MX25L4006E. | [CAD] [DOC] |

## 4. Power delivery

### Inputs

| Connector | Type | Pinout (CAD net names) | Basis |
|---|---|---|---|
| **J1000** (main) | PCIe-style 8-pin, 4.2 mm Mini-Fit, right angle | 3x **+12V** and 5x **GND**. The CAD shows pins 1/3/5 = +12V and pins 2/4/6/7/8 = GND. There are **no sense pins**; every non-12V pin is ground. | [CAD] [DOC] |
| **J2000** | 2x4 Micro-Fit-compatible (ALLTOP C229H7), 3.0 mm | 3x +12V, 3x GND, plus pin 1 = `LED_M_G` and pin 5 = `LED_M_R`. These tap the green and red lines of the LED16 status LED, and docs call them LED1/LED2. | [CAD] [DOC] |
| **J2001** | 2x4 Micro-Fit-compatible | 3x +12V, 4x GND, plus pin 4. Docs call pin 4 `PGD` / PGOOD ("shorting to ground powers the blade off"); **the CAD names that net `PWR_SW`**. | [CAD] [DOC]: same pin, different names |

- The board takes **12 V only**. It has no ATX 24-pin and no PS_ON control, so an ATX PSU must be forced on or switched externally. [DOC]
- **Warning: EPS vs PCIe.** An 8-pin **EPS/CPU** cable is wired differently from an 8-pin **PCIe** cable. Use only a **PCIe** 8-pin (6+2) lead in J1000. Never force an EPS lead in: it puts +12 V onto ground pins. *(Standard ATX knowledge, not specific to the BC-250.)*
- The docs say a 6-pin PCIe lead works for normal loads. Use 8-pin, or add power through J2000/J2001, for overclocking or sustained 220 W+. [DOC]
- The pin current limit (Mini-Fit at 9 A x 3 pins) gives about 324 W through J1000 alone. [DOC]

### VRM

| Rail block | Parts | Basis |
|---|---|---|
| APU main VRM (right of APU) | Renesas **ISL69247** controller (PUA1, "AMD 4+2"), with **6x ISL99360 60 A smart power stages** (PUA11/12/21-24) and 0.15 uH / 90 A chokes (PLA11-24) | [CAD] |
| Secondary VRM (left of APU) | Renesas **ISL95712** controller (PUIO1, 4+3), with 0.33 uH / 60 A chokes (PLS1, PLM1, PLIO1, PLIO2) | [CAD] |
| Other bucks | Richtek RT8237E (PUM1, PUS1), RT6576D (PU24), MPS MPQ8633A (PUVP1) | [CAD] |
| PMBus access | `I2C_HEADER1`: the CAD shows pin 1 = `SMB0_DA_ISO` (SDA), pin 2 = `SMB0_CL_ISO` (SCL), pin 3 = GND. The docs list the order as "SCL SDA GND". **Check with a meter before connecting.** | [CAD] [DOC] |

### Measured consumption (community, wall or DC meters vary)

| State | Watts |
|---|---|
| Idle, no governor (GPU locked at 1500 MHz) | 85-105 |
| Idle, with oberon-governor | 65-85 |
| Desktop | 70-90 |
| Gaming, medium / heavy | 120-150 / 160-200 |
| Peak observed in a game (Cyberpunk RT, stock) | ~235 |
| Sustained 40 CU compute at 2 GHz (llama-bench) | 220-230 |
| FurMark, stock / overclocked | ~250 / ~320 |

Rated TDP is 220 W. Docs recommend at least 300 W of 12 V capacity, or 400 W+ for an ATX unit. [DOC]

## 5. I/O and expansion

| Item | Detail | Basis |
|---|---|---|
| Rear I/O, top to bottom in the images | PANEL1 power/reset buttons, **2x USB 2.0** (stacked, USB1), **DisplayPort** (J4002, the only video out), **2x USB 3.0** (stacked, USB_3_4), LED16 status window, **RJ45 GbE** (LAN1) | [CAD] [PHOTO] |
| DisplayPort | Full size; docs list DP 1.4. HDMI needs an adapter. Audio over DP varies. | [DOC] |
| M.2 | **M2_1**, M-key, 2280 (Foxconn 67-pin, 8.5 mm). **NVMe at PCIe 2.0 x2** (~1 GB/s) **or SATA III**, switched by the CBTL04083B. | [CAD] [DOC] |
| SATA ports | None. SATA reaches only the M.2 slot. | [CAD] (no SATA connector in the parts list) |
| Ethernet | RTL8111H. The jack has 2 LEDs: left green, right green/orange. | [CAD] |
| Wi-Fi / Bluetooth | None on board | [CAD] |
| TPM | No TPM chip. A TPMS1 2x9 2.0 mm LPC header is present (pinout in the docs). | [CAD] [DOC] |

### Headers and jumpers

| Ref | Function | Pinout / notes | Basis |
|---|---|---|---|
| **CPU_FAN1** | 4-pin PWM fan (12 V) | Pin 1 GND, 2 +12V, 3 tach (`CPUFANIN_H`), 4 PWM (`CPUFANOUT_H`) | [CAD] |
| **J4003** | 2x8 2.54 mm, signals for the rack's power distribution board | Tach and PWM for **5 fans** plus DET. **It supplies no fan power.** Fan 1 is the same signal as CPU_FAN1. BIOS fan numbers 1-5 show up in Linux `nct6683` as 2,3,4,5,1. | [DOC] [CAD] |
| **J4004** | SPI flash programming header | CAD: 1 = +3.3VSB, 2 = GND, 3 = CS#, 4 = CLK, 5 = SPI_DI (flash data out, so MISO), 6 = SPI_DO (MOSI), 7 = key, 8 = `PROGRAM#`. That is the pin the docs list as "unknown, 10 k to GND". | [CAD] [DOC] |
| **J5** (shares a footprint with SPEAKER1) | **UART**, unpopulated, 1x4 | CAD: 1 = +3.3VSB, 2 = GND, 3 = `U_TX`, 4 = `U_RX`. Baud rate and console use are **not verified**. | [CAD] [PHOTO] (pads empty) |
| SPEAKER1 | Beeper header, unpopulated | Pin 1 = +5V, pin 4 = speaker drive | [CAD] |
| **AUTO_PWRON1** | 3-pin jumper | 1-2 = power on when 12 V is applied (default); 2-3 = wait for the power button | [DOC] |
| **CLRCMOS1** | 3-pin jumper | 1-2 = normal; 2-3 = clear CMOS | [DOC] [CAD] (nets BAT3 / SB_BATT# / GND) |
| BATTERY1 | CR2032 holder | Upper right | [CAD] [PHOTO] |
| **J2** (bottom) | AMD HDT+ 20-pin 1.27 mm JTAG, unpopulated | Pinout in the docs | [DOC] [CAD] |

## 6. LEDs (complete list from the boardview)

The boardview lists exactly these light sources, **all on the top side**. The bottom side has **no LEDs**; LEDQ1, LEDQ2, LEDD1 and LEDR45 are MOSFETs and a resistor that drive LED16. See `bc250-leds-annotated.png`.

| # | Ref | Where | Part | Colour / behaviour | Who drives it | Basis |
|---|---|---|---|---|---|---|
| 1 | **LED1** | Top side, between hole H8 and the M.2 slot | 0603 SMD, hyper red (EVER 19-217/R6C) | Storage activity ("HDD" LED) | Net `HDLED-`: M.2 `SATA_ACT#` (pin 10) through D4023. A second path from the FCH `SATALED#` goes through **D24, which is unpopulated** on the photographed boards. Hardware only. | [CAD] [PHOTO] [COMMUNITY] |
| 2 | **PANEL1** (2 LEDs) | Rear I/O edge, top corner, seen through clear caps | Wellbuy TC004L stacked tact switch with **blue + green** LEDs | Power button = green; reset button = blue. Community: the protruding button is power and the recessed one is reset. | **NCT6686D Super I/O** (pin 3 drives `PLED`, pin 86 drives `RESETLED`), through Q7481 and Q7482. The power LED's supply is switched by `SLP_S4_S5`. | [CAD] [COMMUNITY] |
| 3 | **LED16** | Board edge between the USB 3.0 stack and the RJ45, shining through a slot in the I/O shield | Harvatek E3113BGR side-view **RGB** SMD; only red and green are wired (common anode to +5V) | Red at idle, green under heavy GPU load, flickers yellow at mixed load | An **LM358 op-amp stage** (U4503) with MOSFETs. It looks like a hardware load or current comparator, **not OS-controlled**. Mirrored on J2000 pins 1 and 5. | [CAD] [COMMUNITY] |
| 4 | **LAN1** (2 LEDs) | Inside the RJ45 jack | UDE S22-AC-0010 jack | Left green; right green/orange (link and speed/activity). Lit only with a cable connected. | RTL8111H LED pins | [CAD] |

**Total: 6 emitters in 4 places.** All are visible from the rear I/O end. Only LED1 faces up from the board surface.

### Blackout notes for Pithos

- Hardware-driven, so they need to be covered: LED16 (status) and LED1 (storage activity).
- **[UNVERIFIED]** The button LEDs are switched by the NCT6686D, so there may be a register-level way to turn them off. No Linux interface for it is documented.
- **[UNVERIFIED]** The Linux `r8169` driver gained netdev LED support in recent kernels (RTL8168/8111 family). If `ls /sys/class/leds` shows Realtek LAN entries, the RJ45 LEDs may be controllable through sysfs.

## 7. Thermals and cooling

| Item | Detail | Basis |
|---|---|---|
| Stock heatsink | Passive aluminium fin stack, fins running front to back, built for rack wind-tunnel airflow. **Not enough on a desk without fans.** Three heatsink variants exist (8-row and 9-row fins); a QR code next to the 8-pin marks the 9-row type. | [DOC] |
| Hot spots | APU, both VRMs, and the **GDDR6 on the underside**, which runs hot. Thermal pads go on the backplate side. | [DOC] [CAD] (memory placement) |
| Typical safe ranges | GPU edge 65-80 °C while gaming; throttling likely above ~85 °C; instability reported above ~90 °C. Memory under ~80 °C. | [DOC] [COMMUNITY] |
| Common fixes | 2x 120 mm high static pressure fans on the (opened) heatsink; replace the paste and pads (PTM7950 is popular); add airflow to the backplate. | [DOC] [COMMUNITY] |

## 8. Firmware, BIOS and Linux quirks

| Topic | Detail | Basis |
|---|---|---|
| BIOS | AMI Aptio. A community-modified BIOS (P3.00 "Chipset menu" builds) exposes more settings. Always keep a backup and a hardware SPI programmer (CH341A/CH347/Pico) for recovery through J4004. | [DOC] |
| VRAM split | Set it in `Chipset > GFX Configuration` (modded BIOS) or with the `bc250memcfg` tool, which writes battery-backed CMOS rather than SPI, so the setting survives reflashes. **512 MB dynamic** is the usual recommendation; 6/10 or 8/8 static splits are also used. | [DOC] |
| TTM / GTT limit | With small splits, raise the TTM page limit so the GPU can borrow more system RAM. Documented values: `ttm.pages_limit=3959290` (+ `ttm.page_pool_size=3959290`) in the mothenjoyer69 docs, and `ttm.pages_limit=3014656` in the elektricm docs. **A value of 4194304 pages (= 16 GiB) is more than the OS can actually hand out after the carve-out, so don't use it.** | [DOC] |
| Scanout | Display framebuffers must live in the real VRAM carve-out; scatter-gather display is off on Cyan Skillfish. | [DOC] |
| IOMMU | **Must be disabled.** It causes black screens and crashes. No GPU passthrough. | [DOC] |
| Mesa / Vulkan | Upstream RADV support since **Mesa 25.1**; Vulkan 1.4 on Mesa 25.3+. Avoid LTS distros. | [DOC] |
| ROCm / HIP | Not usable out of the box: no gfx1013 libraries in AMD userspace. A patched kernel 7.1.5 setup has been shown working (akandr/bc250-rocm). **Vulkan (llama.cpp) is the practical inference path.** | [DOC] |
| GPU governor | `oberon-governor` (config `/etc/oberon-config.yaml`). Saves 20-30 W at idle. Manual clocks go through `pp_od_clk_voltage`. | [DOC] |
| Sensors and fans | `modprobe nct6683 force=true` for reading. For PWM control, the out-of-tree `nct6687` (Fred78290/nct6687d) with `force=true`. | [DOC] |
| Unsupported | Windows GPU drivers, Secure Boot, TPM chip, VCN | [DOC] |
| Power button | No front-panel header. Solder to PANEL1, or use AUTO_PWRON1 with an external PSU switch. | [DOC] [COMMUNITY] |

## 9. Open items (not verified)

1. Heatsink and backplate hole spacing around the APU (not in the boardview).
2. UART on J5: baud rate and whether firmware or the OS prints to it.
3. The LED16 comparator's input signal (the LM358 inputs are not in the boardview netlist).
4. Software control of the PANEL1 LEDs through NCT6686D registers, and of the RJ45 LEDs through `r8169` sysfs.
5. J2001 pin 4: PGOOD (docs) vs `PWR_SW` (CAD net name).
6. I2C_HEADER1 pin order: CAD vs docs.
7. Weight and exact PCB thickness.

## Sources

- Boardview (GenCAD): <https://bc-250.com/cad.php>, file `public/cad/ASRock_AMD_BC-250_ISL_X5R_r1.00.cad`
- mothenjoyer69 documentation: <https://github.com/mothenjoyer69/bc250-documentation> (README and `hardware.md`, including the chip-ID photo)
- elektricm AMD BC250 Documentation: <https://elektricm.github.io/amd-bc250-docs/> (specifications, pinouts, power, cooling, VRAM)
- Status LED behaviour: <https://www.reddit.com/r/BC250Gaming/comments/1r2oqa6/bc250_red_and_green_led/>
- Button and HDD LED wiring, LED1 close-up: <https://www.reddit.com/r/BC250Gaming/comments/1r9eb5f/bc250_leds_and_buttons_external_connection/>
- Power vs reset button: <https://www.reddit.com/r/BC250Gaming/comments/1wtrsgg/bc250_simple_question/>
- ROCm investigation: <https://github.com/akandr/bc250-rocm>
- Community CAD model: "ASRock BC250 Complete-ish CAD Model" (Printables, by MandicReally)
