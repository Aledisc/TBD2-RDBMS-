import tkinter as tk
from tkinter import ttk
from metadata import get_tables

class MainWindow:

    def __init__(self, connection, database):
        self.connection = connection
        self.database = database

        self.root = tk.Tk()
        self.root.title("Database Manager")
        self.root.geometry("1200x700")

        # --- Contenedor principal ---
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # --- Panel izquierdo ---
        left_frame = tk.Frame(main_frame, width=300, bg="#f0f0f0")
        left_frame.pack(side=tk.LEFT, fill=tk.Y)

        # --- Panel derecho  ---
        right_frame = tk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # --- Árbol de objetos ---
        self.tree = ttk.Treeview(left_frame)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        # asociar tablas al arbol
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_click)

        # Nodo raíz (base de datos)
        db_node = self.tree.insert("", "end", text="Base de Datos", open=True)

        # Nodos
        self.tables_node = self.tree.insert(db_node, "end", text="Tables")
        self.views_node = self.tree.insert(db_node, "end", text="Views")
        self.procedures_node = self.tree.insert(db_node, "end", text="Procedures")
        self.functions_node = self.tree.insert(db_node, "end", text="Functions")
        self.triggers_node = self.tree.insert(db_node, "end", text="Triggers")
        self.indexes_node = self.tree.insert(db_node, "end", text="Indexes")
        self.users_node = self.tree.insert(db_node, "end", text="Users")

        # --- Placeholder del área derecha
        label = tk.Label(
            right_frame,
            text="Área de trabajo",
            font=("Arial", 16)
        )
        label.pack(pady=20)


    def run(self):
        self.root.mainloop()

    def load_tables(self):
        print("se supone que carga tablas...")
        self.tree.delete(*self.tree.get_children(self.tables_node))

        tables = get_tables(self.connection)
        print("se supone que encontro las tablas:" , tables)

        for table in tables:
            self.tree.insert(self.tables_node, "end", text=table)



    def on_tree_click(self, event):
        selected_item = self.tree.focus()
        item_text = self.tree.item(selected_item, "text")

        print("click en: ", item_text)
        if item_text == "Tables":
            self.load_tables()