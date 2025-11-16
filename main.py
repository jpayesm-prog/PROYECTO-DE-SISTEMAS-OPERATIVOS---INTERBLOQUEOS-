from io_utils import load_config, load_events
from sim import run_simulation


def main():
    # Cargar configuración y eventos
    state = load_config("config.json")
    events = load_events("events.csv")

    # Ejecutar simulación
    run_simulation(state, events)


if __name__ == "__main__":
    main()