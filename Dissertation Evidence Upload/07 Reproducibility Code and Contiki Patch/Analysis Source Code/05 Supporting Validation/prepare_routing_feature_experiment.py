#!/usr/bin/env python3
"""Prepare isolated Cooja configs for the routing-aware feature milestone."""

from __future__ import annotations

import argparse
import re
import shutil
import xml.etree.ElementTree as ET
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
BLACKHOLE_FINAL = REPO / "experiments/90 Raw Reproducibility Workspace/blackhole/final_corrected_240s_540s"
SINKHOLE_FINAL = REPO / "experiments/90 Raw Reproducibility Workspace/sinkhole/final_corrected_240s_540s"
RPL_ICMP6 = Path("/Users/mizzy/contiki-ng/os/net/routing/rpl-lite/rpl-icmp6.c")


def copy_code(out_dir: Path) -> None:
    code_dir = out_dir / "code"
    code_dir.mkdir(parents=True, exist_ok=True)
    sources = {
        "udp-client.c": SINKHOLE_FINAL / "code/udp-client.c",
        "udp-server.c": SINKHOLE_FINAL / "code/udp-server.c",
        "blackhole-router.c": BLACKHOLE_FINAL / "code/blackhole-router.c",
        "control-router.c": BLACKHOLE_FINAL / "code/control-router.c",
        "sinkhole-router.c": SINKHOLE_FINAL / "code/sinkhole-router.c",
        "sinkhole-control-router.c": SINKHOLE_FINAL / "code/sinkhole-control-router.c",
        "uip6_blackhole_modified.c": BLACKHOLE_FINAL / "code/uip6_blackhole_modified.c",
        "rpl-icmp6_snapshot.c": RPL_ICMP6,
    }
    for name, source in sources.items():
        if not source.is_file():
            raise FileNotFoundError(source)
        shutil.copy2(source, code_dir / name)

    # Cooja loads mote firmware as shared libraries. A weak-only definition can
    # be interposed by another mote type, so give each router firmware its own
    # strong flag while retaining the shared-variable hook contract.
    for name in ("sinkhole-router.c", "sinkhole-control-router.c"):
        path = code_dir / name
        text = path.read_text(encoding="utf-8")
        marker = "extern int sinkhole_attack_enabled;"
        if marker not in text:
            raise ValueError(f"Missing sinkhole flag declaration in {path}")
        path.write_text(
            text.replace(marker, "int sinkhole_attack_enabled = 0;", 1),
            encoding="utf-8",
        )

    (code_dir / "Makefile").write_text(
        "CONTIKI=/Users/mizzy/contiki-ng\n\n"
        "MAKE_ROUTING = MAKE_ROUTING_RPL_LITE\n\n"
        "# Generic routing telemetry; attack markers remain excluded from ML features.\n"
        "CFLAGS += -DLOG_CONF_LEVEL_RPL=LOG_LEVEL_INFO\n\n"
        "include $(CONTIKI)/Makefile.include\n",
        encoding="utf-8",
    )


def replace_required(text: str, old: str, new: str, source: Path) -> str:
    if old not in text:
        raise ValueError(f"Expected text {old!r} in {source}")
    return text.replace(old, new)


def prepare_config(source: Path, destination: Path) -> None:
    text = source.read_text(encoding="utf-8")
    text = replace_required(text, "<speedlimit>1.0</speedlimit>", "<speedlimit>null</speedlimit>", source)
    text = re.sub(r"<title>(.*?)</title>", r"<title>RF \1</title>", text, count=1)
    text = text.replace(
        "[CONTIKI_DIR]/examples/rpl-udp/udp-server.c",
        "[CONFIG_DIR]/../code/udp-server.c",
    )
    text = text.replace(
        "[CONTIKI_DIR]/examples/rpl-udp/udp-client.c",
        "[CONFIG_DIR]/../code/udp-client.c",
    )
    text = text.replace("[CONFIG_DIR]/blackhole-router.c", "[CONFIG_DIR]/../code/blackhole-router.c")
    text = text.replace("[CONFIG_DIR]/control-router.c", "[CONFIG_DIR]/../code/control-router.c")
    text = text.replace("$(MAKE) -j$(CPUS)", "/usr/local/bin/gmake -j$(CPUS)")

    if "[CONTIKI_DIR]/examples/rpl-udp" in text or "[CONFIG_DIR]/blackhole-router.c" in text:
        raise ValueError(f"Unconverted source path in {source}")
    ET.fromstring(text)
    destination.write_text(text, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path("experiments/90 Raw Reproducibility Workspace/routing_features_v1"),
    )
    args = parser.parse_args()

    copy_code(args.out_dir)
    config_dir = args.out_dir / "configs"
    config_dir.mkdir(parents=True, exist_ok=True)
    configs = sorted((BLACKHOLE_FINAL / "configs").glob("*.csc"))
    configs += sorted((SINKHOLE_FINAL / "configs").glob("*.csc"))
    if len(configs) != 20:
        raise ValueError(f"Expected 20 final configs; found {len(configs)}")
    for source in configs:
        prepare_config(source, config_dir / source.name)

    (args.out_dir / "runs").mkdir(parents=True, exist_ok=True)
    (args.out_dir / "README.md").write_text(
        "# Routing-Aware Cooja Milestone\n\n"
        "This package reuses the validated 16-node blackhole and sinkhole topologies, "
        "five seeds, 240-second activation and 540-second duration. It does not modify "
        "the preserved final evidence packages.\n\n"
        "The only simulation-setting change is `LOG_CONF_LEVEL_RPL=LOG_LEVEL_INFO`, "
        "which exposes Contiki-NG's generic DIO rank, parent-switch, DIS and DAO logs. "
        "The sinkhole router firmware also provides a strong flag definition to prevent "
        "Cooja shared-library weak-symbol interposition; the RPL hook remains unchanged. "
        "Explicit attack markers are retained for validation but excluded from IDS features.\n",
        encoding="utf-8",
    )
    print(f"Prepared {len(configs)} configs in {args.out_dir}")


if __name__ == "__main__":
    main()
