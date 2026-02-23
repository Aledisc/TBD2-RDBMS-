import tkinter as tk
from tkinter import ttk
from metadata import get_tables_and_views
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

        # --- Árbol de objetos ---
        # --- Barra superior de botones ---
        top_left_frame = tk.Frame(left_frame)
        top_left_frame.pack(fill=tk.X, pady=5)

        btn_editor = tk.Button(
            top_left_frame,
            text="Editor SQL",
            command=self.show_sql_editor
        )
        btn_editor.pack(fill=tk.X, padx=5, pady=2)

        btn_logout = tk.Button(
            top_left_frame,
            text="Cerrar sesión",
            command=self.logout
        )
        btn_logout.pack(fill=tk.X, padx=5, pady=2)

        btn_ddl = tk.Button(
            top_left_frame,
            text="Mostrar DDL",
            command=self.show_ddl
        )
        btn_ddl.pack(fill=tk.X, padx=5, pady=2)

        btn_create_table = tk.Button(
            top_left_frame,
            text="Crear Tabla",
            command=self.show_create_table
        )
        btn_create_table.pack(fill=tk.X, padx=5, pady=2)

        btn_create_view = tk.Button(
            top_left_frame,
            text="Crear Vista",
            command=self.show_create_view
        )
        btn_create_view.pack(fill=tk.X, padx=5, pady=2)

        # --- Árbol ---
        self.tree = ttk.Treeview(left_frame)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.tree.bind("<<TreeviewSelect>>", self.on_tree_click)


        # --- Panel derecho  ---
        self.right_frame = tk.Frame(main_frame)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)



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
        self.show_sql_editor()


    def run(self):
        self.root.mainloop()

    def load_tables(self):

        self.tree.delete(*self.tree.get_children(self.tables_node))
        self.tree.delete(*self.tree.get_children(self.views_node))

        tables, views = get_tables_and_views(self.connection)

        for table in tables:
            self.tree.insert(self.tables_node, "end", text=table)

        for view in views:
            self.tree.insert(self.views_node, "end", text=view)

    def on_tree_click(self, event):
        selected_item = self.tree.focus()
        item_text = self.tree.item(selected_item, "text")

        print("Click en:", item_text)

        if item_text == "Tables":
            self.load_tables()

        elif item_text == "Views":

            self.load_tables()

        else:

            self.selected_table = item_text
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

    def logout(self):
        self.connection.close()
        self.root.destroy()

        from login import LoginWindow
        login = LoginWindow()
        login.run()

    def show_ddl(self):

        if not hasattr(self, "selected_table"):
            messagebox.showwarning("Aviso", "Seleccione una tabla primero")
            return

        cursor = self.connection.cursor()
        query = f"SHOW CREATE TABLE {self.selected_table};"
        cursor.execute(query)

        result = cursor.fetchone()
        ddl = result[1]  # la segunda columna trae el CREATE

        # Limpiamos panel derecho
        for widget in self.right_frame.winfo_children():
            widget.destroy()

        ddl_text = tk.Text(self.right_frame)
        ddl_text.pack(fill=tk.BOTH, expand=True)

        ddl_text.insert(tk.END, ddl)

    def show_create_table(self):

        # Limpiar panel derecho
        for widget in self.right_frame.winfo_children():
            widget.destroy()

        container = tk.Frame(self.right_frame)
        container.pack(anchor="w", padx=20, pady=20)

        # --------- Info general ---------
        tk.Label(container, text="Nombre de la tabla:").grid(row=0, column=0, sticky="w")
        self.table_name_entry = tk.Entry(container, width=30)
        self.table_name_entry.grid(row=0, column=1, pady=5, sticky="w")

        tk.Label(container, text=f"Schema: {self.database}").grid(row=1, column=0, sticky="w")

        # --------- Encabezados ----------
        headers = ["Nombre Columna", "Datatype", "PK", "NN"]

        for i, text in enumerate(headers):
            tk.Label(container, text=text, font=("Arial", 10, "bold")).grid(
                row=3, column=i, padx=10, sticky="w"
            )

        # --------- Frame columnas -------
        self.columns_frame = tk.Frame(container)
        self.columns_frame.grid(row=4, column=0, columnspan=4, sticky="w")

        self.column_entries = []
        self.add_column_row()

        tk.Button(
            container,
            text="Agregar Columna",
            command=self.add_column_row
        ).grid(row=5, column=0, pady=10, sticky="w")

        tk.Button(
            container,
            text="Crear Tabla",
            command=self.create_table
        ).grid(row=6, column=0, pady=20, sticky="w")

    def add_column_row(self):

        row_index = len(self.column_entries)

        name_entry = tk.Entry(self.columns_frame, width=20)
        name_entry.grid(row=row_index, column=0, padx=10, pady=3, sticky="w")

        # ---- Combobox de tipos ----
        datatypes = [
            "INT",
            "VARCHAR(50)",
            "VARCHAR(100)",
            "VARCHAR(255)",
            "TEXT",
            "DATE",
            "DATETIME",
            "FLOAT",
            "DOUBLE",
            "DECIMAL(10,2)",
            "BOOLEAN"
        ]

        type_combo = ttk.Combobox(
            self.columns_frame,
            values=datatypes,
            width=18,
            state="readonly"
        )
        type_combo.grid(row=row_index, column=1, padx=10, pady=3, sticky="w")
        type_combo.set("INT")  # valor por defecto

        pk_var = tk.BooleanVar()
        pk_check = tk.Checkbutton(self.columns_frame, variable=pk_var)
        pk_check.grid(row=row_index, column=2)

        nn_var = tk.BooleanVar()
        nn_check = tk.Checkbutton(self.columns_frame, variable=nn_var)
        nn_check.grid(row=row_index, column=3)

        self.column_entries.append((name_entry, type_combo, pk_var, nn_var))

    def create_table(self):

        table_name = self.table_name_entry.get()
        columns_sql = []

        for name_entry, type_entry, pk_var, nn_var in self.column_entries:

            name = name_entry.get()
            col_type = type_entry.get()

            if not name or not col_type:
                continue

            col_def = f"{name} {col_type}"

            if nn_var.get():
                col_def += " NOT NULL"

            if pk_var.get():
                col_def += " PRIMARY KEY"

            columns_sql.append(col_def)

        if not table_name or not columns_sql:
            messagebox.showerror("Error", "Datos incompletos")
            return

        query = f"CREATE TABLE {table_name} ({', '.join(columns_sql)});"

        try:
            cursor = self.connection.cursor()
            cursor.execute(query)
            self.connection.commit()
            messagebox.showinfo("Éxito", "Tabla creada correctamente")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def show_create_view(self):

        # Limpiar panel derecho
        for widget in self.right_frame.winfo_children():
            widget.destroy()

        container = tk.Frame(self.right_frame)
        container.pack(anchor="w", padx=20, pady=20)

        tk.Label(container, text="Nombre de la vista").grid(row=0, column=0, sticky="w")
        self.view_name_entry = tk.Entry(container, width=30)
        self.view_name_entry.grid(row=0, column=1, pady=5, sticky="w")

        tk.Label(container, text="Definición SELECT").grid(row=1, column=0, sticky="w")

        self.view_sql_text = tk.Text(container, height=10, width=60)
        self.view_sql_text.grid(row=2, column=0, columnspan=2, pady=10)

        tk.Button(
            container,
            text="Crear Vista",
            command=self.create_view
        ).grid(row=3, column=0, pady=10, sticky="w")

    def create_view(self):

        view_name = self.view_name_entry.get()
        select_sql = self.view_sql_text.get("1.0", tk.END).strip()

        if not view_name or not select_sql:
            messagebox.showerror("Error", "Datos incompletos")
            return

        query = f"CREATE VIEW {view_name} AS {select_sql};"

        try:
            cursor = self.connection.cursor()
            cursor.execute(query)
            self.connection.commit()
            messagebox.showinfo("Éxito", "Vista creada correctamente")
        except Exception as e:
            messagebox.showerror("Error", str(e))