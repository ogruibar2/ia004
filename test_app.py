import unittest
import os
import shutil
import pandas as pd
from unittest.mock import MagicMock, patch
import tkinter as tk
from app import FileProcessorApp
import predict

class TestPredict(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Crear directorios necesarios para pruebas
        os.makedirs('entrada', exist_ok=True)
        os.makedirs('salida', exist_ok=True)
        os.makedirs('backup', exist_ok=True)
        
        # Crear archivo CSV de prueba
        cls.test_csv = 'entrada/test.csv'
        df = pd.DataFrame({
            'Elemento': ['Test1', 'Test2'],
        })
        df.to_csv(cls.test_csv, index=False)
        
        # Crear archivo XLSX de prueba
        cls.test_xlsx = 'entrada/test.xlsx'
        df.to_excel(cls.test_xlsx, index=False)

    @classmethod
    def tearDownClass(cls):
        # Limpiar archivos de prueba
        if os.path.exists(cls.test_csv):
            os.remove(cls.test_csv)
        if os.path.exists(cls.test_xlsx):
            os.remove(cls.test_xlsx)

    def test_get_input_file(self):
        """Probar que get_input_file encuentra archivos correctamente"""
        result = predict.get_input_file()
        self.assertTrue(result.endswith('.csv') or result.endswith('.xlsx'))

    def test_move_to_backup(self):
        """Probar que move_to_backup mueve archivos correctamente"""
        # Crear archivo temporal
        test_file = 'entrada/temp_test.csv'
        with open(test_file, 'w') as f:
            f.write('test')
        
        predict.move_to_backup(test_file)
        self.assertTrue(os.path.exists('backup/temp_test.csv'))
        
        # Limpiar
        os.remove('backup/temp_test.csv')

class TestApp(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.app = FileProcessorApp(self.root)

    def tearDown(self):
        self.root.destroy()

    def test_update_file_lists(self):
        """Probar que las listas se actualizan correctamente"""
        # Crear archivo temporal
        test_file = 'entrada/test_update.csv'
        with open(test_file, 'w') as f:
            f.write('test')
        
        self.app.update_file_lists()
        
        # Verificar que el archivo aparece en la lista
        files_in_listbox = self.app.entrada_listbox.get(0, tk.END)
        self.assertIn('test_update.csv', files_in_listbox)
        
        # Limpiar
        os.remove(test_file)

    @patch('tkinter.filedialog.askopenfilename')
    def test_select_file(self, mock_filedialog):
        """Probar la selección de archivo"""
        mock_filedialog.return_value = 'test_file.csv'
        
        # Simular selección de archivo
        self.app.select_file()
        
        # Verificar que la etiqueta se actualizó
        self.assertTrue('test_file.csv' in self.app.file_label.cget('text'))

    @patch('predict.main')
    def test_process_file(self, mock_predict):
        """Probar el procesamiento de archivo"""
        self.app.process_file()
        mock_predict.assert_called_once()

    def test_show_about(self):
        """Probar que la ventana About se muestra correctamente"""
        # Abrir ventana About
        self.app.show_about()
        
        # Verificar que existe una ventana Toplevel
        about_windows = [w for w in self.root.winfo_children() if isinstance(w, tk.Toplevel)]
        self.assertEqual(len(about_windows), 1)
        
        # Cerrar ventana About
        about_windows[0].destroy()

def run_tests():
    # Configurar y ejecutar las pruebas
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestPredict)
    suite.addTests(loader.loadTestsFromTestCase(TestApp))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()

if __name__ == '__main__':
    run_tests()
