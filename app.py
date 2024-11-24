import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import shutil
import os
import predict
import pandas as pd
from tkinter.ttk import Style
import threading
import webbrowser
from logger import system_logger
from pathlib import Path

class FileProcessorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Procesador de Archivos CSV/XLSX")
        self.root.geometry("1000x700")
        
        # Inicializar tema
        self.style = Style()
        self.current_theme = "light"
        
        # Crear barra de menú
        self.menubar = tk.Menu(root)
        root.config(menu=self.menubar)
        
        # Menú Help
        help_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
        help_menu.add_command(label="View Logs", command=self.show_logs)
        help_menu.add_command(label="View Dashboard", command=self.show_dashboard)
        
        # Menú View
        view_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Cambiar Tema", command=self.toggle_theme)
        
        # Crear frame principal
        self.main_frame = ttk.Frame(root, padding="20")
        self.main_frame.pack(expand=True, fill='both')
        
        # Frame superior para botones
        button_frame = ttk.Frame(self.main_frame)
        button_frame.pack(fill='x', pady=(0, 20))
        
        # Frame izquierdo para etiqueta y botones principales
        left_button_frame = ttk.Frame(button_frame)
        left_button_frame.pack(side='left', fill='x', expand=True)
        
        # Etiqueta para mostrar archivo seleccionado
        self.file_label = ttk.Label(left_button_frame, text="Ningún archivo seleccionado", wraplength=350)
        self.file_label.pack(side='left', pady=10)
        
        # Botones principales
        upload_button = ttk.Button(left_button_frame, text="Seleccionar Archivo", command=self.select_file)
        upload_button.pack(side='left', padx=10)
        
        process_button = ttk.Button(left_button_frame, text="Procesar Archivo", command=self.process_file_with_progress)
        process_button.pack(side='left')
        
        # Botón de Dashboard
        dashboard_button = ttk.Button(left_button_frame, text="Dashboard", command=self.show_dashboard)
        dashboard_button.pack(side='left', padx=10)
        
        # Botón de salir (alineado a la derecha)
        exit_button = ttk.Button(button_frame, text="Salir", command=self.root.quit)
        exit_button.pack(side='right', padx=10)
        
        # Barra de progreso
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(self.main_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(fill='x', pady=(0, 20))
        
        # Frame para preview y listas
        content_frame = ttk.Frame(self.main_frame)
        content_frame.pack(expand=True, fill='both')
        
        # Frame para preview
        preview_frame = ttk.Frame(content_frame)
        preview_frame.pack(side='top', fill='both', expand=True, pady=(0, 10))
        
        preview_label = ttk.Label(preview_frame, text="Vista Previa del Archivo:")
        preview_label.pack()
        
        # Crear Treeview para la vista previa
        self.preview_tree = ttk.Treeview(preview_frame, show='headings')
        self.preview_tree.pack(side='left', fill='both', expand=True)
        
        # Scrollbars para el Treeview
        vsb = ttk.Scrollbar(preview_frame, orient="vertical", command=self.preview_tree.yview)
        vsb.pack(side='right', fill='y')
        hsb = ttk.Scrollbar(preview_frame, orient="horizontal", command=self.preview_tree.xview)
        hsb.pack(side='bottom', fill='x')
        
        self.preview_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        # Frame inferior para las listas
        lists_frame = ttk.Frame(content_frame)
        lists_frame.pack(expand=True, fill='both')
        
        # Frame para lista de entrada
        entrada_frame = ttk.Frame(lists_frame)
        entrada_frame.pack(side='left', expand=True, fill='both', padx=(0, 10))
        
        self.entrada_label = ttk.Label(entrada_frame, text="Archivos en Entrada:")
        self.entrada_label.pack()
        
        self.entrada_listbox = tk.Listbox(entrada_frame)
        self.entrada_listbox.pack(expand=True, fill='both')
        entrada_scroll = ttk.Scrollbar(entrada_frame, orient="vertical", command=self.entrada_listbox.yview)
        entrada_scroll.pack(side='right', fill='y')
        self.entrada_listbox.config(yscrollcommand=entrada_scroll.set)
        
        # Vincular evento de selección
        self.entrada_listbox.bind('<<ListboxSelect>>', self.on_file_select)
        
        # Frame para lista de salida
        salida_frame = ttk.Frame(lists_frame)
        salida_frame.pack(side='left', expand=True, fill='both')
        
        self.salida_label = ttk.Label(salida_frame, text="Archivos en Salida:")
        self.salida_label.pack()
        
        self.salida_listbox = tk.Listbox(salida_frame)
        self.salida_listbox.pack(expand=True, fill='both')
        salida_scroll = ttk.Scrollbar(salida_frame, orient="vertical", command=self.salida_listbox.yview)
        salida_scroll.pack(side='right', fill='y')
        self.salida_listbox.config(yscrollcommand=salida_scroll.set)
        
        # Vincular evento de selección para salida
        self.salida_listbox.bind('<<ListboxSelect>>', self.on_file_select)
        
        # Botón de descarga para archivos de salida
        download_button = ttk.Button(salida_frame, text="Descargar Archivo Seleccionado", command=self.download_file)
        download_button.pack(pady=10)
        
        self.selected_file = None
        
        # Actualizar listas inicialmente
        self.update_file_lists()
        
        # Aplicar tema inicial después de crear todos los widgets
        self.apply_theme()

    def show_dashboard(self):
        """Abrir el dashboard en el navegador predeterminado"""
        dashboard_path = Path('logs/dashboard.html')
        if dashboard_path.exists():
            webbrowser.open(dashboard_path.absolute().as_uri())
        else:
            messagebox.showinfo("Info", "El dashboard aún no está disponible. Procese algunos archivos primero.")

    def show_logs(self):
        """Mostrar ventana con logs del sistema"""
        logs_window = tk.Toplevel(self.root)
        logs_window.title("System Logs")
        logs_window.geometry("800x600")
        
        # Frame para los logs
        logs_frame = ttk.Frame(logs_window, padding="10")
        logs_frame.pack(fill='both', expand=True)
        
        # Crear notebook para diferentes tipos de logs
        notebook = ttk.Notebook(logs_frame)
        notebook.pack(fill='both', expand=True)
        
        # Función para crear tab de logs
        def create_log_tab(file_name, tab_name):
            frame = ttk.Frame(notebook)
            notebook.add(frame, text=tab_name)
            
            text_widget = tk.Text(frame, wrap=tk.WORD)
            text_widget.pack(fill='both', expand=True)
            
            scrollbar = ttk.Scrollbar(frame, command=text_widget.yview)
            scrollbar.pack(side='right', fill='y')
            text_widget.config(yscrollcommand=scrollbar.set)
            
            try:
                with open(f'logs/{file_name}', 'r') as f:
                    text_widget.insert('1.0', f.read())
            except FileNotFoundError:
                text_widget.insert('1.0', f"No {tab_name} available yet.")
            
            text_widget.config(state='disabled')
        
        # Crear tabs para diferentes logs
        create_log_tab('system.log', 'System Logs')
        create_log_tab('errors.log', 'Error Logs')
        
        # Botón para cerrar
        close_button = ttk.Button(logs_frame, text="Close", command=logs_window.destroy)
        close_button.pack(pady=10)

    def apply_theme(self):
        if self.current_theme == "dark":
            self.root.configure(bg='#2b2b2b')
            bg_color = '#2b2b2b'
            fg_color = 'white'
            self.style.configure('TFrame', background=bg_color)
            self.style.configure('TLabel', background=bg_color, foreground=fg_color)
            self.style.configure('TButton', background='#404040')
            self.style.configure('Treeview', background='#333333', foreground='white', fieldbackground='#333333')
            self.style.configure('TProgressbar', background='#404040')
        else:
            self.root.configure(bg='#f0f0f0')
            bg_color = '#f0f0f0'
            fg_color = 'black'
            self.style.configure('TFrame', background=bg_color)
            self.style.configure('TLabel', background=bg_color, foreground=fg_color)
            self.style.configure('TButton', background='#e0e0e0')
            self.style.configure('Treeview', background='white', foreground='black', fieldbackground='white')
            self.style.configure('TProgressbar', background='#0078d7')

        # Configurar colores de Listbox
        for listbox in [self.entrada_listbox, self.salida_listbox]:
            listbox.configure(bg=bg_color, fg=fg_color)

    def toggle_theme(self):
        self.current_theme = "dark" if self.current_theme == "light" else "light"
        self.apply_theme()

    def show_preview(self, filepath):
        try:
            # Limpiar vista previa actual
            for item in self.preview_tree.get_children():
                self.preview_tree.delete(item)
            
            # Leer archivo según su extensión
            if filepath.endswith('.csv'):
                df = pd.read_csv(filepath, nrows=100)  # Limitar a 100 filas para rendimiento
            elif filepath.endswith('.xlsx'):
                df = pd.read_excel(filepath, nrows=100)
            else:
                return
            
            # Configurar columnas
            self.preview_tree['columns'] = list(df.columns)
            for col in df.columns:
                self.preview_tree.heading(col, text=col)
                self.preview_tree.column(col, width=100)
            
            # Insertar datos
            for idx, row in df.iterrows():
                self.preview_tree.insert('', 'end', values=list(row))
                
        except Exception as e:
            system_logger.log_error(e, f"Error showing preview for file: {filepath}")
            messagebox.showerror("Error", f"Error al mostrar vista previa: {str(e)}")

    def on_file_select(self, event):
        widget = event.widget
        selection = widget.curselection()
        
        if selection:
            filename = widget.get(selection[0])
            if widget == self.entrada_listbox:
                filepath = os.path.join('entrada', filename)
            else:
                filepath = os.path.join('salida', filename)
            
            self.show_preview(filepath)

    def process_file_with_progress(self):
        def update_progress(value):
            self.progress_var.set(value)
            self.root.update_idletasks()

        def run_process():
            try:
                update_progress(0)
                # Simular progreso
                update_progress(30)
                predict.main()
                update_progress(100)
                messagebox.showinfo("Éxito", "Archivo procesado exitosamente")
                self.update_file_lists()
            except Exception as e:
                system_logger.log_error(e, "Error processing file")
                messagebox.showerror("Error", f"Error al procesar archivo: {str(e)}")
            finally:
                update_progress(0)

        thread = threading.Thread(target=run_process)
        thread.start()

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
        frame = ttk.Frame(about_window, padding="20")
        frame.pack(expand=True, fill='both')
        
        # Logo o nombre de la compañía
        company_label = ttk.Label(frame, text="SKYNET", font=("Arial", 16, "bold"))
        company_label.pack(pady=(0, 10))
        
        # Versión
        version_label = ttk.Label(frame, text="Version 1.0.0", font=("Arial", 10))
        version_label.pack(pady=(0, 20))
        
        # Descripción
        description = "Procesador de archivos CSV y XLSX\nDesarrollado por SKYNET"
        desc_label = ttk.Label(frame, text=description, justify=tk.CENTER)
        desc_label.pack(pady=(0, 20))
        
        # Botón de cerrar
        close_button = ttk.Button(frame, text="Cerrar", command=about_window.destroy)
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
            try:
                self.selected_file = file_path
                self.file_label.config(text=f"Archivo seleccionado: {os.path.basename(file_path)}")
                
                os.makedirs('entrada', exist_ok=True)
                shutil.copy(file_path, os.path.join('entrada', os.path.basename(file_path)))
                messagebox.showinfo("Éxito", "Archivo copiado exitosamente a la carpeta entrada/")
                self.update_file_lists()
            except Exception as e:
                system_logger.log_error(e, f"Error selecting file: {file_path}")
                messagebox.showerror("Error", f"Error al copiar archivo: {str(e)}")

    def download_file(self):
        # Obtener el archivo seleccionado de la lista de salida
        selection = self.salida_listbox.curselection()
        if not selection:
            messagebox.showwarning("Advertencia", "Por favor seleccione un archivo de la lista de salida")
            return
        
        selected_file = self.salida_listbox.get(selection[0])
        source_path = os.path.join('salida', selected_file)
        
        try:
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
                shutil.copy2(source_path, save_path)
                messagebox.showinfo("Éxito", f"Archivo descargado exitosamente como:\n{save_path}")
        except Exception as e:
            system_logger.log_error(e, f"Error downloading file: {source_path}")
            messagebox.showerror("Error", f"Error al descargar archivo: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = FileProcessorApp(root)
    root.mainloop()
