import tkinter as tk
from tkinter import filedialog, messagebox
import shutil
import os
import predict

class FileProcessorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Procesador de Archivos CSV")
        self.root.geometry("400x200")
        
        # Crear frame principal
        main_frame = tk.Frame(root, padx=20, pady=20)
        main_frame.pack(expand=True, fill='both')
        
        # Etiqueta para mostrar archivo seleccionado
        self.file_label = tk.Label(main_frame, text="Ningún archivo seleccionado", wraplength=350)
        self.file_label.pack(pady=10)
        
        # Botón para seleccionar archivo
        upload_button = tk.Button(main_frame, text="Seleccionar CSV", command=self.select_file)
        upload_button.pack(pady=10)
        
        # Botón para procesar
        process_button = tk.Button(main_frame, text="Procesar Archivo", command=self.process_file)
        process_button.pack(pady=10)
        
        self.selected_file = None

    def select_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Archivos CSV", "*.csv")]
        )
        if file_path:
            self.selected_file = file_path
            self.file_label.config(text=f"Archivo seleccionado: {os.path.basename(file_path)}")
            
            # Copiar archivo a la carpeta entrada/
            try:
                os.makedirs('entrada', exist_ok=True)
                shutil.copy(file_path, os.path.join('entrada', os.path.basename(file_path)))
                messagebox.showinfo("Éxito", "Archivo copiado exitosamente a la carpeta entrada/")
            except Exception as e:
                messagebox.showerror("Error", f"Error al copiar archivo: {str(e)}")

    def process_file(self):
        try:
            predict.main()
            messagebox.showinfo("Éxito", "Archivo procesado exitosamente")
        except Exception as e:
            messagebox.showerror("Error", f"Error al procesar archivo: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = FileProcessorApp(root)
    root.mainloop()
