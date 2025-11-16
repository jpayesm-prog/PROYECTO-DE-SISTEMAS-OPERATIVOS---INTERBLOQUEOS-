from typing import List
from models import SystemState, Event
from deadlock import build_wait_for_graph, detect_cycle, select_victim, resolve_deadlock

# ───────────────────────────────────────────────
# Función principal del motor de simulación
# ───────────────────────────────────────────────

def run_simulation(state: SystemState, events: List[Event]) -> None:
    print("\n=== INICIO DE LA SIMULACIÓN ===\n")

    for i, event in enumerate(events):
        state.tick += 1
        print(f"--- Tick {state.tick} | Evento {i}: {event.type} {event.process_id} {event.resource_id or ''} {event.amount_or_time}")

        if event.type == "REQUEST":
            handle_request(state, event)
        elif event.type == "RELEASE":
            handle_release(state, event)
        elif event.type == "COMPUTE":
            handle_compute(state, event)

        # Mostrar estado del sistema después de cada evento
        show_state(state)
        print("-" * 50)

        # Cada cierto número de ticks, verificar interbloqueos
        if state.mode == "deteccion" and state.tick % state.detection_interval == 0:
            print(f"\n[DEBUG] Tick {state.tick}: analizando interbloqueo...")
            graph = build_wait_for_graph(state)
            cycle = detect_cycle(graph)
            if cycle:
                print(f"\nPosible interbloqueo detectado entre: {', '.join(cycle)}")
                victim = select_victim(state, cycle)
                resolve_deadlock(state, victim)
                # Mostrar el estado actualizado después de resolver
                show_state(state)
                print("-" * 50)

    print("\n=== FIN DE LA SIMULACIÓN ===")

    # Mostrar resumen final
    show_summary(state)


# ───────────────────────────────────────────────
# Funciones auxiliares de manejo de eventos
# ───────────────────────────────────────────────

def handle_request(state: SystemState, e: Event):
    pid = e.process_id
    rid = e.resource_id
    req = e.amount_or_time

    resource = state.resources[rid]
    allocated = state.get_allocation(pid, rid)
    requested = state.get_request(pid, rid)

    # Si hay suficientes instancias disponibles
    if resource.available_instances >= req:
        resource.available_instances -= req
        state.set_allocation(pid, rid, allocated + req)
        state.set_request(pid, rid, 0)
        print(f"{pid} obtiene {req} instancia(s) de {rid}.")
        # Si estaba bloqueado, lo desbloqueamos
        if pid in state.blocked_processes:
            state.blocked_processes.remove(pid)
    else:
        # No hay suficientes instancias, el proceso se bloquea
        state.set_request(pid, rid, requested + req)
        state.blocked_processes.add(pid)
        print(f"{pid} BLOQUEADO: no hay suficientes instancias de {rid}.")


def handle_release(state: SystemState, e: Event):
    pid = e.process_id
    rid = e.resource_id
    rel = e.amount_or_time

    resource = state.resources[rid]
    allocated = state.get_allocation(pid, rid)

    # Solo libera si tenía asignadas
    if allocated >= rel:
        resource.available_instances += rel
        state.set_allocation(pid, rid, allocated - rel)
        print(f"{pid} libera {rel} instancia(s) de {rid}.")
    else:
        print(f"{pid} intentó liberar {rel} de {rid}, pero solo tenía {allocated} asignadas.")


def handle_compute(state: SystemState, e: Event):
    pid = e.process_id
    time = e.amount_or_time
    proc = state.processes[pid]
    proc.work_done += time
    print(f"💻 {pid} realiza {time} unidad(es) de trabajo (total={proc.work_done}).")


# ───────────────────────────────────────────────
# Mostrar estado actual
# ───────────────────────────────────────────────

def show_state(state: SystemState):
    print("\nEstado actual:")
    for rid, res in state.resources.items():
        print(f"  {rid}: disp={res.available_instances}/{res.total_instances}")

    if state.blocked_processes:
        print(f"Procesos bloqueados: {', '.join(state.blocked_processes)}")
    else:
        print("Procesos bloqueados: ninguno")

    # Mostrar matriz de asignación compacta
    print("Asignaciones:")
    if not state.allocation:
        print("  (sin asignaciones)")
    else:
        for (pid, rid), val in state.allocation.items():
            print(f"  {pid}-{rid}: {val}")


# ───────────────────────────────────────────────
# Resumen final
# ───────────────────────────────────────────────

def show_summary(state: SystemState):
    print("\n=== RESUMEN FINAL ===")
    print(f"Total de ticks ejecutados: {state.tick}")

    print("\nRecursos finales:")
    for rid, res in state.resources.items():
        print(f"  {rid}: disponibles={res.available_instances}/{res.total_instances}")

    print("\nProcesos abortados:")
    if hasattr(state, "aborted_processes") and state.aborted_processes:
        for p in state.aborted_processes:
            print(f"  ⚰ {p}")
    else:
        print("  Ninguno")

    print("\nProcesos bloqueados al final:")
    if state.blocked_processes:
        print("  " + ", ".join(state.blocked_processes))
    else:
        print("  Ninguno")

    print("===============================")
