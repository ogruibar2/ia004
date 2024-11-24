import pandas as pd
import numpy as np

# Cargar datos
df_train = pd.read_csv('entrenador/entrenador001.csv')
df_input = pd.read_csv('entrada/primero.csv')

# Limpiar datos
df_train = df_train.dropna(subset=['Elemento'])
df_input = df_input.dropna(subset=['Elemento'])

# Generar predicciones
predictions = []

# Para cada elemento en el archivo de entrada
for elemento in df_input['Elemento']:
    # Obtener todas las filas correspondientes a este elemento del archivo de entrenamiento
    elemento_rows = df_train[df_train['Elemento'] == elemento]
    
    if not elemento_rows.empty:
        # Si encontramos datos para este elemento, usar todas sus variaciones
        predictions.extend(elemento_rows.to_dict('records'))
    else:
        # Si no hay datos específicos, usar los valores más comunes generales
        common_values = df_train.mode().iloc[0]
        predictions.append(common_values.to_dict())

# Crear DataFrame con predicciones
df_predictions = pd.DataFrame(predictions)

# Reordenar columnas para mantener el mismo orden que el archivo original
column_order = df_input.columns.tolist()
df_predictions = df_predictions[column_order]

# Eliminar filas completamente vacías
df_predictions = df_predictions.dropna(how='all')

# Guardar resultados
df_predictions.to_csv('salida/predicciones.csv', index=False)
