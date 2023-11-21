import os
import shutil
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from pathlib import Path

class FileManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Administrador de Archivos")

        # Contenedor para la barra de búsqueda y el botón de búsqueda
        self.search_frame = tk.Frame(self.root)
        self.search_frame.pack(side=tk.TOP)

        # Barra de búsqueda y botón de búsqueda
        self.search_entry = ttk.Entry(self.search_frame)
        self.search_entry.pack(pady=5, side=tk.LEFT)

        self.search_button = ttk.Button(self.search_frame, text="Buscar", command=self.search_items)
        self.search_button.pack(pady=5, side=tk.LEFT)

        # Crear el árbol de directorios
        self.tree = ttk.Treeview(self.root)
        self.tree.heading("#0", text=os.path.basename('carpeta_pruebas'), anchor=tk.W)
        self.tree.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.scrollbar = ttk.Scrollbar(self.root, orient=tk.VERTICAL, command=self.tree.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=self.scrollbar.set)

        # Cargar imágenes
        script_dir = Path(__file__).resolve().parent
        self.file_icon = tk.PhotoImage(file=script_dir / "images" / "file.png").subsample(22, 22)
        self.folder_icon = tk.PhotoImage(file=script_dir / "images" / "folder.png").subsample(22, 22)

        # Botones de eliminar y renombrar en la parte inferior
        self.delete_button = ttk.Button(self.root, text="Eliminar", command=self.remove_item)
        self.delete_button.pack(side=tk.BOTTOM, pady=5)

        self.rename_button = ttk.Button(self.root, text="Renombrar", command=self.rename_item)
        self.rename_button.pack(side=tk.BOTTOM, pady=5)

        # Crear el árbol inicial
        self.create_tree('carpeta_pruebas', "")

    # Escanear un directorio y crear un árbol visual
    def create_tree(self, dir_path, parent):
        current_dir = Path(dir_path)
        for path in current_dir.iterdir():
            if path.is_file():
                self.tree.insert(parent, "end", text=path.name, values=(str(path),), tags=("file",), image=self.file_icon)
            elif path.is_dir():
                folder = self.tree.insert(parent, "end", text=path.name, values=(str(path),), tags=("folder",), image=self.folder_icon)
                self.create_tree(path, folder)

    # Eliminar un elemento
    def remove_item(self):
        selected_item = self.tree.focus()
        item_tags = self.tree.item(selected_item)["tags"]
        
        if "file" in item_tags or "folder" in item_tags:
            if self.confirm_remove():
                path = self.tree.item(selected_item)["values"][0]
                self.remove_file_or_folder(path)
                self.tree.delete(selected_item)

    # Confirmación de eliminación
    def confirm_remove(self):
        response = messagebox.askyesno("Eliminar", "¿Estás seguro de que deseas eliminar este elemento?")
        return response

    def remove_file_or_folder(self, path):
        if os.path.isfile(path):
            os.remove(path)
        elif os.path.isdir(path):
            shutil.rmtree(path)

    def search_tree_items(self, parent, search_term):
        for child in self.tree.get_children(parent):
            item_text = self.tree.item(child, "text")
            if search_term.lower() in item_text.lower():
                self.tree.item(child, open=True)
                self.search_tree_items(child, search_term)
            else:
                self.tree.detach(child)

    # Eliminar un elemento del sistema de archivos
    def search_items(self):
        search_term = self.search_entry.get()
        self.tree.delete(*self.tree.get_children())
        self.create_tree('carpeta_pruebas', "")
        self.search_tree_items("", search_term)

    # Renombrar un elemento
    def rename_item(self):
        selected_item = self.tree.focus()
        item_tags = self.tree.item(selected_item)["tags"]

        is_folder = "folder" in item_tags
        path_key = "values"

        if is_folder:
            path_key = "values"

        item_path = self.tree.item(selected_item)[path_key][0]
        current_name = os.path.basename(item_path)

        dialog_title = "Renombrar Carpeta" if is_folder else "Renombrar Archivo"
        new_name = simpledialog.askstring(dialog_title, f"Ingrese el nuevo nombre de la {'carpeta' if is_folder else 'archivo'}:", initialvalue=current_name)

        if new_name:
            new_path = os.path.join(os.path.dirname(item_path), new_name)
            try:
                os.rename(item_path, new_path)
                self.tree.item(selected_item, text=new_name, values=(new_path,))
                message = f"La {'carpeta' if is_folder else 'archivo'} se ha renombrado correctamente."
                messagebox.showinfo(dialog_title, message)
                self.update_tree_after_rename(selected_item, item_path, new_path, is_folder)
            except Exception as e:
                error_message = f"No se pudo renombrar la {'carpeta' if is_folder else 'archivo'}:\n{str(e)}"
                messagebox.showerror(dialog_title, error_message)

    # Actualizar el arbol despues de cambiar un nombre
    def update_tree_after_rename(self, selected_item, old_path, new_path, is_folder):
        # Obtener el padre del elemento seleccionado
        parent_id = self.tree.parent(selected_item)

        # Actualizar el elemento renombrado
        self.tree.item(selected_item, values=(new_path,))

        # Si es una carpeta, actualizar los hijos también
        if is_folder:
            children = self.tree.get_children(selected_item)
            for child_id in children:
                child_item = self.tree.item(child_id)
                child_values = child_item["values"]
                if child_values and child_values[0].startswith(old_path):
                    updated_path = child_values[0].replace(old_path, new_path)
                    self.tree.item(child_id, text=os.path.basename(updated_path), values=(updated_path,))

# Crear la ventana principal
window = tk.Tk()
app = FileManagerApp(window)
window.mainloop()


