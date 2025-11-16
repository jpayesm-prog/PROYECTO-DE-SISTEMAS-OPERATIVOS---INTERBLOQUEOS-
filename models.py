from dataclasses import dataclass, field
from typing import Dict, List, Optional, Literal, Tuple, Set

# Modo de trabajo del sistema
Mode = Literal["prevencion", "deteccion"]


@dataclass
class Process:
    pid: str
    priority: int = 1  # menor número = mayor prioridad (por ejemplo)
    work_done: int = 0  # ticks de CPU completados (para políticas de víctima)


@dataclass
class ResourceType:
    rid: str
    total_instances: int
    available_instances: int


@dataclass
class Event:
    """
    type: REQUEST, RELEASE o COMPUTE
    process_id: proceso que genera el evento
    resource_id: recurso (solo para REQUEST/RELEASE)
    amount_or_time: unidades a pedir/liberar o tiempo de COMPUTE
    """
    type: Literal["REQUEST", "RELEASE", "COMPUTE"]
    process_id: str
    resource_id: Optional[str] = None
    amount_or_time: int = 0


@dataclass
class SystemState:
    """
    Representa el estado completo del sistema en un tick dado.
    """
    mode: Mode
    victim_policy: str
    detection_interval: int = 1

    processes: Dict[str, Process] = field(default_factory=dict)
    resources: Dict[str, ResourceType] = field(default_factory=dict)

    # Matriz de asignación y de solicitudes (process, resource) -> unidades
    allocation: Dict[Tuple[str, str], int] = field(default_factory=dict)
    requests: Dict[Tuple[str, str], int] = field(default_factory=dict)

    blocked_processes: Set[str] = field(default_factory=set)
    tick: int = 0

    # Helpers para leer/escribir matriz de asignación
    def get_allocation(self, pid: str, rid: str) -> int:
        return self.allocation.get((pid, rid), 0)

    def set_allocation(self, pid: str, rid: str, units: int) -> None:
        if units <= 0:
            self.allocation.pop((pid, rid), None)
        else:
            self.allocation[(pid, rid)] = units

    # Helpers para leer/escribir matriz de solicitud
    def get_request(self, pid: str, rid: str) -> int:
        return self.requests.get((pid, rid), 0)

    def set_request(self, pid: str, rid: str, units: int) -> None:
        if units <= 0:
            self.requests.pop((pid, rid), None)
        else:
            self.requests[(pid, rid)] = units
