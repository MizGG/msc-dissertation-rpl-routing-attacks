#!/usr/bin/env python3
"""Generate Sybil attack/control Cooja configs from the validated 16-mote layout."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parent
TEMPLATE_DIR = ROOT.parent / "routing_features_v1" / "configs"
OUTPUT_DIR = ROOT / "configs"
SEEDS = ("123456", "234567", "345678", "456789", "567890")


def replace_router_type(text: str, source_name: str) -> str:
    text = text.replace("sinkhole advertising router", source_name.replace("-", " "))
    text = text.replace("sinkhole control router", source_name.replace("-", " "))
    text = text.replace("sinkhole-router.c", f"{source_name}.c")
    text = text.replace("sinkhole-control-router.c", f"{source_name}.c")
    return text


def generate() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    for seed in SEEDS:
        for mode, source_name in (("ATTACK", "sybil-router"), ("CONTROL", "sybil-control-router")):
            template = TEMPLATE_DIR / f"SH_{mode}_N16_SEED{seed}.csc"
            text = template.read_text(encoding="utf-8")
            text = text.replace(f"RF SH {mode} N16 SEED{seed}", f"SYBIL {mode} N16 SEED{seed}")
            text = text.replace("[CONFIG_DIR]/../code/udp-server.c", "[CONTIKI_DIR]/examples/rpl-udp/udp-server.c")
            text = text.replace("[CONFIG_DIR]/../code/udp-client.c", "[CONTIKI_DIR]/examples/rpl-udp/udp-client.c")
            text = replace_router_type(text, source_name)
            (OUTPUT_DIR / f"SYBIL_{mode}_N16_SEED{seed}.csc").write_text(text, encoding="utf-8")


if __name__ == "__main__":
    generate()
