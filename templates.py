import json
import os
from pathlib import Path

class TemplateManager:
    def __init__(self):
        self.templates_dir = Path('templates')
        self.templates_dir.mkdir(exist_ok=True)
        self.templates_file = self.templates_dir / 'templates.json'
        self.load_templates()
    
    def load_templates(self):
        """Cargar plantillas existentes"""
        if self.templates_file.exists():
            with open(self.templates_file, 'r') as f:
                self.templates = json.load(f)
        else:
            self.templates = {
                'default': {
                    'name': 'Plantilla Predeterminada',
                    'description': 'Plantilla básica para archivos CSV/XLSX',
                    'required_columns': ['Elemento'],
                    'optional_columns': [],
                    'validation_rules': {
                        'Elemento': {
                            'type': 'string',
                            'required': True,
                            'min_length': 1
                        }
                    }
                }
            }
            self.save_templates()
    
    def save_templates(self):
        """Guardar plantillas en archivo"""
        with open(self.templates_file, 'w') as f:
            json.dump(self.templates, f, indent=4)
    
    def add_template(self, name, description, required_columns, optional_columns=None, validation_rules=None):
        """Agregar nueva plantilla"""
        template_id = name.lower().replace(' ', '_')
        self.templates[template_id] = {
            'name': name,
            'description': description,
            'required_columns': required_columns,
            'optional_columns': optional_columns or [],
            'validation_rules': validation_rules or {}
        }
        self.save_templates()
        return template_id
    
    def validate_file(self, filepath, template_id='default'):
        """Validar archivo contra una plantilla"""
        import pandas as pd
        
        template = self.templates.get(template_id)
        if not template:
            raise ValueError(f"Plantilla '{template_id}' no encontrada")
        
        # Leer archivo
        if filepath.endswith('.csv'):
            df = pd.read_csv(filepath)
        elif filepath.endswith('.xlsx'):
            df = pd.read_excel(filepath)
        else:
            raise ValueError("Formato de archivo no soportado")
        
        # Validar columnas requeridas
        missing_columns = set(template['required_columns']) - set(df.columns)
        if missing_columns:
            raise ValueError(f"Columnas requeridas faltantes: {missing_columns}")
        
        # Validar reglas
        errors = []
        for column, rules in template.get('validation_rules', {}).items():
            if column in df.columns:
                # Validar tipo de datos
                if rules.get('type') == 'string':
                    non_string = df[df[column].apply(lambda x: not isinstance(x, str))][column]
                    if not non_string.empty:
                        errors.append(f"Columna '{column}' debe contener solo texto")
                
                # Validar requerido
                if rules.get('required'):
                    if df[column].isnull().any():
                        errors.append(f"Columna '{column}' no puede contener valores vacíos")
                
                # Validar longitud mínima
                if 'min_length' in rules:
                    min_len = rules['min_length']
                    short_values = df[df[column].str.len() < min_len][column]
                    if not short_values.empty:
                        errors.append(f"Columna '{column}' debe tener al menos {min_len} caracteres")
        
        if errors:
            raise ValueError("Errores de validación:\n" + "\n".join(errors))
        
        return True
    
    def get_template_list(self):
        """Obtener lista de plantillas disponibles"""
        return [(id, template['name']) for id, template in self.templates.items()]
    
    def get_template(self, template_id):
        """Obtener una plantilla específica"""
        return self.templates.get(template_id)
