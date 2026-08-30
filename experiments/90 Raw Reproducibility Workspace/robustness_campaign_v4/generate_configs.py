#!/usr/bin/env python3
"""Generate isolated layout and radio-sensitivity Cooja configurations."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "configs"
REPOSITORY = ROOT.parents[1]
SEEDS = ("123456", "234567", "345678", "456789", "567890")
FAMILIES = {
    "blackhole": {
        "prefix": "BH",
        "template": REPOSITORY / "experiments/blackhole/final_corrected_240s_540s/configs/BH_{mode}_N16_SEED{seed}.csc",
        "attack_source": "../code/blackhole/blackhole-router.c",
        "control_source": "../code/blackhole/control-router.c",
    },
    "sinkhole": {
        "prefix": "SH",
        "template": REPOSITORY / "experiments/sinkhole/final_corrected_240s_540s/configs/SH_{mode}_N16_SEED{seed}.csc",
        "attack_source": "../code/sinkhole/sinkhole-router.c",
        "control_source": "../code/sinkhole/sinkhole-control-router.c",
    },
    "sybil": {
        "prefix": "SYBIL",
        "template": REPOSITORY / "experiments/sybil_attack_v1/configs/SYBIL_{mode}_N16_SEED{seed}.csc",
        "attack_source": "../code/sybil/sybil-router.c",
        "control_source": "../code/sybil/sybil-control-router.c",
    },
}
CONDITIONS = {
    "attacker_relocated": {"position": (80, 75), "rx": "1.0"},
    "lossy_radio": {"position": (65, 75), "rx": "0.85"},
}


def replace_attacker_source(text: str, family: str, mode: str) -> str:
    source = FAMILIES[family]["attack_source" if mode == "ATTACK" else "control_source"]
    if family == "blackhole":
        old = "[CONFIG_DIR]/blackhole-router.c" if mode == "ATTACK" else "[CONFIG_DIR]/control-router.c"
    elif family == "sinkhole":
        old = "[CONFIG_DIR]/../code/sinkhole-router.c" if mode == "ATTACK" else "[CONFIG_DIR]/../code/sinkhole-control-router.c"
    else:
        old = "[CONFIG_DIR]/../code/sybil-router.c" if mode == "ATTACK" else "[CONFIG_DIR]/../code/sybil-control-router.c"
    return text.replace(old, f"[CONFIG_DIR]/{source}")


def replace_common_sources(text: str) -> str:
    return (text
            .replace("[CONFIG_DIR]/../code/udp-server.c", "[CONFIG_DIR]/../code/server/udp-server.c")
            .replace("[CONFIG_DIR]/../code/udp-client.c", "[CONFIG_DIR]/../code/client/udp-client.c"))


def enable_rpl_telemetry(text: str) -> str:
    # The per-application Makefiles define telemetry. Passing CFLAGS through
    # the Cooja command line would replace Contiki's generated include flags.
    return text


def change_attacker_position(text: str, x: int, y: int) -> str:
    old = '<pos x="65" y="75" />'
    if old not in text:
        raise ValueError("Expected node 16 baseline position not found")
    return text.replace(old, f'<pos x="{x}" y="{y}" />', 1)


def generate() -> None:
    OUTPUT.mkdir(exist_ok=True)
    for condition, settings in CONDITIONS.items():
        for family, config in FAMILIES.items():
            for mode in ("ATTACK", "CONTROL"):
                for seed in SEEDS:
                    template = Path(str(config["template"]).format(mode=mode, seed=seed))
                    text = template.read_text(encoding="utf-8")
                    title = f"ROBUST_{condition.upper()}_{config['prefix']}_{mode}_N16_SEED{seed}"
                    text = text.replace(f"{config['prefix']} {mode} N16 SEED{seed}", title)
                    text = enable_rpl_telemetry(replace_common_sources(replace_attacker_source(text, family, mode)))
                    text = text.replace("<success_ratio_rx>1.0</success_ratio_rx>", f"<success_ratio_rx>{settings['rx']}</success_ratio_rx>")
                    text = text.replace("TIMEOUT(540000);", "TIMEOUT(541000);")
                    text = change_attacker_position(text, *settings["position"])
                    output = OUTPUT / f"{condition.upper()}_{config['prefix']}_{mode}_N16_SEED{seed}.csc"
                    output.write_text(text, encoding="utf-8")
                    if "[CONFIG_DIR]/../code/udp-server.c" in text or "[CONFIG_DIR]/../code/udp-client.c" in text:
                        raise ValueError(f"Unrewritten source in {output.name}")


if __name__ == "__main__":
    generate()
