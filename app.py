import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import shutil
import os
import predict

class FileProcessorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Procesador de Archivos CSV/XLSX")
        self.root.geometry("800x600")
        
        # Crear barra de menú
        self.menubar = tk.Menu(root)
        root.config(menu=self.menubar)
        
        # Menú Help
        help_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
        
        # Crear frame principal
        main_frame = tk.Frame(root, padx=20, pady=20)
        main_frame.pack(expand=True, fill='both')
        
        # Frame superior para botones
        button_frame = tk.Frame(main_frame)
        button_frame.pack(fill='x', pady=(0, 20))
        
        # Frame izquierdo para etiqueta y botones principales
        left_button_frame = tk.Frame(button_frame)
        left_button_frame.pack(side='left', fill='x', expand=True)
        
        # Etiqueta para mostrar archivo seleccionado
        self.file_label = tk.Label(left_button_frame, text="Ningún archivo seleccionado", wraplength=350)
        self.file_label.pack(side='left', pady=10)
        
        # Botones principales
        upload_button = tk.Button(left_button_frame, text="Seleccionar Archivo", command=self.select_file)
        upload_button.pack(side='left', padx=10)
        
        process_button = tk.Button(left_button_frame, text="Procesar Archivo", command=self.process_file)
        process_button.pack(side='left')
        
        # Botón de salir (alineado a la derecha)
        exit_button = tk.Button(button_frame, text="Salir", command=self.root.quit, 
                              bg='#ff4444', fg='white', width=10)
        exit_button.pack(side='right', padx=10)
        
        # Frame inferior para las listas
        lists_frame = tk.Frame(main_frame)
        lists_frame.pack(expand=True, fill='both')
        
        # Frame para lista de entrada
        entrada_frame = tk.Frame(lists_frame)
        entrada_frame.pack(side='left', expand=True, fill='both', padx=(0, 10))
        
        tk.Label(entrada_frame, text="Archivos en Entrada:").pack()
        self.entrada_listbox = tk.Listbox(entrada_frame)
        self.entrada_listbox.pack(expand=True, fill='both')
        entrada_scroll = tk.Scrollbar(entrada_frame, orient="vertical", command=self.entrada_listbox.yview)
        entrada_scroll.pack(side='right', fill='y')
        self.entrada_listbox.config(yscrollcommand=entrada_scroll.set)
        
        # Frame para lista de salida
        salida_frame = tk.Frame(lists_frame)
        salida_frame.pack(side='left', expand=True, fill='both')
        
        tk.Label(salida_frame, text="Archivos en Salida:").pack()
        self.salida_listbox = tk.Listbox(salida_frame)
        self.salida_listbox.pack(expand=True, fill='both')
        salida_scroll = tk.Scrollbar(salida_frame, orient="vertical", command=self.salida_listbox.yview)
        salida_scroll.pack(side='right', fill='y')
        self.salida_listbox.config(yscrollcommand=salida_scroll.set)
        
        # Botón de descarga para archivos de salida
        download_button = tk.Button(salida_frame, text="Descargar Archivo Seleccionado", command=self.download_file)
        download_button.pack(pady=10)
        
        self.selected_file = None
        
        # Actualizar listas inicialmente
        self.update_file_lists()

    def show_about(self):
        about_window = tk.Toplevel(self.root)
        about_window.title("About")
        about_window.geometry("400x200")
        about_window.resizable(False, False)
        
        # Hacer la ventana modal
        about_window.transient(self.root)
        about_window.grab_set()
        
        # Centrar la ventana
        about_window.geometry("+%d+%d" % (
            self.root.winfo_rootx() + self.root.winfo_width()/2 - 200,
            self.root.winfo_rooty() + self.root.winfo_height()/2 - 100
        ))
        
        # Frame para el contenido
        frame = tk.Frame(about_window, padx=20, pady=20)
        frame.pack(expand=True, fill='both')
        
        # Logo o nombre de la compañía
        company_label = tk.Label(frame, text="SKYNET", font=("Arial", 16, "bold"))
        company_label.pack(pady=(0, 10))
        
        # Versión
        version_label = tk.Label(frame, text="Version 1.0.0", font=("Arial", 10))
        version_label.pack(pady=(0, 20))
        
        # Descripción
        description = "Procesador de archivos CSV y XLSX\nDesarrollado por SKYNET"
        desc_label = tk.Label(frame, text=description, justify=tk.CENTER)
        desc_label.pack(pady=(0, 20))
        
        # Botón de cerrar
        close_button = tk.Button(frame, text="Cerrar", command=about_window.destroy)
        close_button.pack()

    def update_file_lists(self):
        # Limpiar listas
        self.entrada_listbox.delete(0, tk.END)
        self.salida_listbox.delete(0, tk.END)
        
        # Actualizar lista de entrada
        os.makedirs('entrada', exist_ok=True)
        for file in sorted(os.listdir('entrada')):
            if file.endswith(('.csv', '.xlsx')):
                self.entrada_listbox.insert(tk.END, file)
        
        # Actualizar lista de salida
        os.makedirs('salida', exist_ok=True)
        for file in sorted(os.listdir('salida')):
            if file.endswith(('.csv', '.xlsx')):
                self.salida_listbox.insert(tk.END, file)

    def select_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[
                ("Archivos Soportados", "*.csv *.xlsx"),
                ("Archivos CSV", "*.csv"),
                ("Archivos Excel", "*.xlsx")
            ]
        )
        if file_path:
            self.selected_file = file_path
            self.file_label.config(text=f"Archivo seleccionado: {os.path.basename(file_path)}")
            
            try:
                os.makedirs('entrada', exist_ok=True)
                shutil.copy(file_path, os.path.join('entrada', os.path.basename(file_path)))
                messagebox.showinfo("Éxito", "Archivo copiado exitosamente a la carpeta entrada/")
                self.update_file_lists()
            except Exception as e:
                messagebox.showerror("Error", f"Error al copiar archivo: {str(e)}")

    def process_file(self):
        try:
            predict.main()
            messagebox.showinfo("Éxito", "Archivo procesado exitosamente")
            self.update_file_lists()
        except Exception as e:
            messagebox.showerror("Error", f"Error al procesar archivo: {str(e)}")

    def download_file(self):
        # Obtener el archivo seleccionado de la lista de salida
        selection = self.salida_listbox.curselection()
        if not selection:
            messagebox.showwarning("Advertencia", "Por favor seleccione un archivo de la lista de salida")
            return
        
        selected_file = self.salida_listbox.get(selection[0])
        source_path = os.path.join('salida', selected_file)
        
        # Determinar la extensión del archivo
        file_ext = os.path.splitext(selected_file)[1]
        
        # Abrir diálogo para seleccionar dónde guardar el archivo
        save_path = filedialog.asksaveasfilename(
            defaultextension=file_ext,
            initialfile=selected_file,
            filetypes=[
                ("Archivos CSV", "*.csv") if file_ext == '.csv' else ("Archivos Excel", "*.xlsx")
            ]
        )
        
        if save_path:
            try:
                shutil.copy2(source_path, save_path)
                messagebox.showinfo("Éxito", f"Archivo descargado exitosamente como:\n{save_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Error al descargar archivo: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = FileProcessorApp(root)
    root.mainloop()
