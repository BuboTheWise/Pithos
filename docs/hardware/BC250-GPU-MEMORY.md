# BC-250 GPU Memory for Larger Models

How to give a Pithos BC-250 enough GPU memory for larger LLMs. The board has 16 GB of GDDR6 shared by the CPU and the GPU. A small fixed UMA carve-out is reserved as real VRAM; the GPU borrows the rest through GTT (a Linux Graphics Translation Table ceiling, not a reservation).

## Tested values (reference unit, 2026-11-19)

- **BIOS:** UMA Frame Buffer Size = **512 MB**
- **Kernel command line:**

```
ttm.pages_limit=3959290 ttm.page_pool_size=3959290 amdgpu.gttsize=15466
```

- **Result:** a GTT ceiling of about **15 466 MiB** (~15.1 GiB), plus the 512 MB fixed VRAM carve-out. Check with `dmesg | grep -i gtt`.

## Legend

- **[UNVERIFIED]** — not confirmed on a Pithos reference unit
- **[RELATED]** — present in current or pending repo docs, but not part of the tested command line

---

## 1. BIOS: 512 MB UMA carve-out

The 512 MB setting is a **minimum** VRAM allocation, not the GPU's maximum. It leaves as much of the 16 GB as possible available as ordinary RAM until the GPU needs it.

### 1.1 Making the UMA size option appear

Stock BIOS images often hide the VRAM / UMA controls. Two facts are established:

1. **The Chipset / GFX / UMA screens are unlocked by the community P3.00 Chipset Menu image**, `BC250_3.00_CHIPSETMENU.ROM` (SHA256 `48fbe5d366e6a56e2fdffdca848426216ba1f083610dab63db89d2f4e6c940b5`; always check the hash before flashing). That image is the community standard for unlocked chipset menus, the GFX UMA UI, and related NBIO options. Follow the [BC-250 flashing guide](https://elektricm.github.io/amd-bc250-docs/bios/flashing/) and have a SPI-programmer recovery path before you write anything. After a flash, **clear CMOS** (pull the CR2032 for at least 60 seconds, or use the clear jumper, then restore it) or the new settings often will not stick.
2. **On that image, the size option is not visible until two earlier settings are applied**, then saved or confirmed in the same menu. Community notes cited by the [VRAM guide](https://elektricm.github.io/amd-bc250-docs/bios/vram/) place the size control under **Chipset → GFX Configuration**. Set them in this order:

   1. **Integrated Graphics Controller** = **Forced**
   2. **UMA Mode** = **UMA_SPECIFIED**
   3. **UMA Frame Buffer Size** = **512 MB** (the menu may show `512MB`)

If the size field still does not appear, you do not have to flash or hunt further menus to get the 512 MB split: use the Linux utility in [§1.3](#13-setting-the-split-without-the-bios-menu).

A path such as **AMD CBS → NBIO → …** is sometimes mentioned in general AMD firmware discussions and in descriptions of what the chipset-menu image unlocks. **It was not established as the menu path used on the reference unit.** Do not assume that path exists or that it is required.

**[UNVERIFIED]** Which exact BIOS image the reference unit is running (stock P3.00, P3.00 Chipset Menu, P5.00, or something else) was not recorded with the 2026-11-19 memory-config test. The 512 MB UMA value and the Chipset → GFX Configuration procedure above are the documented Pithos settings.

When flashing the chipset-menu image, write it to the flash chip labeled **BIOS_A1**, never **SIO1_R**, then clear CMOS. If the flash tool reports an error, do not power off or reboot; photograph the screen and recover from there.

Enter setup with **Del**. A direct DisplayPort connection to a PC monitor is the reliable way to see the menus; some HDMI adapters and TVs show a black screen in firmware.

### 1.2 Other BIOS settings

These are part of the documented BC-250 enablement:

| Setting | Value |
|---|---|
| **Advanced → CPU Configuration:** IOMMU | **Disabled** (community docs treat IOMMU as broken on this board) |
| **Secure Boot** | **off** (needed for unsigned modules such as the GPU governor or sensor drivers) |
| **Boot mode** | **UEFI** |

Save with **F10**.

### 1.3 Setting the split without the BIOS menu

Flashing is **not** required just to change the split. On stock P3.00 or P5.00, or if the menus are missing after a flash:

```sh
git clone https://github.com/fanoush/bc250_memcfg
cd bc250_memcfg && make
sudo ./bc250memcfg UMA_SIZE 512
```

Then reboot. The change is stored in extended CMOS, so it survives a BIOS reflash but is **lost on a CMOS clear**. Re-check after any clear.

**Do not use 2 GB** (`UMA_SIZE 2048`): Linux will not boot with that split. A CMOS clear undoes a bad value.

Confirm the live carve after reboot:

```sh
cat /sys/class/drm/card*/device/mem_info_vram_total
# 536870912 = 512 MiB
free -h
# system RAM should be about 16 GB minus the 512 MB carve
```

---

## 2. Kernel parameters (tested)

Add all three together:

```
ttm.pages_limit=3959290 ttm.page_pool_size=3959290 amdgpu.gttsize=15466
```

**Arithmetic:** `3 959 290 × 4 KiB = 15 465.98 MiB`, which is why `amdgpu.gttsize` is set to `15 466`. The three parameters are the tested set and agree at that ceiling. That is about 400 MiB below `16 GiB − 512 MiB` (15 872 MiB). GTT is a ceiling, not a reservation, so the CPU can still use memory the GPU is not holding.

> **[RELATED]** Current and pending repo docs also include `amdgpu.sg_display=0` for display stability. Whether the reference unit's 2026-11-19 command line included it was **not recorded**. If you add it, keep the three tested values unchanged.

Apply the parameters in the bootloader the box actually uses (see [§3](#3-bootloader-specific-steps)). After regenerating the boot config, **reboot**, then verify:

```sh
cat /proc/cmdline
# must contain all three tokens

sudo dmesg | grep -i gtt
# should report about 15466M

cat /sys/module/ttm/parameters/pages_limit
# 3959290

awk '{printf "%.0f MiB\n", $1/1024/1024}' /sys/class/drm/card*/device/mem_info_gtt_total
# about 15466 MiB
```

**Practical ceiling:** model plus KV-cache size is still less than the GTT ceiling, because the CPU and OS need RAM too. Older install notes cited a practical ceiling of about 13 GiB; that figure was **not re-measured** against these 2026-11-19 values **[UNVERIFIED]**.

---

## 3. Bootloader-specific steps

Edit only the durable config file for your bootloader, then run the matching regenerate command. **Keep every existing root, resume, and LUKS option intact.** If the root filesystem is encrypted, dropping `rd.luks.uuid=<your-luks-uuid>` or `root=/dev/mapper/luks-<your-luks-uuid>` will make the box unable to find its root disk.

In the examples below, `<your-luks-uuid>` is a placeholder. Use the UUID already on your line. Never copy an example UUID from another machine.

### 3.1 GRUB (used on the reference unit)

Edit `/etc/default/grub` and append the three options inside `GRUB_CMDLINE_LINUX_DEFAULT`:

```sh
# /etc/default/grub (illustrative — keep existing tokens!)
GRUB_CMDLINE_LINUX_DEFAULT="quiet ttm.pages_limit=3959290 ttm.page_pool_size=3959290 amdgpu.gttsize=15466"
```

If the line already has other options (`quiet`, `amdgpu.sg_display=0`, a resume device, etc.), add the three tokens at the end of the same quoted string.

Then rebuild and reboot:

```sh
sudo grub-mkconfig -o /boot/grub/grub.cfg
# or equivalently on Debian-family systems:
# sudo update-grub
sudo reboot
```

### 3.2 Limine (CachyOS)

CachyOS often ships Limine. The durable file is `/etc/default/limine`, not the generated `/boot/limine.conf`.

**Preferred method.** Open `/etc/default/limine` and append the three options **inside the existing** `KERNEL_CMDLINE[default]` quotes:

```sh
# /etc/default/limine — before
ESP_PATH="/boot"
KERNEL_CMDLINE[default]+="quiet nowatchdog splash rw rootflags=subvol=/@ rd.luks.uuid=<your-luks-uuid> root=/dev/mapper/luks-<your-luks-uuid>"

# after
ESP_PATH="/boot"
KERNEL_CMDLINE[default]+=" quiet nowatchdog splash rw rootflags=subvol=/@ rd.luks.uuid=<your-luks-uuid> root=/dev/mapper/luks-<your-luks-uuid> ttm.pages_limit=3959290 ttm.page_pool_size=3959290 amdgpu.gttsize=15466"
```

Then regenerate and reboot:

```sh
sudo limine-update     # or: sudo limine-mkinitcpio
sudo reboot
```

**Fallback only,** if `/etc/default/limine` does not exist: append the three tokens to each `cmdline:` line in `/boot/limine.conf` or `/boot/efi/limine.conf`. This is temporary — the next kernel or Limine update will overwrite it. Create `/etc/default/limine` and run `sudo limine-update` as soon as you can.

### 3.3 systemd-boot (CachyOS) — untested on Pithos **[UNVERIFIED]**

On CachyOS, do **not** rely on editing `/boot/loader/entries/*.conf` or `/etc/kernel/cmdline` alone. `sdboot-manage` regenerates loader entries, and `/etc/kernel/cmdline` has been reported not to persist across kernel updates on CachyOS.

Edit `LINUX_OPTIONS=` in `/etc/sdboot-manage.conf`:

```sh
# /etc/sdboot-manage.conf (illustrative)
LINUX_OPTIONS="zswap.enabled=0 nowatchdog quiet splash ttm.pages_limit=3959290 ttm.page_pool_size=3959290 amdgpu.gttsize=15466"
```

Then regenerate entries and reboot:

```sh
sudo sdboot-manage gen
sudo reboot
```

On a generic Arch systemd-boot install (no `sdboot-manage`), the usual files are the `options` line in each `/boot/loader/entries/*.conf`, or `/etc/kernel/cmdline` where `kernel-install` is in use. Those paths are **[UNVERIFIED on Pithos]** and are not durable on CachyOS.

---

## 4. Superseded value: `4194304`

Older Pithos docs, and some community LLM guides, used:

```
ttm.pages_limit=4194304 ttm.page_pool_size=4194304
```

and said not to set `amdgpu.gttsize` because it was "deprecated." That combination is **wrong for this project** after the 512 MB UMA carve-out:

| Value | Meaning |
|---|---|
| `4 194 304` pages × 4 KiB | A full **16 GiB** of GTT — more than remains after the 512 MB carve-out |
| `3 959 290` pages × 4 KiB | **15 465.98 MiB**, the tested TTM limit (paired with `gttsize=15466`) |
| `amdgpu.gttsize=15466` | Matches that ceiling; part of the tested command line, not something to omit |

If you still see `4194304` in a checklist, in `/etc/default/grub`, in `/etc/default/limine`, in `/etc/modprobe.d/ttm-gpu-memory.conf`, or in `/etc/tmpfiles.d/gpu-ttm-memory.conf`, replace it with the tested values. Older notes also warned that a live `pages_limit` of `3 145 728` means a silent 12 GiB cap, often from tmpfiles.d applying last.

---

## 5. Troubleshooting

| Symptom | What to check |
|---|---|
| The three options are missing from `/proc/cmdline` after reboot | Wrong bootloader file was edited, a second `KERNEL_CMDLINE[default]` line overrode the first, or the regenerate command was skipped. On Limine, a direct edit of `/boot/limine.conf` may already have been overwritten. |
| `dmesg` does not show about `15466M` | Confirm all three options on the command line. Check `pages_limit` and `mem_info_gtt_total`. Look for leftover `4194304` or `3145728` in modprobe.d / tmpfiles.d. |
| UMA Frame Buffer Size is missing in setup | Set **Forced**, then **UMA_SPECIFIED**, then look again under Chipset → GFX Configuration. If still not there, use `bc250memcfg`. |
| BIOS settings do not stick after a flash | Clear CMOS, then set them again. |
| The box will not boot after a 2 GB UMA attempt | Clear CMOS, then set 512 MB (menu or `bc250memcfg`). |
| The box will not find its root disk after a cmdline edit | A LUKS or `root=` token was dropped. Restore it and regenerate. |
| `memcfg` split reverts to a small carve | A CMOS clear was done; re-run `sudo ./bc250memcfg UMA_SIZE 512` and reboot. |

---

## 6. Rollback

1. Remove `ttm.pages_limit=3959290 ttm.page_pool_size=3959290 amdgpu.gttsize=15466` from the same durable bootloader file you edited, leaving root and LUKS options untouched.
2. Regenerate (`grub-mkconfig`, `limine-update`, or `sdboot-manage gen`) and reboot.
3. To undo only the UMA split: set a different size in the BIOS menu, or run `bc250memcfg` with another supported value, or clear CMOS (this also resets other firmware settings).
4. Keep a copy of the pre-change bootloader file so you can restore it from a live USB if the box does not boot.

---

## See also

- [HARDWARE.md](../HARDWARE.md) — board overview and safety
- [ARCHITECTURE.md](../ARCHITECTURE.md) — how these parameters fit the BC-250 enablement layer
- [INSTALL-DEBIAN13.md](../INSTALL-DEBIAN13.md) — installation steps with condensed GPU memory settings
- [VRAM Configuration](https://elektricm.github.io/amd-bc250-docs/bios/vram/) and [BIOS flashing](https://elektricm.github.io/amd-bc250-docs/bios/flashing/) in the community BC-250 docs
- [CachyOS boot-manager configuration](https://wiki.cachyos.org/configuration/boot_manager_configuration/)
