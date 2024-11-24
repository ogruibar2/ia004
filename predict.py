import pandas as pd
import joblib
import os
import glob
import shutil

def load_models():
    """Cargar modelos y encoders guardados"""
    models = joblib.load('modelos/models.joblib')
    encoders = joblib.load('modelos/encoders.joblib')
    return models, encoders

def predict_single(elemento, models, encoders):
    """Hacer predicción para un solo elemento"""
    elemento_encoded = encoders['input'].transform([elemento])
    
    predictions = {}
    for column, model in models.items():
        if column != 'Elemento':
            pred_encoded = model.predict([elemento_encoded])[0]
            predictions[column] = encoders['output'][column].inverse_transform([pred_encoded])[0]
    
    return predictions

def get_training_combinations(elemento):
    """Obtener todas las combinaciones existentes del elemento en datos de entrenamiento"""
    df_train = pd.read_csv('entrenador/entrenador001.csv')
    return df_train[df_train['Elemento'] == elemento].to_dict('records')

def get_input_file():
    """Obtener el primer archivo CSV de la carpeta entrada"""
    csv_files = glob.glob('entrada/*.csv')
    if not csv_files:
        raise FileNotFoundError("No se encontraron archivos CSV en la carpeta entrada")
    return csv_files[0]

def move_to_backup(input_file):
    """Mover el archivo de entrada a la carpeta backup"""
    filename = os.path.basename(input_file)
    backup_path = os.path.join('backup', filename)
    shutil.move(input_file, backup_path)

def main():
    # Obtener archivo de entrada
    input_file = get_input_file()
    input_filename = os.path.basename(input_file)
    
    # Cargar el archivo de entrada
    df_input = pd.read_csv(input_file)
    df_input = df_input.dropna(subset=['Elemento'])
    
    # Cargar modelos y encoders
    models, encoders = load_models()
    
    # Generar predicciones
    all_predictions = []
    
    for elemento in df_input['Elemento']:
        # Obtener combinaciones existentes del entrenamiento
        combinations = get_training_combinations(elemento)
        
        if combinations:
            # Si existen combinaciones en el entrenamiento, usarlas
            all_predictions.extend(combinations)
        else:
            # Si no existen, usar el modelo para predecir
            pred = predict_single(elemento, models, encoders)
            pred['Elemento'] = elemento
            all_predictions.append(pred)
    
    # Crear DataFrame con predicciones
    df_predictions = pd.DataFrame(all_predictions)
    
    # Reordenar columnas para mantener el mismo orden que el archivo original
    column_order = df_input.columns.tolist()
    df_predictions = df_predictions[column_order]
    
    # Guardar predicciones usando el mismo nombre del archivo de entrada
    output_path = os.path.join('salida', input_filename)
    df_predictions.to_csv(output_path, index=False)
    print(f"Predicciones guardadas en 'salida/{input_filename}'")
    
    # Mover archivo de entrada a backup
    move_to_backup(input_file)
    print(f"Archivo de entrada movido a backup: {input_filename}")

if __name__ == "__main__":
    main()
