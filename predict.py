import pandas as pd
import joblib
import os
import glob
import shutil
import time
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

def predict_single(elemento, models, encoders):
    """Hacer predicción para un solo elemento"""
    start_time = time.time()
    try:
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
        input_filename = os.path.basename(input_file)
        system_logger.logger.info(f"Processing file: entrada/{input_filename}")
        
        # Cargar el archivo de entrada
        df_input = read_input_file(input_file)
        df_input = df_input.dropna(subset=['Elemento'])
        
        # Cargar modelos y encoders
        models, encoders = load_models()
        
        # Generar predicciones
        all_predictions = []
        prediction_count = 0
        
        for elemento in df_input['Elemento']:
            # Obtener combinaciones existentes del entrenamiento
            combinations = get_training_combinations(elemento)
            
            if combinations:
                # Si existen combinaciones en el entrenamiento, usarlas
                all_predictions.extend(combinations)
                prediction_count += len(combinations)
            else:
                # Si no existen, usar el modelo para predecir
                pred = predict_single(elemento, models, encoders)
                pred['Elemento'] = elemento
                all_predictions.append(pred)
                prediction_count += 1
        
        # Crear DataFrame con predicciones
        df_predictions = pd.DataFrame(all_predictions)
        
        # Reordenar columnas para mantener el mismo orden que el archivo original
        column_order = df_input.columns.tolist()
        df_predictions = df_predictions[column_order]
        
        # Guardar predicciones usando el mismo nombre del archivo de entrada
        output_path = os.path.join('salida', input_filename)
        save_predictions(df_predictions, output_path)
        
        # Mover archivo de entrada a backup
        move_to_backup(input_file)
        
        # Log completion
        execution_time = time.time() - start_time
        system_logger.log_file_processed(input_filename, prediction_count)
        system_logger.logger.info(f"Total execution time: {execution_time:.2f} seconds")
        
        # Generate updated dashboard
        dashboard_path = system_logger.generate_html_dashboard()
        system_logger.logger.info(f"Dashboard updated at: {dashboard_path}")
        
    except Exception as e:
        system_logger.log_error(e, "Error in main execution")
        raise

if __name__ == "__main__":
    main()
