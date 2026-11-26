#!/bin/sh
### BEGIN /etc/grub.d/pithos-mode-switcher
# Pithos GRUB mode switcher — one menuentry per Pithos deployment mode.
# Install on the box: copy to /etc/grub.d/30_pithos-mode-switcher, chmod +x,
# then `grub-mkconfig -o <your grub.cfg>`.
#
# Contract (docs/CLI-SPEC.md "pithos-mode", docs/ARCHITECTURE.md "Mode
# Switching"): the menuentry titles below exactly match what `pithos-mode`
# passes to `grub-reboot`, and each entry passes `systemd.unit=<target>`
# on the kernel command line so systemd isolates the right target at boot.

set -u

# Kernel path resolution is overridable so the generator can be tested
# off-box without touching the real /boot.
BOOT_DIR=${BOOT_DIR:-/boot}

LINUX_IMAGE=$(ls -1 "$BOOT_DIR"/vmlinuz-* 2>/dev/null | sort -V | tail -n 1)
INITRD_IMAGE=$(ls -1 "$BOOT_DIR"/initrd.img-* "$BOOT_DIR"/initrd*-* 2>/dev/null | sort -V | tail -n 1)

if [ -z "$LINUX_IMAGE" ]; then
    echo "pithos-mode-switcher: no kernel found in $BOOT_DIR; skipping" >&2
    exit 1
fi

INITRD_LINE=""
if [ -n "$INITRD_IMAGE" ]; then
    INITRD_LINE="    initrd $INITRD_IMAGE"
fi

# AMD GTT sizing for the BC250 box (docs/hardware/BC250-GPU-MEMORY.md):
# cap the amdgpu GEM TTM pool so big-model workloads get VRAM headroom.
AMDGPU_OPTS="amdgpu.sg_display=0 ttm.pages_limit=4194304 ttm.page_pool_size=4194304"

# grub-mkconfig exports these into the generator's environment.
CMDLINE="${GRUB_CMDLINE_LINUX_DEFAULT:-} ${GRUB_CMDLINE_LINUX:-} ${AMDGPU_OPTS}"

cat <<EOF
menuentry 'graphical.target' --class pithos --class desktop {
    linux $LINUX_IMAGE root=UUID=\${root} ro $CMDLINE systemd.unit=graphical.target
$INITRD_LINE
}

menuentry 'pithos-server.target' --class pithos {
    linux $LINUX_IMAGE root=UUID=\${root} ro $CMDLINE systemd.unit=pithos-server.target
$INITRD_LINE
}

menuentry 'pithos-cluster.target' --class pithos {
    linux $LINUX_IMAGE root=UUID=\${root} ro $CMDLINE systemd.unit=pithos-cluster.target
$INITRD_LINE
}
EOF
### END /etc/grub.d/pithos-mode-switcher
