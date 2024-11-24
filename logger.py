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
        self.metrics = self._load_metrics()

    def _load_metrics(self):
        if self.metrics_file.exists():
            with open(self.metrics_file, 'r') as f:
                return json.load(f)
        return {
            'total_predictions': 0,
            'total_files_processed': 0,
            'processing_times': [],
            'error_count': 0,
            'last_execution': None,
            'model_usage': {},
            'memory_usage': []
        }

    def _save_metrics(self):
        with open(self.metrics_file, 'w') as f:
            json.dump(self.metrics, f, indent=4)

    def log_prediction(self, elemento, predictions, execution_time):
        """Log individual prediction details"""
        self.logger.info(f"Prediction made for elemento: {elemento}")
        self.metrics['total_predictions'] += 1
        self.metrics['processing_times'].append(execution_time)
        self._save_metrics()

    def log_file_processed(self, filename, num_predictions):
        """Log file processing completion"""
        self.metrics['total_files_processed'] += 1
        self.metrics['last_execution'] = datetime.now().isoformat()
        self.logger.info(f"Processed file {filename} with {num_predictions} predictions")
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
        
        dashboard_data = {
            'total_predictions': self.metrics['total_predictions'],
            'total_files': self.metrics['total_files_processed'],
            'average_processing_time': round(avg_time, 3),
            'error_rate': round(self.metrics['error_count'] / max(self.metrics['total_predictions'], 1) * 100, 2),
            'last_execution': self.metrics['last_execution'],
            'memory_usage': self.metrics['memory_usage'][-1]['memory_mb'] if self.metrics['memory_usage'] else 0
        }
        
        return dashboard_data

    def generate_html_dashboard(self):
        """Generate HTML dashboard"""
        data = self.generate_dashboard_data()
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>System Metrics Dashboard</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .metric-card {{
                    background: #f5f5f5;
                    border-radius: 8px;
                    padding: 15px;
                    margin: 10px;
                    display: inline-block;
                    width: 200px;
                    text-align: center;
                }}
                .metric-value {{ font-size: 24px; font-weight: bold; color: #2196F3; }}
                .metric-label {{ color: #666; }}
            </style>
        </head>
        <body>
            <h1>System Metrics Dashboard</h1>
            
            <div class="metric-card">
                <div class="metric-value">{data['total_predictions']}</div>
                <div class="metric-label">Total Predictions</div>
            </div>
            
            <div class="metric-card">
                <div class="metric-value">{data['total_files']}</div>
                <div class="metric-label">Files Processed</div>
            </div>
            
            <div class="metric-card">
                <div class="metric-value">{data['average_processing_time']}s</div>
                <div class="metric-label">Avg Processing Time</div>
            </div>
            
            <div class="metric-card">
                <div class="metric-value">{data['error_rate']}%</div>
                <div class="metric-label">Error Rate</div>
            </div>
            
            <div class="metric-card">
                <div class="metric-value">{round(data['memory_usage'], 2)} MB</div>
                <div class="metric-label">Memory Usage</div>
            </div>
            
            <div class="metric-card">
                <div class="metric-value">{data['last_execution'].split('T')[0] if data['last_execution'] else 'Never'}</div>
                <div class="metric-label">Last Execution</div>
            </div>
        </body>
        </html>
        """
        
        dashboard_path = self.logs_dir / 'dashboard.html'
        with open(dashboard_path, 'w') as f:
            f.write(html_content)
        
        return dashboard_path

system_logger = SystemLogger()
