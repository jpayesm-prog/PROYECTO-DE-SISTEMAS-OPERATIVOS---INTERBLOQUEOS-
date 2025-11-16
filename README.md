# PROYECTO-DE-SISTEMAS-OPERATIVOS---INTERBLOQUEOS-
# Simulador de Interbloqueos
Curso: Sistemas Operativos
Proyecto Final — Universidad Mariano Gálvez de Guatemala

Este proyecto implementa un simulador visual e interactivo que reproduce el comportamiento de un sistema concurrente donde múltiples procesos compiten por recursos limitados. El objetivo principal es permitir el estudio práctico del interbloqueo (deadlock), su detección mediante grafos de espera y su recuperación a través de políticas de selección de víctimas.

El simulador combina teoría de sistemas operativos con una interfaz gráfica intuitiva que ayuda a visualizar en tiempo real cómo los procesos avanzan, se bloquean, crean dependencias y generan ciclos.

## Características principales
1. Simulación por eventos (REQUEST, RELEASE, COMPUTE)
2. Construcción dinámica del Wait-For Graph
3. Detección automática de ciclos en el grafo
4. Políticas de recuperación: menor_trabajo_hecho, menor_prioridad
5. Panel de detalles para procesos y recursos
6. Gráficos en tiempo real:
7. Distribución de estados de procesos
8. Uso de recursos
9. Grafo de Espera animado
10. Carga de configuraciones (config.json) y eventos (events.csv)
11. Generación automática de escenarios
12. Interfaz moderna con temas Claro, Oscuro y Pastel
13. Filtros avanzados en el registro de eventos

# Estructura del proyecto
├── gui.py               # Interfaz gráfica (PyQt5)
├── sim.py               # Motor de simulación por eventos
├── deadlock.py          # Algoritmos de detección y resolución de interbloqueos
├── models.py            # Modelos del sistema (procesos, recursos, estado)
├── io_utils.py          # Carga de config.json y events.csv
├── main.py              # Punto de ejecución no visual
├── config.json          # Archivo de configuración (ejemplo)
├── events.csv           # Archivo de eventos (ejemplo)
└── README.md            # Instructivo

# Requisitos
Asegúrate de tener instalado:
1. Python 3.8+
2. PyQt5
3. Matplotlib
4. NetworkX

Puedes instalar todo con:
pip install -r requirements.txt
(En caso de no usar requirements, instalar manualmente:)
pip install pyqt5 matplotlib networkx

# ¿Cómo ejecutar el simulador?
1. Clonar o descargar el repositorio.
2. Abrir una terminal dentro del proyecto.
3. Ejecutar:
python gui.py (La interfaz gráfica se abrirá automáticamente.)

# Cargar una simulación
En la barra superior:
1. Clic en “Configuración”
2. Elegir: Cargar config.json y events.csv. Generar configuración manual. Generar configuración automática.
3. Luego presiona:
Ejecutar → corre toda la simulación
Paso a paso → avanza un evento por tick
Reiniciar → vuelve todo al estado inicial

# ¿Cómo usar la interfaz?
✔️ Panel izquierdo

Gráfico de estados (Activos, Bloqueados, Abortados)
Gráfico de uso de recursos
Grafo de Espera animado
Registro de eventos filtrable por tipo

✔️ Panel derecho

Detalles de procesos (prioridad, trabajo hecho, recursos asignados)
Detalles de recursos (instancias, uso)
Estadísticas del sistema
Puedes hacer clic en nodos del grafo o en eventos para ver sus detalles.

# Modo Detección y Recuperación
El simulador construye el Wait-For Graph y cada cierto intervalo (configurable) ejecuta:

1. Construcción del grafo
2. Detección de ciclos mediante DFS
3. Selección de víctima
4. Abortado del proceso
5. Liberación de recursos
6. Continuación normal del sistema

# Escenarios de prueba
Puedes probar:
1. Ciclos simples (P1 ↔ P2)
2. Ciclos largos (P1 → P2 → P3 → P1)
3. Múltiples procesos bloqueados
4. Recursos con múltiples instancias
5. Cargas aleatorias con generación automática

# Autores
Karla Gabriela Mendoza Bravo - 5090-23-15243 
Andrea Paola Chacón Segura - 5090-23-1225
Joseline Vanessa Payes Mejía - 5090-23-14071
Esteban José Tumax Cano - 5090-23-16170

# Fecha
Guatemala, 16 noviembre 2025

