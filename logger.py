import logging
import time
import json
import os
from datetime import datetime
import psutil
import pandas as pd
from pathlib import Path

class SystemLogger:
    def __init__(self):
        # Create logs directory if it doesn't exist
        self.logs_dir = Path('logs')
        self.logs_dir.mkdir(exist_ok=True)
        
        # Configure main logger
        self.logger = logging.getLogger('system_logger')
        self.logger.setLevel(logging.INFO)
        
        # File handler for general logs
        general_handler = logging.FileHandler(self.logs_dir / 'system.log')
        general_handler.setFormatter(
            logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        )
        self.logger.addHandler(general_handler)
        
        # File handler for errors
        error_handler = logging.FileHandler(self.logs_dir / 'errors.log')
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(
            logging.Formatter('%(asctime)s - %(levelname)s - %(message)s\nStack Trace: %(exc_info)s')
        )
        self.logger.addHandler(error_handler)
        
        # Performance metrics
        self.metrics_file = self.logs_dir / 'metrics.json'
        self.missing_elements_file = self.logs_dir / 'missing_elements.json'
        self.metrics = self._load_metrics()
        self.missing_elements = self._load_missing_elements()
        
        # Migrar métricas si es necesario
        self._migrate_metrics()

    def _load_metrics(self):
        if self.metrics_file.exists():
            with open(self.metrics_file, 'r') as f:
                metrics = json.load(f)
                # Asegurar que lines_per_file existe
                if 'lines_per_file' not in metrics:
                    metrics['lines_per_file'] = []
                return metrics
        return {
            'total_predictions': 0,
            'total_files_processed': 0,
            'processing_times': [],
            'error_count': 0,
            'last_execution': None,
            'model_usage': {},
            'memory_usage': [],
            'lines_per_file': []
        }

    def _load_missing_elements(self):
        if self.missing_elements_file.exists():
            with open(self.missing_elements_file, 'r') as f:
                return json.load(f)
        return {
            'elements': {},  # Diccionario para almacenar elementos y fechas
            'total_count': 0
        }

    def _save_missing_elements(self):
        with open(self.missing_elements_file, 'w') as f:
            json.dump(self.missing_elements, f, indent=4)

    def log_missing_elements(self, elementos_faltantes):
        """Registrar elementos faltantes con fecha"""
        current_date = datetime.now().isoformat()
        
        for elemento in elementos_faltantes:
            if elemento not in self.missing_elements['elements']:
                self.missing_elements['elements'][elemento] = {
                    'first_seen': current_date,
                    'last_seen': current_date,
                    'count': 1
                }
            else:
                self.missing_elements['elements'][elemento]['last_seen'] = current_date
                self.missing_elements['elements'][elemento]['count'] += 1
        
        self.missing_elements['total_count'] = len(self.missing_elements['elements'])
        self._save_missing_elements()

    def log_prediction(self, elemento, predictions, execution_time):
        """Log individual prediction details"""
        self.logger.info(f"Prediction made for elemento: {elemento}")
        self.metrics['total_predictions'] += 1
        self.metrics['processing_times'].append(execution_time)
        self._save_metrics()

    def log_file_processed(self, filename, num_predictions, lines_processed):
        """Log file processing completion"""
        self.metrics['total_files_processed'] += 1
        self.metrics['last_execution'] = datetime.now().isoformat()
        if 'lines_per_file' not in self.metrics:
            self.metrics['lines_per_file'] = []
        self.metrics['lines_per_file'].append(lines_processed)
        self.logger.info(f"Processed file {filename} with {num_predictions} predictions and {lines_processed} total lines")
        self._save_metrics()

    def log_error(self, error, context=None):
        """Log error with context"""
        self.metrics['error_count'] += 1
        self.logger.error(f"Error: {str(error)}", exc_info=True, extra={'context': context})
        self._save_metrics()

    def log_performance(self):
        """Log system performance metrics"""
        memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        self.metrics['memory_usage'].append({
            'timestamp': datetime.now().isoformat(),
            'memory_mb': memory
        })
        self._save_metrics()

    def generate_dashboard_data(self):
        """Generate data for the dashboard"""
        avg_time = sum(self.metrics['processing_times']) / len(self.metrics['processing_times']) if self.metrics['processing_times'] else 0
        
        # Ordenar elementos faltantes por fecha de último avistamiento
        missing_elements_sorted = sorted(
            self.missing_elements['elements'].items(),
            key=lambda x: x[1]['last_seen'],
            reverse=True
        )
        
        dashboard_data = {
            'total_predictions': self.metrics['total_predictions'],
            'total_files': self.metrics['total_files_processed'],
            'average_processing_time': round(avg_time, 3),
            'lines_processed': sum(self.metrics['lines_per_file']) if 'lines_per_file' in self.metrics else 0,
            'last_execution': self.metrics['last_execution'],
            'memory_usage': self.metrics['memory_usage'][-1]['memory_mb'] if self.metrics['memory_usage'] else 0,
            'missing_elements': {
                'total': self.missing_elements['total_count'],
                'elements': missing_elements_sorted
            }
        }
        
        return dashboard_data

    def generate_html_dashboard(self):
        """Generate HTML dashboard"""
        data = self.generate_dashboard_data()
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Dashboard de Procesamiento</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .metric {{ background: #f5f5f5; padding: 15px; margin: 10px 0; border-radius: 5px; }}
                .metric h3 {{ margin: 0 0 10px 0; }}
                .missing-elements {{ margin-top: 20px; }}
                .missing-element {{ background: #fff3f3; padding: 10px; margin: 5px 0; border-left: 3px solid #ff4444; }}
                .timestamp {{ color: #666; font-size: 0.9em; }}
            </style>
        </head>
        <body>
            <h1>Dashboard de Procesamiento</h1>
            
            <div class="metric">
                <h3>Métricas Generales</h3>
                <p>Total de Predicciones: {data['total_predictions']}</p>
                <p>Archivos Procesados: {data['total_files']}</p>
                <p>Predicciones Procesadas: {data['lines_processed']}</p>
                <p>Tiempo Promedio de Procesamiento: {data['average_processing_time']}s</p>
                <p>Última Ejecución: {data['last_execution']}</p>
                <p>Uso de Memoria: {round(data['memory_usage'], 2)} MB</p>
            </div>
            
            <div class="metric missing-elements">
                <h3>Elementos Faltantes en Entrenamiento ({data['missing_elements']['total']})</h3>
                """
        
        # Agregar cada elemento faltante al dashboard
        for elemento, info in data['missing_elements']['elements']:
            html_content += f"""
                <div class="missing-element">
                    <strong>{elemento}</strong><br>
                    <span class="timestamp">
                        Primer avistamiento: {info['first_seen']}<br>
                        Último avistamiento: {info['last_seen']}<br>
                        Veces encontrado: {info['count']}
                    </span>
                </div>
            """
        
        html_content += """
            </div>
        </body>
        </html>
        """
        
        # Guardar dashboard
        dashboard_path = self.logs_dir / 'dashboard.html'
        with open(dashboard_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return str(dashboard_path)

    def _migrate_metrics(self):
        """Migrar métricas antiguas al nuevo formato"""
        needs_save = False
        
        # Asegurar que todos los campos necesarios existen
        required_fields = {
            'total_predictions': 0,
            'total_files_processed': 0,
            'processing_times': [],
            'error_count': 0,
            'last_execution': None,
            'model_usage': {},
            'memory_usage': [],
            'lines_per_file': []
        }
        
        for field, default_value in required_fields.items():
            if field not in self.metrics:
                self.metrics[field] = default_value
                needs_save = True
        
        if needs_save:
            self._save_metrics()
            self.logger.info("Métricas migradas al nuevo formato")

    def _save_metrics(self):
        with open(self.metrics_file, 'w') as f:
            json.dump(self.metrics, f, indent=4)

system_logger = SystemLogger()
