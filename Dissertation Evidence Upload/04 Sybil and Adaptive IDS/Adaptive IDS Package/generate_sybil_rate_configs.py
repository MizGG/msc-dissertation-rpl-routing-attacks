#!/usr/bin/env python3
"""Generate separate Cooja configurations for prepared Sybil rate variants."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parent
TEMPLATE_DIR = ROOT.parent / "sybil_attack_v1" / "configs"
OUTPUT_DIR = ROOT / "configs"
SEEDS = ("123456", "234567", "345678", "456789", "567890")
VARIANTS = {
    "LOW_RATE": "sybil-low-rate-router",
    "HIGH_RATE": "sybil-high-rate-router",
}


def generate() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    for variant, attack_source in VARIANTS.items():
        for seed in SEEDS:
            for mode in ("ATTACK", "CONTROL"):
                template = TEMPLATE_DIR / f"SYBIL_{mode}_N16_SEED{seed}.csc"
                source_name = attack_source if mode == "ATTACK" else "sybil-rate-control-router"
                text = template.read_text(encoding="utf-8")
                text = text.replace(f"SYBIL {mode} N16 SEED{seed}", f"SYBIL {variant} {mode} N16 SEED{seed}")
                text = text.replace("sybil router", source_name.replace("-", " "))
                text = text.replace("sybil control router", source_name.replace("-", " "))
                text = text.replace("sybil-router.c", f"{source_name}.c")
                text = text.replace("sybil-control-router.c", f"{source_name}.c")
                (OUTPUT_DIR / f"SYBIL_{variant}_{mode}_N16_SEED{seed}.csc").write_text(text, encoding="utf-8")


if __name__ == "__main__":
    generate()
