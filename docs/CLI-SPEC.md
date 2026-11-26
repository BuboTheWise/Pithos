# Pithos CLI Specification

This document specifies the **Pithos CLI** command family and their integration with on-box Hermes and Project N.O.M.A.D.

## Scope

The `pithos` command line tool provides idempotent utilities for deploying, verifying, and configuring Pithos systems. Each command is documented below with exact invocations, flags, and exit codes.

This spec covers **docs only** — implementation (shell scripts, systemd units, binaries) belongs to later cards.

## Command Family Overview

| Command | Purpose |
|---------|---------|
| `pithos-install` | Idempotent installer for INSTALL steps 3-8 |
| `pithos-check` | System verification script with pass/fail reporting |
| `pithos-mode` | Switch between desktop/server/cluster modes |
| `pithos-archive` | Fetch, hash and record model provenance (out of scope per issue #17) |

> **Note on `pithos-archive`:** Model management is handled by N.O.M.A.D./Ollama upstream. Per comment from worker cthugha when completing this card, `pithos-archive` is explicitly out of scope for this spec. The command exists in the family naming but is not documented here; it should be addressed separately if adopted upstream.

---

## 1. pithos-install

**Purpose:** Idempotent installer for INSTALL steps 3-8: BC-250 enablement, Ollama Vulkan backend, N.O.M.A.D. container preparation, systemd targets and services.

**Invocation:**
```bash
pithos-install [OPTIONS]
```

**Options:**

| Option | Description | Default |
|--------|-------------|---------|
| `--dry-run` | Show what would be installed without making changes | `false` |
| `--force` | Skip checks and overwrite existing config (use with caution) | `false` |
| `-h`, `--help` | Print usage information | — |

**Exit Codes:**

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Dry-run mode; changes printed but not applied |
| 2 | Validation failed (missing dependencies, broken config); use `--force` to override or investigate |
| >2 | Unexpected error; check stderr for details |

**Behavior:**

- Calls the **stock N.O.M.A.D. installer** (`install_nomad.sh`) unmodified after preparing `/opt/project-nomad/storage`.
- Writes systemd units and config files idempotently (detects existing state before writing).
- The file writer uses atomic writes to avoid partial configs.
- Re-runs are safe; the command detects what's installed and only updates missing components.

**Dry-run behavior:** In `--dry-run` mode, prints each action prefixed with `[DRY-RUN]` and exits with code 1. No files are modified.

**Force flag:** With `--force`, skips validation checks and proceeds with installation even if prerequisites fail or partial config exists. This is for recovery scenarios only.

---

## 2. pithos-check

**Purpose:** Verification script that checks the essential components of a Pithos system: kernel, RADV support, GTT settings, GPU governor, Ollama Vulkan backend, and N.O.M.A.D. containers.

**Invocation:**
```bash
pithos-check [OPTIONS]
```

**Options:**

| Option | Description | Default |
|--------|-------------|---------|
| `-h`, `--help` | Print usage information | — |
| `--details` | Show detailed per-check output with timestamps | `false` |

**Exit Codes:**

| Code | Meaning |
|------|---------|
| 0 | All checks passed |
| 1 | One or more checks failed (see below) |
| 2 | Script error (not a validation failure) |

**Checks Performed:**

The script performs the following checks in order. Each check prints its result line, and all results are summarized at the end:

1. **Kernel**: Running kernel is Debian 13 trixie with backports (`trixie-backports`)
2. **RADV**: `radv` driver is loaded; `/dev/dri/radeon` exists
3. **GTT**: GTT settings verified (pages_limit=8162647, page_pool_size=0 for BC-250)
4. **Governor**: GPU governor `cyan-skillfish-governor-smu` is active
5. **Ollama Vulkan**: Ollama process running with Vulkan backend (`/dev/dri` mounted or equivalent)
6. **N.O.M.A.D. containers**: Docker/Podman container for N.O.M.A.D. is running on port 8080

**Output Format:**

Each check prints a line: `[PASS]` or `[FAIL] <check name> — <reason>`

Example output:
```
[PASS] kernel — Debian 13 trixie-backports running (7.2.11)
[PASS] radv — /dev/dri/radeon found; driver loaded
[PASS] gtt — pages_limit=8162647, page_pool_size=0
[PASS] governor — cyan-skillfish-governor-smu active
[PASS] ollama-vulkan — Ollama running with Vulkan backend
[FAIL] nomad-containers — N.O.M.A.D. container not running on 8080
=========================================
SUMMARY: 5/6 checks passed, 1 failed
=========================================
```

The script returns exit code 1 if any check fails, 0 only if all pass.

---

## 3. pithos-mode

**Purpose:** Switch between desktop/server/cluster modes via GRUB + systemd isolate. Changes the runtime role of the system.

**Invocation:**
```bash
pithos-mode <MODE> [--once]
```

**Arguments:**

| Argument | Description | Values |
|----------|-------------|--------|
| `<MODE>` | Target mode to switch to | `desktop`, `server`, `cluster` |

**Options:**

| Option | Description | Default |
|--------|-------------|---------|
| `-h`, `--help` | Print usage information | — |
| `--once` | Reboot into the new mode without persisting; GRUB entry applied for one boot only | `false` |

**Modes:**

| Mode | Systemd Target | Description |
|------|----------------|-------------|
| desktop | `graphical.target` (XFCE) | Light GUI, Ollama with small model, N.O.M.A.D., optional Steam |
| server | `pithos-server.target` | Ollama with big model (`pithos-ollama-big.service`), N.O.M.A.D., no display manager |
| cluster | `pithos-cluster.target` | llama-server (head) or ggml-rpc-server (worker); Ollama stopped to free GPU memory |

**Exit Codes:**

| Code | Meaning |
|------|---------|
| 0 | Mode switch requested successfully; rebooting or GRUB entry prepared |
| 1 | Invalid mode argument or GRUB/systemd operation failed |

**Behavior:**

- Uses `grub-reboot` to set the next boot target.
- Optionally reboots immediately via `systemctl isolate`.
- The `--once` flag applies a one-shot change; after reboot, the mode resets to the default (desktop) unless persisted elsewhere.
- Without `--once`, sets up a persistent GRUB entry so the mode persists across reboots.

**Example usage:**
```bash
# Switch to server mode persistently
pithos-mode server

# One-shot switch to cluster, then reboot back to desktop
pithos-mode cluster --once
```

---

## 4. Out of Scope for This Spec

The following items are explicitly out of scope for this documentation-only spec card:

1. **Shell scripts and systemd units**: These belong to implementation cards (M2/M3 milestones).
2. **Binary CLI tool**: The actual `pithos` binary/runner is implemented later; this doc describes its API only.
3. **`pithos-archive` command**: Model fetch, hashing and verification is handled by N.O.M.A.D./Ollama upstream per issue #17. This command does not exist in the spec.
4. **nftables firewall configuration**: Profile for Ollama/N.O.M.A.D. LAN-only access (issue #6) belongs to deployment docs, not CLI spec.
5. **Cluster networking and RPC setup**: Detailed cluster topology, binding interfaces, and security policies are covered by llama.cpp RPC docs and Pithos architecture docs.

---

## On-Box Hermes Integration

Hermes is installed and configured on every box during the `pithos-install` phase:

### Installation Steps (performed by pithos-install)

1. Clone Hermes into `/opt/hermes` (or user-specified directory).
2. Point Hermes at host Ollama via environment variable or config:
   ```bash
   export HERMES_OLLAMA_HOST=http://<BOX_LAN_IP>:11434
   ```
   Replace `<BOX_LAN_IP>` with the box's LAN address (RFC1918).

### Configuration per Mode

| Mode | Hermes Behavior |
|------|-----------------|
| desktop | Runs as a local service; points to localhost Ollama (`http://localhost:11434`) |
| server | Runs as a LAN-facing service on port 8080; remote clients connect via `http://<BOX_LAN_IP>:8080` |
| cluster | Hermes runs on the head node's Ollama endpoint; workers use llama.cpp RPC for model sharing |

### N.O.M.A.D. Integration

- **No fork:** Pithos uses the pristine upstream Project N.O.M.A.D. compose template from `Crosstalk-Solutions/project-nomad`.
- **Override mechanism:** Pithos applies a small override file (e.g., `pithos-config.json`) that sets:
  - The AI Assistant remote Ollama URL to `http://<BOX_LAN_IP>:11434`
  - Prepares the content disk mount at `/opt/project-nomad/storage`
- **Docker wait:** N.O.M.A.D. is configured to wait for the content disk before starting services.

This override approach avoids maintaining a N.O.M.A.D. fork while allowing Pithos-specific configuration.

---

## References

- [Pithos Architecture](ARCHITECTURE.md) — Layered design and component relationships
- [Pithos Backlog](BACKLOG.md) — Issue list mapping CLI commands to milestones
- [INSTALL-DEBIAN13](INSTALL-DEBIAN13.md) — Base system preparation steps

---

## Version

This spec is version 0.1.0 (documentation-only, implementation pending).
