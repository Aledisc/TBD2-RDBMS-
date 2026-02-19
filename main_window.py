import tkinter as tk
from tkinter import ttk

class MainWindow:

    def __init__(self, connection):
        self.connection = connection

        self.root = tk.Tk()
        self.root.title("Database Manager")
        self.root.geometry("1200x700")

        # --- Contenedor principal ---
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # --- Panel izquierdo (árbol) ---
        left_frame = tk.Frame(main_frame, width=300, bg="#f0f0f0")
        left_frame.pack(side=tk.LEFT, fill=tk.Y)

        # --- Panel derecho (trabajo) ---
        right_frame = tk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # --- Árbol de objetos ---
        self.tree = ttk.Treeview(left_frame)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Nodo raíz (base de datos)
        db_node = self.tree.insert("", "end", text="Base de Datos", open=True)

        # Nodos requeridos por el proyecto
        self.tables_node = self.tree.insert(db_node, "end", text="Tables")
        self.views_node = self.tree.insert(db_node, "end", text="Views")
        self.procedures_node = self.tree.insert(db_node, "end", text="Procedures")
        self.functions_node = self.tree.insert(db_node, "end", text="Functions")
        self.triggers_node = self.tree.insert(db_node, "end", text="Triggers")
        self.indexes_node = self.tree.insert(db_node, "end", text="Indexes")
        self.users_node = self.tree.insert(db_node, "end", text="Users")

        # --- Placeholder área derecha ---
        label = tk.Label(
            right_frame,
            text="Área de trabajo",
            font=("Arial", 16)
        )
        label.pack(pady=20)

    def run(self):
        self.root.mainloop()