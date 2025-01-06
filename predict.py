import pandas as pd
import joblib
import os
import glob
import shutil
import time
from tkinter import messagebox
from logger import system_logger

def load_models():
    """Cargar modelos y encoders guardados"""
    try:
        models = joblib.load('modelos/models.joblib')
        encoders = joblib.load('modelos/encoders.joblib')
        system_logger.logger.info("Models and encoders loaded successfully")
        return models, encoders
    except Exception as e:
        system_logger.log_error(e, "Error loading models and encoders")
        raise

def validate_elementos(df_input):
    """Validar que los elementos existan en el archivo de entrenamiento"""
    try:
        df_train = pd.read_csv('entrenador/entrenador001.csv')
        elementos_train = set(df_train['Elemento'].unique())
        elementos_input = set(df_input['Elemento'].unique())
        
        elementos_faltantes = elementos_input - elementos_train
        
        if elementos_faltantes:
            mensaje = "Los siguientes elementos no existen en el archivo de entrenamiento:\n"
            mensaje += "\n".join(sorted(elementos_faltantes))
            system_logger.logger.warning(mensaje)
            return False, mensaje, elementos_faltantes
        
        return True, "", set()
    except Exception as e:
        system_logger.log_error(e, "Error validando elementos")
        raise

def predict_single(elemento, models, encoders):
    """Hacer predicción para un solo elemento"""
    start_time = time.time()
    try:
        # Verificar si el elemento existe en el entrenamiento
        df_train = pd.read_csv('entrenador/entrenador001.csv')
        if elemento not in df_train['Elemento'].unique():
            # Retornar diccionario con valores vacíos para todas las columnas
            predictions = {column: "" for column in models.keys() if column != 'Elemento'}
            execution_time = time.time() - start_time
            system_logger.logger.warning(f"Elemento no encontrado en entrenamiento: {elemento}")
            return predictions
            
        elemento_encoded = encoders['input'].transform([elemento])
        
        predictions = {}
        for column, model in models.items():
            if column != 'Elemento':
                pred_encoded = model.predict([elemento_encoded])[0]
                predictions[column] = encoders['output'][column].inverse_transform([pred_encoded])[0]
        
        execution_time = time.time() - start_time
        system_logger.log_prediction(elemento, predictions, execution_time)
        return predictions
    except Exception as e:
        system_logger.log_error(e, f"Error predicting for elemento: {elemento}")
        raise

def get_training_combinations(elemento):
    """Obtener todas las combinaciones existentes del elemento en datos de entrenamiento"""
    try:
        df_train = pd.read_csv('entrenador/entrenador001.csv')
        return df_train[df_train['Elemento'] == elemento].to_dict('records')
    except Exception as e:
        system_logger.log_error(e, "Error getting training combinations")
        raise

def get_input_file():
    """Obtener el primer archivo CSV o XLSX de la carpeta entrada"""
    try:
        input_files = glob.glob('entrada/*.csv') + glob.glob('entrada/*.xlsx')
        if not input_files:
            raise FileNotFoundError("No se encontraron archivos CSV o XLSX en la carpeta entrada")
        return input_files[0]
    except Exception as e:
        system_logger.log_error(e, "Error getting input file")
        raise

def move_to_backup(input_file):
    """Mover el archivo de entrada a la carpeta backup"""
    try:
        filename = os.path.basename(input_file)
        backup_path = os.path.join('backup', filename)
        shutil.move(input_file, backup_path)
        system_logger.logger.info(f"File moved to backup: {filename}")
    except Exception as e:
        system_logger.log_error(e, f"Error moving file to backup: {input_file}")
        raise

def read_input_file(file_path):
    """Leer archivo de entrada en formato CSV o XLSX"""
    try:
        if file_path.endswith('.csv'):
            return pd.read_csv(file_path)
        elif file_path.endswith('.xlsx'):
            return pd.read_excel(file_path)
        else:
            raise ValueError("Formato de archivo no soportado")
    except Exception as e:
        system_logger.log_error(e, f"Error reading input file: {file_path}")
        raise

def save_predictions(df_predictions, output_path):
    """Guardar predicciones en el mismo formato que el archivo de entrada"""
    try:
        if output_path.endswith('.csv'):
            df_predictions.to_csv(output_path, index=False)
        elif output_path.endswith('.xlsx'):
            df_predictions.to_excel(output_path, index=False)
        system_logger.logger.info(f"Predictions saved to: {output_path}")
    except Exception as e:
        system_logger.log_error(e, f"Error saving predictions to: {output_path}")
        raise

def main():
    start_time = time.time()
    system_logger.log_performance()
    
    try:
        # Obtener archivo de entrada
        input_file = get_input_file()
        df_input = read_input_file(input_file)
        input_filename = os.path.basename(input_file)
        
        # Validar elementos antes de procesar
        valid, mensaje, elementos_faltantes = validate_elementos(df_input)
        if not valid:
            try:
                messagebox.showwarning("Elementos No Encontrados", mensaje)
            except:
                system_logger.logger.warning(mensaje)
            # Registrar elementos faltantes para el dashboard
            system_logger.log_missing_elements(elementos_faltantes)
        
        # Cargar modelos y encoders
        models, encoders = load_models()
        
        # Realizar predicciones
        results = []
        for _, row in df_input.iterrows():
            elemento = row['Elemento']
            # Obtener todas las combinaciones existentes del elemento en el entrenamiento
            combinations = get_training_combinations(elemento)
            
            if combinations:
                # Si existen combinaciones en el entrenamiento, usar todas
                for combination in combinations:
                    results.append(combination)
            else:
                # Si no existe en el entrenamiento, generar una fila con campos vacíos
                predictions = {column: "" for column in models.keys() if column != 'Elemento'}
                predictions['Elemento'] = elemento
                results.append(predictions)
        
        # Crear DataFrame con resultados
        df_predictions = pd.DataFrame(results)
        
        # Reordenar columnas para mantener el mismo orden que el archivo original
        if not df_predictions.empty:
            column_order = ['Elemento'] + [col for col in df_input.columns if col != 'Elemento']
            df_predictions = df_predictions[column_order]
        
        # Guardar predicciones
        output_file = os.path.join('salida', os.path.basename(input_file))
        save_predictions(df_predictions, output_file)
        
        # Registrar métricas
        total_lines = len(df_predictions)
        system_logger.log_file_processed(input_filename, len(df_input), total_lines)
        
        # Mover archivo de entrada a backup
        move_to_backup(input_file)
        
        # Generar dashboard actualizado
        dashboard_path = system_logger.generate_html_dashboard()
        system_logger.logger.info(f"Dashboard actualizado en: {dashboard_path}")
        
        execution_time = time.time() - start_time
        system_logger.logger.info(f"Total execution time: {execution_time:.2f} seconds")
        
    except Exception as e:
        system_logger.log_error(e, "Error in main execution")
        raise

if __name__ == "__main__":
    main()
