from models import SystemState

def build_wait_for_graph(state: SystemState):
    """
    Construye el grafo de espera (Wait-For Graph):
    Si un proceso tiene una solicitud pendiente de un recurso
    que está asignado a otro proceso, se crea una arista.
    """
    graph = {pid: [] for pid in state.processes.keys()}

    # Recorremos todas las solicitudes pendientes
    for (pid, rid), req_units in state.requests.items():
        if req_units > 0:
            # Buscar TODOS los procesos que poseen ese recurso
            for (other_pid, other_rid), alloc_units in state.allocation.items():
                if other_rid == rid and alloc_units > 0 and other_pid != pid:
                    if other_pid not in graph[pid]:
                        graph[pid].append(other_pid)

    print(f"[DEBUG] Wait-for graph construido: {graph}")
    return graph


def detect_cycle(graph):
    """
    Devuelve una lista con los procesos que forman un ciclo (deadlock),
    o None si no hay ciclo.
    """
    visited = set()
    rec_stack = set()

    def dfs(node):
        visited.add(node)
        rec_stack.add(node)
        for neighbor in graph[node]:
            if neighbor not in visited:
                cycle = dfs(neighbor)
                if cycle:
                    return cycle
            elif neighbor in rec_stack:
                # ciclo encontrado
                return list(rec_stack)
        rec_stack.remove(node)
        return None

    for n in graph:
        if n not in visited:
            cycle = dfs(n)
            if cycle:
                return cycle
    return None


def select_victim(state: SystemState, cycle):
    """Selecciona la víctima según la política configurada."""
    if not cycle:
        return None

    policy = state.victim_policy.lower()

    if "menor" in policy:
        victim = min(cycle, key=lambda pid: state.processes[pid].work_done)
    elif "prioridad" in policy:
        victim = max(cycle, key=lambda pid: state.processes[pid].priority)
    else:
        victim = cycle[0]
    return victim


def resolve_deadlock(state: SystemState, victim):
    """Libera todos los recursos del proceso víctima y lo marca como abortado."""
    if victim not in state.processes:
        return

    print(f" Interbloqueo detectado. Se abortará {victim}.\n")

    to_release = []
    for (pid, rid), alloc in list(state.allocation.items()):
        if pid == victim and alloc > 0:
            to_release.append((rid, alloc))
            state.resources[rid].available_instances += alloc
            state.allocation.pop((pid, rid))

    for (pid, rid) in list(state.requests.keys()):
        if pid == victim:
            state.requests.pop((pid, rid))

    if not hasattr(state, "aborted_processes"):
        state.aborted_processes = set()
    state.aborted_processes.add(victim)

    print(f"⚰ {victim} liberó recursos: {to_release}\n")
