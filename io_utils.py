import json
import csv
from pathlib import Path
from typing import List
from models import SystemState, Mode, Process, ResourceType, Event


def load_config(path: str) -> SystemState:
    """
    Lee config.json y construye un SystemState inicial.
    """
    p = Path(path)
    with p.open("r", encoding="utf-8") as f:
        raw = json.load(f)

    mode: Mode = raw.get("mode", "deteccion")
    victim_policy = raw.get("victim_policy", "menor_trabajo_hecho")
    detection_interval = int(raw.get("detection_interval", 1))

    state = SystemState(
        mode=mode,
        victim_policy=victim_policy,
        detection_interval=detection_interval,
    )

    # Procesos
    for proc in raw.get("processes", []):
        pid = proc["pid"]
        priority = int(proc.get("priority", 1))
        state.processes[pid] = Process(pid=pid, priority=priority)

    # Recursos
    for res in raw.get("resources", []):
        rid = res["rid"]
        total = int(res["instances"])
        state.resources[rid] = ResourceType(
            rid=rid,
            total_instances=total,
            available_instances=total,
        )

    return state


def load_events(path: str) -> List[Event]:
    """
    Carga la lista de eventos desde events.csv
    Columnas esperadas: type, process, resource, amount_or_time
    """
    events: List[Event] = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            etype = row["type"].strip().upper()
            pid = row["process"].strip()
            rid = row.get("resource", "") or None
            amount_or_time = int(row.get("amount_or_time", "0") or "0")
            events.append(
                Event(
                    type=etype,
                    process_id=pid,
                    resource_id=rid,
                    amount_or_time=amount_or_time,
                )
            )
    return events
