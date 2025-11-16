import sys
import io
import contextlib
import json
import csv
import random
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Qt5Agg')

# Importaciones CORREGIDAS de matplotlib
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QFileDialog, QTableWidget, QTableWidgetItem,
    QMessageBox, QTextEdit, QFrame, QGridLayout, QGroupBox,
    QSplitter, QProgressBar, QComboBox, QLineEdit, QCheckBox,
    QStackedWidget, QListWidget, QListWidgetItem, QTabWidget,
    QDialog, QFormLayout, QSpinBox, QDialogButtonBox, QScrollArea,
    QToolButton, QMenu, QAction, QSizePolicy, QMainWindow, QToolBar,
    QStatusBar
)
from PyQt5.QtGui import (
    QColor, QFont, QPalette, QIcon, QPixmap, QCursor
)
from PyQt5.QtCore import (
    Qt, QSize, QPropertyAnimation, QEasingCurve, 
    pyqtProperty, QTimer, QPoint
)

# Simulamos los módulos que no están presentes
class Process:
    def __init__(self, pid, priority=1):
        self.pid = pid
        self.priority = priority
        self.work_done = 0

class Resource:
    def __init__(self, rid, total_instances):
        self.rid = rid
        self.total_instances = total_instances
        self.available_instances = total_instances

class SystemState:
    def __init__(self):
        self.processes = {}
        self.resources = {}
        self.allocation = {}
        self.requests = {}
        self.blocked_processes = set()
        self.aborted_processes = set()
        self.tick = 0
        self.event_history = []

def load_config(path):
    """Simula la carga de configuración"""
    with open(path, 'r') as f:
        config = json.load(f)
    
    state = SystemState()
    
    # Crear procesos
    for proc_config in config.get('processes', []):
        pid = proc_config['pid']
        priority = proc_config.get('priority', 1)
        state.processes[pid] = Process(pid, priority)
    
    # Crear recursos
    for res_config in config.get('resources', []):
        rid = res_config['rid']
        instances = res_config['instances']
        state.resources[rid] = Resource(rid, instances)
    
    return state

def load_events(path):
    """Simula la carga de eventos"""
    events = []
    with open(path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            events.append(row)
    return events

def build_wait_for_graph(state):
    """Simula la construcción del grafo de espera"""
    graph = {}
    for pid in state.processes:
        graph[pid] = []
        
        # Simular algunas dependencias para demostración
        if pid == "P1":
            graph[pid] = ["P2"]
        elif pid == "P2":
            graph[pid] = ["P1"]
    
    return graph

def run_simulation(state, events):
    """Simula la ejecución de la simulación"""
    print("INICIO DE LA SIMULACIÓN")
    
    for i, event in enumerate(events):
        state.tick = i + 1
        event_type = event['type']
        process = event['process']
        resource = event.get('resource', '')
        amount = int(event.get('amount_or_time', 1))
        
        print(f"Tick {state.tick} | Evento {i}: {event_type}")
        
        if event_type == "REQUEST":
            print(f"{process} {resource} {amount}")
            if resource in state.resources:
                resource_obj = state.resources[resource]
                if resource_obj.available_instances >= amount:
                    resource_obj.available_instances -= amount
                    state.allocation[(process, resource)] = amount
                    print(f"{process} obtiene {amount} instancia(s) de {resource}.")
                else:
                    state.blocked_processes.add(process)
                    print(f"{process} no puede obtener {resource}. Bloqueado.")
        
        elif event_type == "RELEASE":
            print(f"{process} {resource} {amount}")
            if (process, resource) in state.allocation:
                allocated = state.allocation[(process, resource)]
                if resource in state.resources:
                    state.resources[resource].available_instances += allocated
                    del state.allocation[(process, resource)]
                    print(f"{process} libera {allocated} instancia(s) de {resource}.")
        
        elif event_type == "COMPUTE":
            print(f"{process} ejecuta {amount} ciclos.")
            if process in state.processes:
                state.processes[process].work_done += amount
        
        # Simular detección de interbloqueo ocasional
        if state.tick % 3 == 0 and len(state.blocked_processes) > 1:
            print(f"[DEBUG] Tick {state.tick}: analizando interbloqueo...")
            graph = build_wait_for_graph(state)
            print(f"[DEBUG] Wait-for graph: {graph}")
            
            # Detectar ciclo simple
            if "P1" in graph and "P2" in graph.get("P1", []) and "P1" in graph.get("P2", []):
                print("¡INTERBLOQUEO DETECTADO! Ciclo P1<->P2")
                # Elegir víctima (P2 como ejemplo)
                victim = "P2"
                state.aborted_processes.add(victim)
                if victim in state.blocked_processes:
                    state.blocked_processes.remove(victim)
                print(f"Proceso {victim} abortado para resolver interbloqueo.")
        
        # Registrar evento en historial
        state.event_history.append(f"Tick {state.tick}: {event_type} {process} {resource if resource else ''}")
        
        print(f"Estado actual:")
        for rid, resource_obj in state.resources.items():
            print(f"{rid}: disp={resource_obj.available_instances}/{resource_obj.total_instances}")
        print(f"Procesos bloqueados: {state.blocked_processes if state.blocked_processes else 'ninguno'}")
        print("......")
    
    print("FIN DE LA SIMULACIÓN")


class ConfigurationDialog(QDialog):
    """Diálogo para configuración manual o generación automática"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configuración del Sistema")
        self.setModal(True)
        self.resize(500, 400)
        
        layout = QVBoxLayout()
        
        # Selección de modo
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["Cargar archivo", "Configuración manual", "Generar automáticamente"])
        layout.addWidget(QLabel("Modo de configuración:"))
        layout.addWidget(self.mode_combo)
        
        # Stack para diferentes modos
        self.stack = QStackedWidget()
        
        # Modo archivo
        file_widget = QWidget()
        file_layout = QVBoxLayout()
        self.config_file_btn = QPushButton("Seleccionar config.json")
        self.events_file_btn = QPushButton("Seleccionar events.csv")
        file_layout.addWidget(self.config_file_btn)
        file_layout.addWidget(self.events_file_btn)
        file_widget.setLayout(file_layout)
        
        # Modo manual
        manual_widget = QWidget()
        manual_layout = QFormLayout()
        self.process_count = QSpinBox()
        self.process_count.setRange(1, 20)
        self.process_count.setValue(3)
        self.resource_count = QSpinBox()
        self.resource_count.setRange(1, 10)
        self.resource_count.setValue(2)
        self.event_count = QSpinBox()
        self.event_count.setRange(5, 100)
        self.event_count.setValue(10)
        manual_layout.addRow("Número de procesos:", self.process_count)
        manual_layout.addRow("Número de recursos:", self.resource_count)
        manual_layout.addRow("Número de eventos:", self.event_count)
        manual_widget.setLayout(manual_layout)
        
        # Modo automático
        auto_widget = QWidget()
        auto_layout = QVBoxLayout()
        auto_layout.addWidget(QLabel("Se generará una configuración aleatoria\ncon parámetros equilibrados para testing."))
        auto_widget.setLayout(auto_layout)
        
        self.stack.addWidget(file_widget)
        self.stack.addWidget(manual_widget)
        self.stack.addWidget(auto_widget)
        
        layout.addWidget(self.stack)
        
        # Botones
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        self.setLayout(layout)
        
        # Conexiones
        self.mode_combo.currentIndexChanged.connect(self.stack.setCurrentIndex)
        self.config_file_btn.clicked.connect(self.select_config_file)
        self.events_file_btn.clicked.connect(self.select_events_file)
        
        self.config_path = ""
        self.events_path = ""
        
    def select_config_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Seleccionar config.json", "", "JSON (*.json)")
        if path:
            self.config_path = path
            self.config_file_btn.setText(f"📁 {Path(path).name}")
            
    def select_events_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Seleccionar events.csv", "", "CSV (*.csv)")
        if path:
            self.events_path = path
            self.events_file_btn.setText(f"📊 {Path(path).name}")


class DetailsPanel(QWidget):
    """Panel lateral para mostrar detalles avanzados"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMaximumWidth(400)
        self.setMinimumWidth(300)
        
        layout = QVBoxLayout()
        
        # Header del panel
        self.header_label = QLabel("Detalles")
        self.header_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #007bff; padding: 10px;")
        layout.addWidget(self.header_label)
        
        # Pestañas
        self.tabs = QTabWidget()
        
        # Pestaña de información general
        self.info_tab = QWidget()
        info_layout = QVBoxLayout()
        self.info_text = QTextEdit()
        self.info_text.setReadOnly(True)
        info_layout.addWidget(self.info_text)
        self.info_tab.setLayout(info_layout)
        
        # Pestaña de historial
        self.history_tab = QWidget()
        history_layout = QVBoxLayout()
        self.history_list = QListWidget()
        history_layout.addWidget(self.history_list)
        self.history_tab.setLayout(history_layout)
        
        # Pestaña de estadísticas
        self.stats_tab = QWidget()
        stats_layout = QVBoxLayout()
        self.stats_text = QTextEdit()
        self.stats_text.setReadOnly(True)
        stats_layout.addWidget(self.stats_text)
        self.stats_tab.setLayout(stats_layout)
        
        self.tabs.addTab(self.info_tab, "📋 Info")
        self.tabs.addTab(self.history_tab, "📅 Historial")
        self.tabs.addTab(self.stats_tab, "📊 Stats")
        
        layout.addWidget(self.tabs)
        self.setLayout(layout)
        
    def show_process_details(self, process, state):
        """Muestra detalles de un proceso"""
        self.header_label.setText(f"Proceso: {process.pid}")
        
        # Información general
        info_html = f"""
        <h3>Proceso {process.pid}</h3>
        <p><b>Prioridad:</b> {process.priority}</p>
        <p><b>Trabajo realizado:</b> {process.work_done} unidades</p>
        <p><b>Estado:</b> {self.get_process_status(process, state)}</p>
        <hr>
        <h4>Recursos asignados:</h4>
        <ul>
        """
        
        # Recursos asignados
        for (pid, rid), amount in state.allocation.items():
            if pid == process.pid and amount > 0:
                info_html += f"<li>{rid}: {amount} instancias</li>"
        
        info_html += "</ul><h4>Solicitudes pendientes:</h4><ul>"
        
        # Solicitudes pendientes
        for (pid, rid), amount in state.requests.items():
            if pid == process.pid and amount > 0:
                info_html += f"<li>{rid}: {amount} instancias</li>"
                
        info_html += "</ul>"
        self.info_text.setHtml(info_html)
        
        # Historial del proceso
        self.history_list.clear()
        if hasattr(state, 'event_history'):
            process_events = [event for event in state.event_history if process.pid in event]
            for event in process_events[-10:]:  # Últimos 10 eventos
                self.history_list.addItem(f"• {event}")
        else:
            events = ["Inicio del proceso", "Solicitud de recursos", "Ejecución", "Liberación"]
            for event in events:
                self.history_list.addItem(f"• {event}")
            
        # Estadísticas
        blocked_time = len([t for t in range(state.tick) if process.pid in state.blocked_processes])
        efficiency = (process.work_done / max(1, state.tick)) * 100
        resources_used = sum(amount for (pid, rid), amount in state.allocation.items() if pid == process.pid)
        
        stats_html = f"""
        <h3>Estadísticas de {process.pid}</h3>
        <p><b>Eficiencia:</b> {efficiency:.1f}%</p>
        <p><b>Ticks bloqueado:</b> {blocked_time}</p>
        <p><b>Recursos utilizados:</b> {resources_used}</p>
        <p><b>Trabajo total:</b> {process.work_done} unidades</p>
        <p><b>Prioridad:</b> {process.priority}</p>
        """
        self.stats_text.setHtml(stats_html)
        
    def show_resource_details(self, resource, state):
        """Muestra detalles de un recurso"""
        self.header_label.setText(f"Recurso: {resource.rid}")
        
        usage_rate = ((resource.total_instances - resource.available_instances) / resource.total_instances) * 100
        
        info_html = f"""
        <h3>Recurso {resource.rid}</h3>
        <p><b>Instancias totales:</b> {resource.total_instances}</p>
        <p><b>Disponibles:</b> {resource.available_instances}</p>
        <p><b>En uso:</b> {resource.total_instances - resource.available_instances}</p>
        <p><b>Tasa de uso:</b> {usage_rate:.1f}%</p>
        <hr>
        <h4>Procesos que usan este recurso:</h4>
        <ul>
        """
        
        for (pid, rid), amount in state.allocation.items():
            if rid == resource.rid and amount > 0:
                info_html += f"<li>{pid}: {amount} instancias</li>"
                
        info_html += "</ul>"
        self.info_text.setHtml(info_html)
        
        # Historial del recurso
        self.history_list.clear()
        if hasattr(state, 'event_history'):
            resource_events = [event for event in state.event_history if resource.rid in event]
            for event in resource_events[-10:]:
                self.history_list.addItem(f"• {event}")
                
        # Estadísticas del recurso
        stats_html = f"""
        <h3>Estadísticas de {resource.rid}</h3>
        <p><b>Disponibilidad:</b> {resource.available_instances}/{resource.total_instances}</p>
        <p><b>Tasa de uso:</b> {usage_rate:.1f}%</p>
        <p><b>Procesos en espera:</b> {len([pid for pid in state.blocked_processes])}</p>
        <p><b>Conflictos detectados:</b> {len([e for e in state.event_history if 'interbloqueo' in e.lower()])}</p>
        """
        self.stats_text.setHtml(stats_html)
        
    def show_system_overview(self, state):
        """Muestra una visión general del sistema"""
        self.header_label.setText("Visión General del Sistema")
        
        # Calcular métricas
        total_processes = len(state.processes)
        blocked_processes = len(state.blocked_processes)
        aborted_processes = len(getattr(state, 'aborted_processes', set()))
        
        # Calcular uso de recursos
        resource_usage = {}
        for rid, resource in state.resources.items():
            usage_rate = ((resource.total_instances - resource.available_instances) / 
                         resource.total_instances) * 100
            resource_usage[rid] = usage_rate
            
        # Calcular métricas de eficiencia
        total_work = sum(proc.work_done for proc in state.processes.values())
        avg_efficiency = (total_work / max(1, state.tick * total_processes)) * 100
        
        info_html = f"""
        <h3>Estado del Sistema</h3>
        <p><b>Procesos totales:</b> {total_processes}</p>
        <p><b>Procesos activos:</b> {total_processes - blocked_processes - aborted_processes}</p>
        <p><b>Procesos bloqueados:</b> {blocked_processes}</p>
        <p><b>Procesos abortados:</b> {aborted_processes}</p>
        <p><b>Tick actual:</b> {state.tick}</p>
        <p><b>Trabajo total realizado:</b> {total_work} unidades</p>
        <hr>
        <h4>Uso de Recursos:</h4>
        <ul>
        """
        
        for rid, usage in resource_usage.items():
            status = "🟢 Normal" if usage < 70 else "🟡 Alto" if usage < 90 else "🔴 Crítico"
            info_html += f"<li>{rid}: {usage:.1f}% ({status})</li>"
            
        info_html += "</ul>"
        self.info_text.setHtml(info_html)
        
        # Actualizar historial con eventos recientes
        self.history_list.clear()
        if hasattr(state, 'event_history'):
            for event in state.event_history[-15:]:  # Últimos 15 eventos
                self.history_list.addItem(f"• {event}")
        else:
            self.history_list.addItem("• Sistema iniciado")
            self.history_list.addItem("• Esperando eventos...")
            
        # Mostrar estadísticas del sistema
        deadlock_count = len([e for e in state.event_history if 'interbloqueo' in e.lower()])
        requests_count = len([e for e in state.event_history if 'REQUEST' in e])
        compute_count = len([e for e in state.event_history if 'COMPUTE' in e])
        
        stats_html = f"""
        <h3>Métricas del Sistema</h3>
        <p><b>Solicitudes realizadas:</b> {requests_count}</p>
        <p><b>Operaciones COMPUTE:</b> {compute_count}</p>
        <p><b>Interbloqueos detectados:</b> {deadlock_count}</p>
        <p><b>Procesos víctima:</b> {aborted_processes}</p>
        <p><b>Eficiencia promedio:</b> {avg_efficiency:.1f}%</p>
        <p><b>Ticks ejecutados:</b> {state.tick}</p>
        """
        self.stats_text.setHtml(stats_html)
        
    def get_process_status(self, process, state):
        """Obtiene el estado textual del proceso"""
        if hasattr(state, 'aborted_processes') and process.pid in state.aborted_processes:
            return "❌ Abortado"
        elif process.pid in state.blocked_processes:
            return "⚠️ Bloqueado"
        else:
            return "✅ Activo"


class AnimatedGraph(FigureCanvas):
    """Canvas de gráfico con animaciones simplificadas"""
    def __init__(self, parent=None):
        self.fig = Figure(figsize=(8, 6))
        super().__init__(self.fig)
        self.setParent(parent)
        
        self.ax = self.fig.add_subplot(111)
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.update_animation)
        self.animation_phase = 0
        self.current_state = None
        
    def update_animation(self):
        """Actualiza la animación"""
        self.animation_phase += 0.1
        self.draw_graph(self.current_state)
        
    def start_animation(self):
        """Inicia la animación"""
        self.animation_timer.start(100)  # 10 FPS
        
    def stop_animation(self):
        """Detiene la animación"""
        self.animation_timer.stop()
        
    def draw_graph(self, state=None):
        """Dibuja el grafo con animaciones simples"""
        self.ax.clear()
        
        if not state:
            self.ax.text(0.5, 0.5, 'Cargue la configuración\npara ver el grafo', 
                        ha='center', va='center', transform=self.ax.transAxes, fontsize=12)
            self.ax.set_title('Grafo de Espera')
            self.draw()
            return
            
        graph = build_wait_for_graph(state)
        self.current_state = state
        
        G = nx.DiGraph()
        for pid in state.processes.keys():
            G.add_node(pid)
            
        # Construir aristas del grafo
        for pid, deps in graph.items():
            for dep in deps:
                G.add_edge(pid, dep)
                
        if len(G.nodes()) == 0:
            self.ax.text(0.5, 0.5, 'No hay procesos en el sistema', 
                        ha='center', va='center', transform=self.ax.transAxes)
            self.draw()
            return
            
        pos = nx.spring_layout(G, seed=42, k=2, iterations=50)
        
        # Dibujar nodos con animación simple
        node_colors = []
        node_sizes = []
        
        for node_id in G.nodes():
            # Efecto de pulso para nodos bloqueados
            pulse = 1.0
            if node_id in state.blocked_processes:
                pulse = 1.2 + 0.3 * abs(self.animation_phase % 1 - 0.5)  # Pulso entre 1.2 y 1.5
                color = "#dc3545"  # Rojo para bloqueados
            elif hasattr(state, 'aborted_processes') and node_id in state.aborted_processes:
                color = "#6c757d"  # Gris para abortados
            else:
                color = "#28a745"  # Verde para activos
                
            node_colors.append(color)
            node_sizes.append(2000 * pulse)
                
        nx.draw_networkx_nodes(G, pos, node_color=node_colors, 
                              node_size=node_sizes, alpha=0.9,
                              edgecolors="black", linewidths=2, ax=self.ax)
        
        # Dibujar etiquetas de nodos
        nx.draw_networkx_labels(G, pos, font_size=10, font_weight="bold", 
                               font_color="white", ax=self.ax)
        
        # Dibujar aristas con efecto de flujo
        edge_colors = []
        for edge in G.edges():
            # Efecto de flujo en las aristas
            alpha = 0.5 + 0.5 * abs(self.animation_phase % 1 - 0.5)
            edge_colors.append((0.4, 0.4, 0.4, alpha))
        
        nx.draw_networkx_edges(G, pos, arrows=True, arrowstyle='->',
                              arrowsize=20, edge_color="#6c757d", width=2,
                              connectionstyle="arc3,rad=0.1", ax=self.ax)
        
        self.ax.set_title("Grafo de Espera (Wait-For Graph) - En Tiempo Real", 
                         fontweight='bold', pad=20)
        self.ax.axis("off")
        
        # Añadir leyenda de estados
        legend_text = "🟢 Activo  🟡 Bloqueado  🔴 Crítico"
        self.ax.text(0.02, 0.02, legend_text, transform=self.ax.transAxes,
                    bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8))
        
        self.draw()


class DeadlockGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🔗 Simulador Avanzado de Interbloqueos")
        self.resize(1400, 900)
        
        # Estado del sistema
        self.state = None
        self.events = []
        self.current_theme = "light"
        self.details_panel_visible = True
        self.animation_enabled = True
        self.full_log_text = ""
        
        # Configurar interfaz
        self.setup_ui()
        self.apply_theme()
        self.setup_interactive_elements()
        self.setup_event_filters()
        
        # Mostrar visión general por defecto
        QTimer.singleShot(100, self.show_default_overview)
        
    def setup_ui(self):
        """Configura la interfaz de usuario principal"""
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        main_layout = QHBoxLayout(central_widget)
        
        # Splitter principal para paneles
        self.main_splitter = QSplitter(Qt.Horizontal)
        
        # Panel izquierdo - Controles y visualizaciones
        left_panel = self.create_left_panel()
        self.main_splitter.addWidget(left_panel)
        
        # Panel derecho - Detalles (inicialmente visible)
        self.details_panel = DetailsPanel()
        self.main_splitter.addWidget(self.details_panel)
        
        # Configurar proporciones del splitter
        self.main_splitter.setSizes([1000, 400])
        main_layout.addWidget(self.main_splitter)
        
        # Barra de herramientas
        self.setup_toolbar()
        
        # Barra de estado
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Listo")
        
    def setup_toolbar(self):
        """Configura la barra de herramientas"""
        toolbar = QToolBar("Herramientas Principales")
        self.addToolBar(toolbar)
        
        # Botones de control
        self.load_config_btn = QPushButton("📁 Configuración")
        self.load_config_btn.clicked.connect(self.show_config_dialog)
        toolbar.addWidget(self.load_config_btn)
        
        self.run_btn = QPushButton("▶ Ejecutar")
        self.run_btn.clicked.connect(self.run_sim)
        toolbar.addWidget(self.run_btn)
        
        self.step_btn = QPushButton("⏭ Paso a Paso")
        self.step_btn.clicked.connect(self.step_simulation)
        toolbar.addWidget(self.step_btn)

        self.reset_btn = QPushButton("🔄 Reiniciar")
        self.reset_btn.clicked.connect(self.reset_simulation)
        toolbar.addWidget(self.reset_btn)
        
        toolbar.addSeparator()
        
        # Selector de temas
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Claro", "Oscuro", "Pastel"])
        self.theme_combo.currentTextChanged.connect(self.change_theme)
        toolbar.addWidget(QLabel("Tema:"))
        toolbar.addWidget(self.theme_combo)
        
        # Toggle panel de detalles
        self.toggle_details_btn = QPushButton("📊 Mostrar/Ocultar Detalles")
        self.toggle_details_btn.clicked.connect(self.toggle_details_panel)
        toolbar.addWidget(self.toggle_details_btn)
        
        # Toggle animaciones
        self.toggle_animation_btn = QPushButton("✨ Animaciones: ON")
        self.toggle_animation_btn.clicked.connect(self.toggle_animations)
        toolbar.addWidget(self.toggle_animation_btn)
        
    def setup_interactive_elements(self):
        """Conecta elementos interactivos para el panel de detalles"""
        # Conectar clics en el grafo
        self.graph_canvas.mpl_connect('button_press_event', self.on_graph_click)
        
        # Conectar doble clic en el registro de eventos
        self.log_box.mouseDoubleClickEvent = self.on_log_double_click

    def setup_event_filters(self):
        """Configura los filtros de eventos"""
        self.event_filter.currentTextChanged.connect(self.filter_events)
        self.search_box.textChanged.connect(self.filter_events)
        
    def on_graph_click(self, event):
        """Maneja clics en el grafo para mostrar detalles"""
        if not self.state or not event.inaxes:
            return
            
        # Buscar el nodo más cercano al clic
        graph = build_wait_for_graph(self.state)
        G = nx.DiGraph()
        
        for pid in self.state.processes.keys():
            G.add_node(pid)
            
        for pid, deps in graph.items():
            for dep in deps:
                G.add_edge(pid, dep)
                
        if len(G.nodes()) == 0:
            return
            
        pos = nx.spring_layout(G, seed=42, k=2, iterations=50)
        
        # Encontrar el nodo más cercano
        min_dist = float('inf')
        selected_node = None
        
        for node, (x, y) in pos.items():
            dist = ((x - event.xdata) ** 2 + (y - event.ydata) ** 2) ** 0.5
            if dist < min_dist and dist < 0.1:  # Umbral de selección
                min_dist = dist
                selected_node = node
                
        if selected_node:
            # Mostrar detalles del proceso seleccionado
            process = self.state.processes.get(selected_node)
            if process:
                self.details_panel.show_process_details(process, self.state)
                self.status_bar.showMessage(f"Mostrando detalles de {selected_node}", 3000)

    def on_log_double_click(self, event):
        """Maneja doble clic en el registro para buscar detalles"""
        # Buscar nombres de procesos o recursos en el texto seleccionado
        cursor = self.log_box.textCursor()
        selected_text = cursor.selectedText().strip()
        
        if not selected_text:
            return
            
        # Buscar si es un proceso
        if selected_text.startswith('P') and selected_text[1:].isdigit():
            process_id = selected_text
            process = self.state.processes.get(process_id)
            if process:
                self.details_panel.show_process_details(process, self.state)
                self.status_bar.showMessage(f"Mostrando detalles de {process_id}", 3000)
                return
                
        # Buscar si es un recurso  
        if selected_text.startswith('R') and selected_text[1:].isdigit():
            resource_id = selected_text
            resource = self.state.resources.get(resource_id)
            if resource:
                self.details_panel.show_resource_details(resource, self.state)
                self.status_bar.showMessage(f"Mostrando detalles de {resource_id}", 3000)
                return
                
        # Si no se encontró un proceso o recurso específico, buscar en el texto
        words = selected_text.split()
        for word in words:
            if word.startswith('P') and word[1:].isdigit():
                process = self.state.processes.get(word)
                if process:
                    self.details_panel.show_process_details(process, self.state)
                    self.status_bar.showMessage(f"Mostrando detalles de {word}", 3000)
                    return
            elif word.startswith('R') and word[1:].isdigit():
                resource = self.state.resources.get(word)
                if resource:
                    self.details_panel.show_resource_details(resource, self.state)
                    self.status_bar.showMessage(f"Mostrando detalles de {word}", 3000)
                    return

    def filter_events(self):
        """Filtra el registro de eventos según los criterios seleccionados"""
        if not self.full_log_text:
            return
            
        filter_type = self.event_filter.currentText()
        search_text = self.search_box.text().lower()
        
        lines = self.full_log_text.split('\n')
        filtered_lines = []
        
        for line in lines:
            include_line = True
            
            # Filtrar por tipo
            if filter_type != "Todos":
                if filter_type == "REQUEST" and "REQUEST" not in line:
                    include_line = False
                elif filter_type == "RELEASE" and "RELEASE" not in line:
                    include_line = False
                elif filter_type == "COMPUTE" and "COMPUTE" not in line:
                    include_line = False
                elif filter_type == "DEADLOCK" and "interbloqueo" not in line.lower():
                    include_line = False
                elif filter_type == "ABORT" and "abort" not in line.lower():
                    include_line = False
                    
            # Filtrar por texto de búsqueda
            if include_line and search_text:
                if search_text not in line.lower():
                    include_line = False
                    
            if include_line:
                filtered_lines.append(line)
                
        self.log_box.setPlainText('\n'.join(filtered_lines))
        
    def create_left_panel(self):
        """Crea el panel izquierdo con controles y visualizaciones"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Panel de control superior
        control_panel = self.create_control_panel()
        layout.addWidget(control_panel)
        
        # Splitter para visualizaciones
        vis_splitter = QSplitter(Qt.Vertical)
        
        # Gráficos superiores
        top_charts = self.create_top_charts()
        vis_splitter.addWidget(top_charts)
        
        # Grafo y registro
        bottom_panel = self.create_bottom_panel()
        vis_splitter.addWidget(bottom_panel)
        
        vis_splitter.setSizes([400, 600])
        layout.addWidget(vis_splitter)
        
        return panel
        
    def create_control_panel(self):
        """Crea el panel de control superior"""
        panel = QWidget()
        panel.setMaximumHeight(100)
        layout = QHBoxLayout(panel)
        
        # Barra de salud del sistema
        health_group = QGroupBox("Salud del Sistema")
        health_layout = QVBoxLayout()
        
        self.health_bar = QProgressBar()
        self.health_bar.setMaximum(100)
        self.health_bar.setValue(100)
        self.health_bar.setTextVisible(True)
        self.health_bar.setFormat("Salud del Sistema: %p%")
        health_layout.addWidget(self.health_bar)
        
        health_group.setLayout(health_layout)
        layout.addWidget(health_group)
        
        # Badges de estado
        badges_group = QGroupBox("Estado del Sistema")
        badges_layout = QHBoxLayout()
        
        self.processes_badge = QLabel("Procesos: 0")
        self.blocked_badge = QLabel("Bloqueados: 0")
        self.aborted_badge = QLabel("Abortados: 0")
        
        badges_layout.addWidget(self.processes_badge)
        badges_layout.addWidget(self.blocked_badge)
        badges_layout.addWidget(self.aborted_badge)
        
        badges_group.setLayout(badges_layout)
        layout.addWidget(badges_group)
        
        return panel
        
    def create_top_charts(self):
        """Crea los gráficos superiores"""
        panel = QWidget()
        layout = QHBoxLayout(panel)
        
        # Gráfico de estados
        states_group = QGroupBox("📈 Distribución de Estados")
        states_layout = QVBoxLayout()
        self.states_canvas = FigureCanvas(Figure(figsize=(6, 4)))
        states_layout.addWidget(self.states_canvas)
        states_group.setLayout(states_layout)
        
        # Gráfico de recursos
        usage_group = QGroupBox("📊 Uso de Recursos")
        usage_layout = QVBoxLayout()
        self.usage_canvas = FigureCanvas(Figure(figsize=(6, 4)))
        usage_layout.addWidget(self.usage_canvas)
        usage_group.setLayout(usage_layout)
        
        layout.addWidget(states_group)
        layout.addWidget(usage_group)
        
        return panel
        
    def create_bottom_panel(self):
        """Crea el panel inferior con grafo y registro"""
        panel = QWidget()
        layout = QHBoxLayout(panel)
        
        # Grafo animado
        graph_group = QGroupBox("🕸️ Grafo de Espera en Tiempo Real")
        graph_layout = QVBoxLayout()
        self.graph_canvas = AnimatedGraph()
        graph_layout.addWidget(self.graph_canvas)
        graph_group.setLayout(graph_layout)
        
        # Registro con filtros
        log_group = QGroupBox("📝 Registro de Eventos")
        log_layout = QVBoxLayout()
        
        # Barra de filtros
        filter_layout = QHBoxLayout()
        self.event_filter = QComboBox()
        self.event_filter.addItems(["Todos", "REQUEST", "RELEASE", "COMPUTE", "DEADLOCK", "ABORT"])
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Buscar en registro...")
        
        filter_layout.addWidget(QLabel("Filtrar:"))
        filter_layout.addWidget(self.event_filter)
        filter_layout.addWidget(self.search_box)
        filter_layout.addStretch()
        
        log_layout.addLayout(filter_layout)
        
        self.log_box = QTextEdit()
        self.log_box.setFont(QFont("Consolas", 9))
        log_layout.addWidget(self.log_box)
        
        log_group.setLayout(log_layout)
        
        layout.addWidget(graph_group, 2)
        layout.addWidget(log_group, 1)
        
        return panel
        
    def show_config_dialog(self):
        """Muestra el diálogo de configuración"""
        dialog = ConfigurationDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            mode_index = dialog.mode_combo.currentIndex()
            if mode_index == 0:  # Cargar archivo
                if dialog.config_path and dialog.events_path:
                    self.load_config_file(dialog.config_path)
                    self.load_events_file(dialog.events_path)
            elif mode_index == 1:  # Manual
                self.generate_manual_config(
                    dialog.process_count.value(),
                    dialog.resource_count.value(),
                    dialog.event_count.value()
                )
            else:  # Automático
                self.generate_auto_config()
                
    def generate_manual_config(self, process_count, resource_count, event_count):
        """Genera configuración manual"""
        # Crear configuración básica
        config = {
            "mode": "deteccion",
            "victim_policy": "menor_trabajo_hecho",
            "detection_interval": 1,
            "processes": [],
            "resources": []
        }
        
        # Generar procesos
        for i in range(process_count):
            config["processes"].append({"pid": f"P{i+1}", "priority": random.randint(1, 3)})
            
        # Generar recursos
        for i in range(resource_count):
            config["resources"].append({"rid": f"R{i+1}", "instances": random.randint(1, 3)})
            
        # Guardar configuración temporal
        with open("temp_config.json", "w") as f:
            json.dump(config, f, indent=2)
            
        self.load_config_file("temp_config.json")
        
        # Generar eventos aleatorios
        events = []
        event_types = ["REQUEST", "RELEASE", "COMPUTE"]
        
        for i in range(event_count):
            event_type = random.choice(event_types)
            process = random.choice(config["processes"])["pid"]
            resource = random.choice(config["resources"])["rid"] if event_type != "COMPUTE" else ""
            amount = random.randint(1, 2) if event_type != "COMPUTE" else random.randint(1, 3)
            
            events.append({
                "type": event_type,
                "process": process,
                "resource": resource,
                "amount_or_time": amount
            })
            
        # Guardar eventos temporales
        with open("temp_events.csv", "w", newline='') as f:
            writer = csv.DictWriter(f, fieldnames=["type", "process", "resource", "amount_or_time"])
            writer.writeheader()
            writer.writerows(events)
            
        self.load_events_file("temp_events.csv")
        
    def generate_auto_config(self):
        """Genera configuración automática"""
        self.generate_manual_config(
            random.randint(3, 6),
            random.randint(2, 4),
            random.randint(10, 20)
        )
        
    def load_config_file(self, path):
        """Carga archivo de configuración"""
        try:
            self.state = load_config(path)
            self.show_state()
            self.update_visualizations()
            if self.animation_enabled:
                self.graph_canvas.start_animation()
            self.status_bar.showMessage("✅ Configuración cargada correctamente", 3000)
            
            # Mostrar visión general
            self.details_panel.show_system_overview(self.state)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error cargando configuración: {str(e)}")
            
    def load_events_file(self, path):
        """Carga archivo de eventos"""
        try:
            self.events = load_events(path)
            self.status_bar.showMessage("✅ Eventos cargados correctamente", 3000)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error cargando eventos: {str(e)}")
            
    def run_sim(self):
        """Ejecuta la simulación"""
        if not self.state or not self.events:
            QMessageBox.warning(self, "Advertencia", "Debe cargar configuración y eventos primero.")
            return
            
        # Limpiar registro anterior
        self.log_box.clear()
        
        # Ejecutar simulación
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            run_simulation(self.state, self.events)
            
        result = buffer.getvalue()
        self.full_log_text = result.strip()
        self.log_box.setPlainText(self.full_log_text)
        self.show_state()
        self.update_visualizations()
        self.update_system_health()
        
        # Actualizar panel de detalles
        self.details_panel.show_system_overview(self.state)
        
    def step_simulation(self):
        """Ejecuta un solo paso de la simulación"""
        if not self.state or not self.events:
            QMessageBox.warning(self, "Advertencia", "Debe cargar configuración y eventos primero.")
            return
            
        # Implementación básica de paso a paso
        # En una implementación real, esto ejecutaría solo un evento a la vez
        self.status_bar.showMessage("Modo paso a paso: ejecutando siguiente evento...")
        # Por ahora, simplemente ejecutamos la simulación completa
        self.run_sim()

    def reset_simulation(self):
        """Reinicia la simulación"""
        self.state = None
        self.events = []
        self.log_box.clear()
        self.full_log_text = ""
        self.update_visualizations()
        self.status_bar.showMessage("Simulación reiniciada")
        
        # Restablecer panel de detalles
        self.details_panel.header_label.setText("Detalles")
        self.details_panel.info_text.clear()
        self.details_panel.history_list.clear()
        self.details_panel.stats_text.clear()
        
    def show_default_overview(self):
        """Muestra la visión general por defecto"""
        if hasattr(self, 'details_panel'):
            if self.state:
                self.details_panel.show_system_overview(self.state)
            else:
                self.details_panel.info_text.setHtml("""
                    <h3>Bienvenido al Simulador de Interbloqueos</h3>
                    <p>Para comenzar:</p>
                    <ol>
                        <li>Haga clic en <b>Configuración</b> para cargar o generar una simulación</li>
                        <li>Haga clic en <b>Ejecutar</b> para iniciar la simulación</li>
                        <li>Use los filtros para analizar eventos específicos</li>
                        <li>Haga clic en elementos del grafo o doble clic en el registro para ver detalles</li>
                    </ol>
                """)
        
    def show_state(self):
        """Muestra el estado actual del sistema"""
        if not self.state:
            return
            
        # Actualizar badges
        total_processes = len(self.state.processes)
        blocked = len(self.state.blocked_processes)
        aborted = len(getattr(self.state, 'aborted_processes', set()))
        
        self.processes_badge.setText(f"Procesos: {total_processes}")
        self.blocked_badge.setText(f"Bloqueados: {blocked}")
        self.aborted_badge.setText(f"Abortados: {aborted}")
        
        # Aplicar colores a los badges
        self.update_badge_colors()
        
    def update_badge_colors(self):
        """Actualiza los colores de los badges según el estado"""
        if not self.state:
            return
            
        blocked = len(self.state.blocked_processes)
        aborted = len(getattr(self.state, 'aborted_processes', set()))
        
        # Colores según el estado
        blocked_style = "color: #dc3545; font-weight: bold;" if blocked > 0 else "color: #6c757d;"
        aborted_style = "color: #dc3545; font-weight: bold;" if aborted > 0 else "color: #6c757d;"
        
        self.blocked_badge.setStyleSheet(blocked_style)
        self.aborted_badge.setStyleSheet(aborted_style)
        
    def update_visualizations(self):
        """Actualiza todas las visualizaciones"""
        if not self.state:
            return
            
        self.update_states_chart()
        self.update_usage_chart()
        self.graph_canvas.draw_graph(self.state)
        self.update_system_health()
        
    def update_states_chart(self):
        """Actualiza el gráfico de estados"""
        fig = self.states_canvas.figure
        fig.clear()
        
        if not self.state:
            ax = fig.add_subplot(111)
            ax.text(0.5, 0.5, 'Cargue la configuración\npara ver los datos', 
                   ha='center', va='center', transform=ax.transAxes, fontsize=12)
            ax.set_title('Distribución de Estados de Procesos')
            self.states_canvas.draw()
            return
            
        # Calcular conteos de estados
        active = 0
        blocked = 0
        aborted = 0
        
        for proc in self.state.processes.values():
            if hasattr(self.state, 'aborted_processes') and proc.pid in self.state.aborted_processes:
                aborted += 1
            elif proc.pid in self.state.blocked_processes:
                blocked += 1
            else:
                active += 1
                
        # Crear gráfico
        ax = fig.add_subplot(111)
        labels = ['Activos', 'Bloqueados', 'Abortados']
        sizes = [active, blocked, aborted]
        colors = ['#28a745', '#ffc107', '#dc3545']
        
        if sum(sizes) > 0:
            wedges, texts, autotexts = ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%',
                                            startangle=90, shadow=True)
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
        else:
            ax.text(0.5, 0.5, 'No hay procesos', ha='center', va='center', transform=ax.transAxes)
            
        ax.set_title('Distribución de Estados de Procesos', fontweight='bold')
        self.states_canvas.draw()
        
    def update_usage_chart(self):
        """Actualiza el gráfico de uso de recursos"""
        fig = self.usage_canvas.figure
        fig.clear()
        
        if not self.state or not self.state.resources:
            ax = fig.add_subplot(111)
            ax.text(0.5, 0.5, 'Cargue la configuración\npara ver los datos', 
                   ha='center', va='center', transform=ax.transAxes, fontsize=12)
            ax.set_title('Uso de Recursos del Sistema')
            self.usage_canvas.draw()
            return
            
        # Preparar datos
        resources = list(self.state.resources.keys())
        total_instances = [r.total_instances for r in self.state.resources.values()]
        available_instances = [r.available_instances for r in self.state.resources.values()]
        used_instances = [total - available for total, available in zip(total_instances, available_instances)]
        
        ax = fig.add_subplot(111)
        x = range(len(resources))
        
        # Barras
        bars_used = ax.bar(x, used_instances, label='En Uso', color='#dc3545', alpha=0.8)
        bars_avail = ax.bar(x, available_instances, bottom=used_instances, label='Disponibles', color='#28a745', alpha=0.8)
        
        # Personalización
        ax.set_xlabel('Recursos')
        ax.set_ylabel('Instancias')
        ax.set_title('Uso de Recursos del Sistema', fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(resources)
        ax.legend()
        
        # Añadir valores en las barras
        for i, (avail, used) in enumerate(zip(available_instances, used_instances)):
            if used > 0:
                ax.text(i, used/2, str(used), ha='center', va='center', fontweight='bold', color='white')
            if avail > 0:
                ax.text(i, used + avail/2, str(avail), ha='center', va='center', fontweight='bold', color='white')
                
        self.usage_canvas.draw()
        
    def update_system_health(self):
        """Actualiza la salud del sistema"""
        if not self.state:
            return
            
        total_processes = len(self.state.processes)
        blocked = len(self.state.blocked_processes)
        aborted = len(getattr(self.state, 'aborted_processes', set()))
        
        # Calcular salud del sistema (0-100%)
        health = 100
        if blocked > 0:
            health -= (blocked / total_processes) * 50
        if aborted > 0:
            health -= (aborted / total_processes) * 30
            
        health = max(0, health)
        
        # Actualizar barra de salud
        self.health_bar.setValue(int(health))
        
        # Cambiar color según salud
        if health > 70:
            color = "#28a745"
        elif health > 40:
            color = "#ffc107"
        else:
            color = "#dc3545"
            
        self.health_bar.setStyleSheet(f"""
            QProgressBar {{
                border: 1px solid grey;
                border-radius: 5px;
                text-align: center;
            }}
            QProgressBar::chunk {{
                background-color: {color};
                width: 20px;
            }}
        """)
        
    def change_theme(self, theme_name):
        """Cambia el tema visual"""
        self.current_theme = theme_name.lower()
        self.apply_theme()
        
    def apply_theme(self):
        """Aplica el tema actual"""
        if self.current_theme == "oscuro":
            self.apply_dark_theme()
        elif self.current_theme == "pastel":
            self.apply_pastel_theme()
        else:
            self.apply_light_theme()
            
    def apply_light_theme(self):
        """Aplica tema claro"""
        self.setStyleSheet("""
            QMainWindow, QWidget {
                background-color: #f8f9fa;
                color: #212529;
            }
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 5px 10px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #dee2e6;
                border-radius: 5px;
                margin-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QTextEdit, QTableWidget {
                border: 1px solid #ced4da;
                border-radius: 4px;
                background-color: white;
            }
            QProgressBar {
                border: 1px solid #ced4da;
                border-radius: 4px;
                background-color: #e9ecef;
            }
            QProgressBar::chunk {
                background-color: #007bff;
            }
        """)
        
    def apply_dark_theme(self):
        """Aplica tema oscuro"""
        self.setStyleSheet("""
            QMainWindow, QWidget {
                background-color: #1a1d23;
                color: #e9ecef;
            }
            QPushButton {
                background-color: #0d6efd;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 5px 10px;
            }
            QPushButton:hover {
                background-color: #0b5ed7;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #444c56;
                border-radius: 5px;
                margin-top: 10px;
                color: #adb5bd;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #adb5bd;
            }
            QTextEdit, QTableWidget {
                border: 1px solid #444c56;
                border-radius: 4px;
                background-color: #2d333b;
                color: #adb5bd;
            }
            QProgressBar {
                border: 1px solid #444c56;
                border-radius: 4px;
                background-color: #373e47;
            }
            QProgressBar::chunk {
                background-color: #0d6efd;
            }
        """)
        
    def apply_pastel_theme(self):
        """Aplica tema pastel"""
        self.setStyleSheet("""
            QMainWindow, QWidget {
                background-color: #f4f9f9;
                color: #4b6584;
            }
            QPushButton {
                background-color: #a3e4d7;
                color: #2d3436;
                border: none;
                border-radius: 4px;
                padding: 5px 10px;
            }
            QPushButton:hover {
                background-color: #81d8c7;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #d1d8e0;
                border-radius: 5px;
                margin-top: 10px;
                color: #4b6584;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #4b6584;
            }
            QTextEdit, QTableWidget {
                border: 1px solid #ced4da;
                border-radius: 4px;
                background-color: white;
                color: #4b6584;
            }
            QProgressBar {
                border: 1px solid #ced4da;
                border-radius: 4px;
                background-color: #e9ecef;
            }
            QProgressBar::chunk {
                background-color: #a3e4d7;
            }
        """)
        
    def toggle_details_panel(self):
        """Muestra/oculta el panel de detalles"""
        self.details_panel_visible = not self.details_panel_visible
        self.details_panel.setVisible(self.details_panel_visible)
        if self.details_panel_visible:
            self.toggle_details_btn.setText("📊 Ocultar Detalles")
        else:
            self.toggle_details_btn.setText("📊 Mostrar Detalles")
        
    def toggle_animations(self):
        """Activa/desactiva las animaciones"""
        self.animation_enabled = not self.animation_enabled
        if self.animation_enabled:
            self.graph_canvas.start_animation()
            self.toggle_animation_btn.setText("✨ Animaciones: ON")
        else:
            self.graph_canvas.stop_animation()
            self.toggle_animation_btn.setText("✨ Animaciones: OFF")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Establecer estilo de aplicación
    app.setStyle('Fusion')
    
    gui = DeadlockGUI()
    gui.show()
    
    sys.exit(app.exec_())