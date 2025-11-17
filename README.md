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
```text
PROYECTO_INTERBLOQUEOS/
│
├── config1.json               # Configuración de ejemplo (procesos, recursos, política, modo)
├── config2.json               # Configuración adicional para pruebas
├── config3.json               # Variantes de escenarios
├── config4.json               # Configuración extendida
│
├── events1.csv                # Secuencia de eventos (REQUEST, RELEASE, COMPUTE)
├── events2.csv                # Caso de prueba 2
├── events3.csv                # Caso de prueba 3
├── events4.csv                # Caso de prueba 4
│
├── deadlock.py                # Algoritmos de detección de ciclos y selección de víctima
├── gui.py                     # Interfaz gráfica completa (PyQt5 + Matplotlib + NetworkX)
├── io_utils.py                # Carga de config.json y events.csv
├── main.py                    # Ejecución del simulador sin interfaz (modo consola)
├── models.py                  # Modelado de procesos, recursos y SystemState
├── sim.py                     # Motor de simulación: REQUEST, RELEASE, COMPUTE y detección
│
├── temp_config.json           # Configuración generada automáticamente por la GUI
└── temp_events.csv            # Eventos generados automáticamente por la GUI
```



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

## ¿Cómo usar la interfaz?

### Panel izquierdo
- Gráfico de estados (Activos, Bloqueados, Abortados)
- Gráfico de uso de recursos
- Grafo de Espera animado en tiempo real
- Registro de eventos con filtros por tipo

### Panel derecho
- Detalles de procesos (prioridad, trabajo hecho, recursos asignados)
- Detalles de recursos (instancias disponibles, uso, procesos asignados)
- Estadísticas generales y métricas del sistema

Puedes hacer clic en los nodos del grafo o en cualquier evento del registro para ver información detallada de procesos o recursos.


# Modo Detección y Recuperación
El simulador construye el Wait-For Graph y cada cierto intervalo (configurable) ejecuta:

1. Construcción del grafo
2. Detección de ciclos mediante DFS
3. Selección de víctima
4. Abortado del proceso
5. Liberación de recursos
6. Continuación normal del sistema

## Escenarios de prueba

El simulador incluye distintos tipos de escenarios que permiten observar desde casos simples hasta situaciones complejas de interbloqueo. En el repositorio se proporcionan archivos `config*.json` y `events*.csv` que representan estos casos de prueba.

1. Ciclos simples de interbloqueo (P1 ↔ P2)  
   Escenario básico donde dos procesos se bloquean mutuamente al solicitar recursos que el otro ya posee. Es ideal para visualizar de forma clara el grafo de espera (Wait-For Graph) y cómo el algoritmo detecta el ciclo entre ambos procesos.

2. Ciclos largos entre varios procesos (P1 → P2 → P3 → P1)  
   Caso donde la dependencia se extiende a más de dos procesos, haciendo que el interbloqueo sea menos evidente a simple vista. El grafo de espera permite identificar el ciclo completo y, una vez detectado, se aplica la política de selección de víctima configurada en el sistema.

3. Múltiples procesos bloqueados de forma simultánea  
   Situación en la que varios procesos compiten por los mismos recursos y terminan en estado bloqueado. Este escenario sirve para analizar el impacto en la “salud del sistema”, el porcentaje de procesos bloqueados y cómo evoluciona la simulación a medida que se resuelven o no los interbloqueos.

4. Recursos con múltiples instancias y alta contención  
   En estos casos, un mismo recurso dispone de varias instancias, pero la demanda total de los procesos es muy alta. Se pueden estudiar situaciones donde algunos procesos obtienen parte de los recursos mientras otros esperan, evaluando cómo la política de asignación y liberación afecta al rendimiento y a la aparición de ciclos.

5. Cargas de trabajo aleatorias con generación automática  
   La interfaz permite generar configuraciones y listas de eventos aleatorios (`REQUEST`, `RELEASE`, `COMPUTE`) para crear escenarios no predecibles. Estos casos son útiles para probar la robustez del algoritmo de detección de interbloqueos, la selección de víctimas y el comportamiento global del sistema bajo diferentes patrones de carga.

# Autores
---

### Autores

<div align="center">
  
**Karla Gabriela Mendoza Bravo** (5090-23-15243)<br>
**Andrea Paola Chacón Segura** (5090-23-1225)<br>
**Joseline Vanessa Payes Mejía** (5090-23-14071)<br>
**Esteban José Tumax Cano** (5090-23-16170)

</div>

# Fecha
Guatemala, 16 noviembre 2025

## FAQ (Preguntas Frecuentes)
<details>
  <summary><strong>P: ¿Por qué la aplicación se cierra sola (crashea)?</strong></summary>
  <br>
  <strong>R:</strong> Esto puede pasar si tienes dos versiones de PyQt5 o Matplotlib en conflicto. Asegúrate de haber instalado las dependencias en un entorno virtual limpio (`venv`) como se indica en la guía de instalación.
</details>

<details>
  <summary><strong>P: No veo ningún interbloqueo, ¿qué archivo debo usar?</strong></summary>
  <br>
  <strong>R:</strong> ¡El escenario de interbloqueo está en `config2.json` y `events2.csv`! Carga esos dos archivos para ver la detección y recuperación en acción.
</details>

<details>
  <summary><strong>P: ¿Puedo crear mis propios escenarios?</strong></summary>
  <br>
  <strong>R:</strong> ¡Sí! Simplemente crea un nuevo `config_mio.json` (definiendo procesos/recursos) y un `events_mio.csv` (definiendo la secuencia de `REQUEST`/`RELEASE`). El simulador puede cargar cualquier archivo con el formato correcto.
</details>
