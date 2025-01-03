# ProcesadorArchivos

Aplicación de escritorio para procesamiento y predicción de datos basada en modelos de machine learning.

## Estructura del Proyecto

```
ProcesadorArchivos/
├── app.py                 # Aplicación principal (GUI)
├── predict.py             # Módulo de predicción
├── predictor.py           # Funciones core de predicción
├── logger.py             # Sistema de logging
├── config.py             # Manejo de configuración
├── templates.py          # Sistema de plantillas
├── config.json           # Archivo de configuración
├── requirements.txt      # Dependencias del proyecto
├── proceso.ico           # Icono de la aplicación
│
├── entrada/              # Directorio para archivos de entrada
│   └── README.md        # Instrucciones para archivos de entrada
│
├── salida/              # Directorio para archivos procesados
│   └── README.md        # Información sobre archivos de salida
│
├── modelos/             # Modelos entrenados
│   ├── models.joblib    # Modelos de predicción
│   └── encoders.joblib  # Encoders para procesamiento
│
├── logs/                # Archivos de registro
│   ├── system.log      # Log del sistema
│   ├── errors.log      # Log de errores
│   └── dashboard.html  # Dashboard de actividad
│
├── templates/           # Plantillas para procesamiento
│   └── templates.json  # Configuración de plantillas
│
└── entrenador/         # Datos de entrenamiento
    └── entrenador001.csv  # Dataset de entrenamiento
```

## Descripción de Componentes

### Archivos Principales

- **app.py**: Interfaz gráfica principal desarrollada con tkinter.
- **predict.py**: Módulo que maneja la lógica de predicción.
- **predictor.py**: Implementación de algoritmos de predicción.
- **logger.py**: Sistema de logging y generación de dashboard.
- **config.py**: Gestión de configuración de la aplicación.
- **templates.py**: Sistema de plantillas para validación de datos.

### Directorios

- **entrada/**: Carpeta para colocar archivos CSV/XLSX a procesar.
- **salida/**: Almacena los archivos procesados.
- **modelos/**: Contiene los modelos entrenados y encoders.
- **logs/**: Archivos de registro y dashboard.
- **templates/**: Plantillas para diferentes tipos de archivos.
- **entrenador/**: Datos utilizados para entrenamiento.

## Requisitos del Sistema

- Python 3.12 o superior
- Dependencias listadas en requirements.txt

## Instalación

1. Clonar o descargar el repositorio
2. Crear un entorno virtual:
   ```bash
   python -m venv venv
   source venv/bin/activate  # En Linux/Mac
   venv\Scripts\activate     # En Windows
   ```
3. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   ```

## Uso

1. Ejecutar la aplicación:
   ```bash
   python app.py
   ```
2. Seleccionar archivos a procesar desde el botón "Seleccionar Archivos"
3. Elegir una plantilla de procesamiento
4. Hacer clic en "Procesar Archivos"
5. Los resultados se guardarán en la carpeta "salida/"

## Características

- Interfaz gráfica intuitiva
- Procesamiento por lotes
- Sistema de plantillas personalizable
- Validación de datos
- Dashboard de actividad
- Exportación en múltiples formatos (CSV, Excel, JSON)
- Temas claro/oscuro
- Registro detallado de operaciones

## Mantenimiento

- Los archivos de log se rotan automáticamente
- El dashboard se actualiza en tiempo real
- Las plantillas se pueden crear/editar desde la interfaz
- La configuración se guarda automáticamente