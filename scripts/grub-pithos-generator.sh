#!/bin/sh
### BEGIN /etc/grub.d/pithos-mode-switcher
# Pithos GRUB Mode Switcher - generates menu entries for desktop/server/cluster modes
# Copied by pithos-mode CLI to /etc/grub.d/pithos-mode-switcher

# Generate boot entry for server mode
cat <<'SERVER'
set timeout=${TIMEOUT:-10}
menuentry 'Pithos Server (Ollama Big Model)' '\\efi/boot/grub/grub.cfg' {
    load_video
    if [ x$feature_platform_search_handler = xtrue ]; then
        set platform_search_default=true;
    else
        set platform_search_default=false;
    fi
    search --no-floppy --fs-lostfound --file --set=root --label 'Pithos Server' || true
    configfile \\${linux}/\\boot/grub/grub.cfg
}
SERVER

# Generate boot entry for cluster mode  
cat <<'CLUSTER'
menuentry 'Pithos Cluster (LLaMa Server/Worker)' '\\efi/boot/grub/grub.cfg' {
    load_video
    if [ x$feature_platform_search_handler = xtrue ]; then
        set platform_search_default=true;
    else
        set platform_search_default=false;
    fi
    search --no-floppy --fs-lostfound --file --set=root --label 'Pithos Cluster' || true
    configfile \\${linux}/\\boot/grub/grub.cfg
}
CLUSTER

# Generate boot entry for default desktop mode
cat <<'DESKTOP'
menuentry 'Pithos Default (Desktop)' '\\efi/boot/grub/grub.cfg' {
    load_video
    if [ x$feature_platform_search_handler = xtrue ]; then
        set platform_search_default=true;
    else
        set platform_search_default=false;
    fi
    search --no-floppy --fs-lostfound --file --set=root --label 'Pithos Default' || true
    configfile \\${linux}/\\boot/grub/grub.cfg
}
DESKTOP

# Set kernel command line for selected mode based on pithos.mode GRUB parameter
if [ -n "${GRUB_CMDLINE_LINUX}" ]; then
    echo "linux /boot/vmlinuz-$(uname -r) ${GRUB_CMDLINE_LINUX} amdgpu.sg_display=0 ttm.pages_limit=4194304 ttm.page_pool_size=4194304"
elif [ -n "${pithos.mode}" ]; then
    if [ "$pithos.mode" = "server" ]; then
        echo "linux /boot/vmlinuz-$(uname -r) quiet root=UUID=\\${root} ro pithos.mode=pithos-server.target amdgpu.sg_display=0 ttm.pages_limit=4194304 ttm.page_pool_size=4194304"
    elif [ "$pithos.mode" = "cluster" ]; then
        echo "linux /boot/vmlinuz-$(uname -r) quiet root=UUID=\\${root} ro pithos.mode=pithos-cluster.target amdgpu.sg_display=0 ttm.pages_limit=4194304 ttm.page_pool_size=4194304"
    else
        echo "linux /boot/vmlinuz-$(uname -r) quiet root=UUID=\\${root} ro pithos.mode=pithos-desktop.graphical.target amdgpu.sg_display=0 ttm.pages_limit=4194304 ttm.page_pool_size=4194304"
    fi
else
    echo "linux /boot/vmlinuz-$(uname -r) quiet root=UUID=\\${root} ro amdgpu.sg_display=0 ttm.pages_limit=4194304 ttm.page_pool_size=4194304"
fi

echo "initrd /boot/initrd.img-$(uname -r)"
echo "boot"
### END /etc/grub.d/pithos-mode-switcher

# Add pithos.mode to GRUB_CMDLINE_LINUX_DEFAULT for persistence (only if not already present)
pithos_mode_default="${GRUB_CMDLINE_LINUX_DEFAULT:-quiet}"
if ! echo "$pithos_mode_default" | grep -q "pithos.mode"; then
    new_default="${pithos_mode_default} pithos.mode=desktop"
    sed -i '/^GRUB_CMDLINE_LINUX_DEFAULT.*$/!{s/$/ pithos.mode=desktop/;}' /etc/default/grub 2>/dev/null || \
    echo "GRUB_CMDLINE_LINUX_DEFAULT=\"${new_default}\"" >> /etc/default/grub
fi

echo "Pithos GRUB mode switcher ready for pithos-mode CLI integration"
