# PROYECTO-DE-SISTEMAS-OPERATIVOS---INTERBLOQUEOS-
# Simulador de Interbloqueos
Curso: Sistemas Operativos
Proyecto Final — Universidad Mariano Gálvez de Guatemala

Este proyecto implementa un simulador visual e interactivo que reproduce el comportamiento de un sistema concurrente donde múltiples procesos compiten por recursos limitados. El objetivo principal es permitir el estudio práctico del interbloqueo (deadlock), su detección mediante grafos de espera y su recuperación a través de políticas de selección de víctimas.

El simulador combina teoría de sistemas operativos con una interfaz gráfica intuitiva que ayuda a visualizar en tiempo real cómo los procesos avanzan, se bloquean, crean dependencias y generan ciclos.

## Características principales
Simulación por eventos (REQUEST, RELEASE, COMPUTE)
Construcción dinámica del Wait-For Graph
Detección automática de ciclos en el grafo
Políticas de recuperación: menor_trabajo_hecho, menor_prioridad
Panel de detalles para procesos y recursos
Gráficos en tiempo real:
Distribución de estados de procesos
Uso de recursos
Grafo de Espera animado
Carga de configuraciones (config.json) y eventos (events.csv)
Generación automática de escenarios
Interfaz moderna con temas Claro, Oscuro y Pastel
Filtros avanzados en el registro de eventos

