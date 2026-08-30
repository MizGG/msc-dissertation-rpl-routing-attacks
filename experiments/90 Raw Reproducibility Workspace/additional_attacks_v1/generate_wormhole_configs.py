#!/usr/bin/env python3
"""Generate a two-endpoint Cooja wormhole experiment using DGRM links."""

from __future__ import annotations

import copy
import math
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parent
CONFIG_DIR = ROOT / "configs"
SEEDS = ("123456", "234567", "345678", "456789", "567890")
RANGE = 65.0
DGRM = "org.contikios.cooja.radiomediums.DirectedGraphMedium"
DEST = "org.contikios.cooja.radiomediums.DGRMDestinationRadio"


def mote_id_and_position(mote: ET.Element) -> tuple[int, float, float]:
    mote_id = None
    position = None
    for config in mote.findall("interface_config"):
        name = (config.text or "").strip()
        if name == "org.contikios.cooja.contikimote.interfaces.ContikiMoteID":
            mote_id = int(config.findtext("id", ""))
        if name == "org.contikios.cooja.interfaces.Position":
            position = config.find("pos")
    if mote_id is None or position is None:
        raise ValueError("Mote is missing ID or position")
    return mote_id, float(position.attrib["x"]), float(position.attrib["y"])


def append_edge(medium: ET.Element, source: int, destination: int) -> None:
    edge = ET.SubElement(medium, "edge")
    ET.SubElement(edge, "source").text = str(source)
    dest = ET.SubElement(edge, "dest")
    dest.text = DEST
    ET.SubElement(dest, "radio").text = str(destination)
    ET.SubElement(dest, "ratio").text = "1.0"
    ET.SubElement(dest, "signal").text = "-10.0"
    ET.SubElement(dest, "lqi").text = "105"
    ET.SubElement(dest, "delay").text = "0"
    ET.SubElement(dest, "channel").text = "-1"


def add_wormhole_script(script: str) -> str:
    setup = """
var wormholeEnabled = false;
var DirectedGraphMedium = Java.type(\"org.contikios.cooja.radiomediums.DirectedGraphMedium\");
var DGRMDestinationRadio = Java.type(\"org.contikios.cooja.radiomediums.DGRMDestinationRadio\");
"""
    loop = """
  if (!wormholeEnabled && time >= 240000000) {
    var leftRadio = sim.getMoteWithID(16).getInterfaces().getRadio();
    var rightRadio = sim.getMoteWithID(17).getInterfaces().getRadio();
    var medium = sim.getRadioMedium();
    medium.addEdge(new DirectedGraphMedium.Edge(leftRadio, new DGRMDestinationRadio(rightRadio)));
    medium.addEdge(new DirectedGraphMedium.Edge(rightRadio, new DGRMDestinationRadio(leftRadio)));
    wormholeEnabled = true;
    log.log(formatTime(time) + \"\\tWORMHOLE ATTACK: tunnel enabled between 16 and 17\\n\");
  }
"""
    if "while (true) {" not in script:
        raise ValueError("Could not find Cooja script loop")
    return script.replace("while (true) {", setup + "\nwhile (true) {\n" + loop, 1)


def generate(seed: str, attack: bool) -> None:
    source = CONFIG_DIR / f"DIO_SUPPRESSION_CONTROL_N16_SEED{seed}.csc"
    tree = ET.parse(source)
    root = tree.getroot()
    simulation = root.find("simulation")
    assert simulation is not None
    family = "WORMHOLE_ATTACK" if attack else "WORMHOLE_CONTROL"
    simulation.find("title").text = f"{family} N17 SEED{seed}"

    attacker_type = next(
        mote_type for mote_type in simulation.findall("motetype")
        if "dio-suppression-control-router.c" in (mote_type.findtext("source") or "")
    )
    attacker_type.find("description").text = "wormhole endpoint routers"
    attacker_type.find("source").text = "[CONFIG_DIR]/../code/wormhole-router.c"
    attacker_type.find("commands").text = "/usr/local/bin/gmake -j$(CPUS) wormhole-router.cooja TARGET=cooja"
    second = copy.deepcopy(attacker_type.find("mote"))
    for config in second.findall("interface_config"):
        name = (config.text or "").strip()
        if name == "org.contikios.cooja.interfaces.Position":
            config.find("pos").attrib.update({"x": "205", "y": "75"})
        if name == "org.contikios.cooja.contikimote.interfaces.ContikiMoteID":
            config.find("id").text = "17"
    attacker_type.append(second)

    medium = simulation.find("radiomedium")
    assert medium is not None
    medium.clear()
    medium.text = DGRM
    motes = [mote_id_and_position(mote) for mote_type in simulation.findall("motetype") for mote in mote_type.findall("mote")]
    for source_id, source_x, source_y in motes:
        for destination_id, destination_x, destination_y in motes:
            if source_id == destination_id:
                continue
            if math.hypot(source_x - destination_x, source_y - destination_y) <= RANGE:
                append_edge(medium, source_id, destination_id)

    if attack:
        runner = next(plugin for plugin in root.findall("plugin") if "ScriptRunner" in (plugin.text or ""))
        script = runner.find("plugin_config/script")
        assert script is not None and script.text is not None
        script.text = add_wormhole_script(script.text)

    tree.write(CONFIG_DIR / f"{family}_N17_SEED{seed}.csc", encoding="utf-8", xml_declaration=True)


for seed_value in SEEDS:
    generate(seed_value, attack=True)
    generate(seed_value, attack=False)
