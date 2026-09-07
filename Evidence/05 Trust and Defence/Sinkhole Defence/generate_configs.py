#!/usr/bin/env python3
"""Generate isolated control, Sinkhole, and Sinkhole-defence Cooja configs."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parent
REPOSITORY = ROOT.parents[1]
SEEDS = ("123456", "234567", "345678", "456789", "567890")


def sources(text: str, mode: str) -> str:
    client = "client_defence" if mode == "DEFENCE" else "client"
    router = "sinkhole-control-router.c" if mode == "CONTROL" else "sinkhole-router.c"
    return (text
            .replace("[CONFIG_DIR]/../code/udp-server.c", "[CONFIG_DIR]/../code/server/udp-server.c")
            .replace("[CONFIG_DIR]/../code/udp-client.c", f"[CONFIG_DIR]/../code/{client}/udp-client.c")
            .replace("[CONFIG_DIR]/../code/sinkhole-router.c", f"[CONFIG_DIR]/../code/sinkhole/{router}")
            .replace("[CONFIG_DIR]/../code/sinkhole-control-router.c", f"[CONFIG_DIR]/../code/sinkhole/{router}"))


def generate() -> None:
    output = ROOT / "configs"
    output.mkdir(exist_ok=True)
    for mode in ("CONTROL", "ATTACK", "DEFENCE"):
        template_mode = "CONTROL" if mode == "CONTROL" else "ATTACK"
        for seed in SEEDS:
            template = REPOSITORY / f"experiments/routing_features_v1/configs/SH_{template_mode}_N16_SEED{seed}.csc"
            text = template.read_text(encoding="utf-8")
            text = text.replace(f"SH {template_mode} N16 SEED{seed}", f"SINKHOLE {mode} N16 SEED{seed}")
            text = sources(text, mode).replace("TIMEOUT(540000);", "TIMEOUT(541000);")
            (output / f"SH_{mode}_N16_SEED{seed}.csc").write_text(text, encoding="utf-8")


if __name__ == "__main__":
    generate()
