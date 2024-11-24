import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
import joblib
import os

# Crear directorio para modelos si no existe
if not os.path.exists('modelos'):
    os.makedirs('modelos')

# Cargar datos de entrenamiento
print("Cargando datos de entrenamiento...")
df_train = pd.read_csv('entrenador/entrenador001.csv')

# Limpiar datos
df_train = df_train.dropna(subset=['Elemento'])

# Separar features y targets
X = df_train[['Elemento']]
target_columns = [col for col in df_train.columns if col != 'Elemento']

# Crear diccionario para almacenar encoders
encoders = {
    'input': LabelEncoder(),
    'output': {}
}

# Entrenar encoder para Elemento
print("Codificando variables categóricas...")
X_encoded = pd.DataFrame()
X_encoded['Elemento'] = encoders['input'].fit_transform(X['Elemento'])

# Crear y entrenar modelos para cada columna objetivo
models = {}
print("Entrenando modelos para cada campo...")

for column in target_columns:
    # Crear encoder para la columna objetivo
    encoders['output'][column] = LabelEncoder()
    
    # Codificar valores objetivo
    y = df_train[column].fillna('MISSING')  # Manejar valores NaN
    y_encoded = encoders['output'][column].fit_transform(y)
    
    # Crear y entrenar modelo
    print(f"Entrenando modelo para: {column}")
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_encoded, y_encoded)
    models[column] = model

# Guardar modelos y encoders
print("Guardando modelos y encoders...")
joblib.dump(models, 'modelos/models.joblib')
joblib.dump(encoders, 'modelos/encoders.joblib')

# Función para hacer predicciones
def predict(elemento):
    # Codificar elemento
    elemento_encoded = encoders['input'].transform([elemento])
    
    # Hacer predicciones para cada campo
    predictions = {}
    for column in target_columns:
        pred_encoded = models[column].predict([elemento_encoded])[0]
        predictions[column] = encoders['output'][column].inverse_transform([pred_encoded])[0]
    
    return predictions

# Función para obtener todas las predicciones posibles
def get_all_predictions(elemento):
    # Obtener todas las filas del elemento en datos de entrenamiento
    elemento_rows = df_train[df_train['Elemento'] == elemento]
    
    if elemento_rows.empty:
        # Si no hay datos, usar el modelo para predecir
        return [predict(elemento)]
    else:
        # Si hay datos, retornar todas las combinaciones existentes
        return elemento_rows.to_dict('records')

print("Modelo entrenado y guardado exitosamente!")

# Probar el modelo con algunos ejemplos
print("\nProbando el modelo con algunos ejemplos:")
test_elementos = df_train['Elemento'].unique()[:3]
for elemento in test_elementos:
    print(f"\nPredicciones para {elemento}:")
    predictions = get_all_predictions(elemento)
    print(f"Número de predicciones: {len(predictions)}")
    print("Primera predicción:", predictions[0])
