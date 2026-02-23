import tkinter as tk
from tkinter import ttk
from metadata import get_tables
from tkinter import messagebox

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
        self.right_frame = tk.Frame(main_frame)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

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
        '''label = tk.Label(
            right_frame,
            text="Área de trabajo",
            font=("Arial", 16)
        )
        label.pack(pady=20)
        '''
        self.show_sql_editor()


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
        else:
            self.load_table_data(item_text)

    def load_table_data(self, table_name):

        # Limpiar panel derecho
        for widget in self.right_frame.winfo_children():
            widget.destroy()

        cursor = self.connection.cursor()
        query = f"SELECT * FROM {table_name} LIMIT 100;"
        cursor.execute(query)

        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]

        table = ttk.Treeview(self.right_frame, columns=columns, show="headings")
        table.pack(fill=tk.BOTH, expand=True)

        #creamos encabezados
        for col in columns:
            table.heading(col, text=col)
            table.column(col, width=120)

        #Creamos filas
        for row in rows:
            table.insert("", "end", values=row)

    #funcion para dibujar el editor de texto en e area derecha dela ventana
    def show_sql_editor(self):

        # Limpiar panel derecho
        for widget in self.right_frame.winfo_children():
            widget.destroy()

        # Editor SQL
        self.sql_text = tk.Text(self.right_frame, height=10)
        self.sql_text.pack(fill=tk.X, padx=5, pady=5)

        # Botón ejecutar
        run_button = tk.Button(
            self.right_frame,
            text="Ejecutar SQL",
            command=self.execute_sql
        )
        run_button.pack(pady=5)

        # Frame resultados
        self.result_frame = tk.Frame(self.right_frame)
        self.result_frame.pack(fill=tk.BOTH, expand=True)

    def execute_sql(self):

        query = self.sql_text.get("1.0", tk.END).strip()

        cursor = self.connection.cursor()

        try:
            cursor.execute(query)

            # Si devuelve datos (SELECT)
            if cursor.description:

                rows = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description]

                self.show_results(columns, rows)

            else:
                # INSERT, UPDATE, DELETE, CREATE, etc.
                self.connection.commit()
                messagebox.showinfo("Éxito", "Sentencia ejecutada correctamente")

        except Exception as e:
            messagebox.showerror("Error", str(e))

    #funcion para pues mostrar los resultads de cuando ejecutamos la vaina sql que hicimos
    def show_results(self, columns, rows):

        # Limpiar resultados anteriores
        for widget in self.result_frame.winfo_children():
            widget.destroy()

        table = ttk.Treeview(self.result_frame, columns=columns, show="headings")
        table.pack(fill=tk.BOTH, expand=True)

        for col in columns:
            table.heading(col, text=col)
            table.column(col, width=120)

        for row in rows:
            table.insert("", "end", values=row)