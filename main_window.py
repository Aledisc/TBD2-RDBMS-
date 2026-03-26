import tkinter as tk
from tkinter import ttk, messagebox
import threading
import datetime
import os

from sync import load_mapping, sync_in, sync_out, get_sync_history
from metadata import (
    get_tables_and_views, get_procedures_and_functions,
    get_triggers, get_users, get_indexes
)


class MainWindow:

    def __init__(self, slave_conn, master_conn, database):
        self.slave_conn  = slave_conn
        self.master_conn = master_conn
        self.database    = database
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        self.mapping = load_mapping(os.path.join(BASE_DIR, "mapping.json"))

        # ── Ventana principal ──────────────────────────────
        self.root = tk.Tk()
        self.root.title("Sincronizador Pagila – Dashboard")
        self.root.geometry("1280x750")

        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # ── Panel izquierdo (árbol de objetos) ────────────
        left = tk.Frame(main_frame, width=260, bg="#f0f0f0")
        left.pack(side=tk.LEFT, fill=tk.Y)
        left.pack_propagate(False)

        tk.Label(left, text="Objetos DB", font=("Arial", 11, "bold"),
                 bg="#f0f0f0").pack(pady=8)

        self.tree = ttk.Treeview(left)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_click)

        db_node = self.tree.insert("", "end", text=f"⬡ {database}", open=True)
        self.tables_node     = self.tree.insert(db_node, "end", text="Tables")
        self.views_node      = self.tree.insert(db_node, "end", text="Views")
        self.procedures_node = self.tree.insert(db_node, "end", text="Procedures")
        self.functions_node  = self.tree.insert(db_node, "end", text="Functions")
        self.triggers_node   = self.tree.insert(db_node, "end", text="Triggers")
        self.indexes_node    = self.tree.insert(db_node, "end", text="Indexes")
        self.users_node      = self.tree.insert(db_node, "end", text="Users")

        tk.Button(left, text="Cerrar sesión", command=self.logout).pack(
            fill=tk.X, padx=5, pady=4)

        # ── Panel derecho ──────────────────────────────────
        self.right = tk.Frame(main_frame)
        self.right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Tabs principales
        self.tabs = ttk.Notebook(self.right)
        self.tabs.pack(fill=tk.BOTH, expand=True)

        self.tab_sync = tk.Frame(self.tabs)
        self.tab_sql  = tk.Frame(self.tabs)
        self.tab_data = tk.Frame(self.tabs)

        self.tabs.add(self.tab_sync, text="  🔄  Sincronización  ")
        self.tabs.add(self.tab_sql,  text="  🖊  Editor SQL  ")
        self.tabs.add(self.tab_data, text="  📋  Datos  ")

        self._build_sync_tab()
        self._build_sql_tab()

    # tab de sync
    def _build_sync_tab(self):
        pad = {"padx": 16, "pady": 8}

        # ─── Estado conexiones ────────────────────────────
        status_frame = tk.LabelFrame(
            self.tab_sync, text=" Estado de conexiones ", font=("Arial", 10, "bold"))
        status_frame.pack(fill="x", **pad)

        self.lbl_slave  = tk.Label(status_frame, text="● SLAVE  (MySQL)",
                                   fg="green", font=("Arial", 10))
        self.lbl_slave.pack(anchor="w", padx=10, pady=4)

        self.lbl_master = tk.Label(status_frame, text="● MASTER (PostgreSQL)",
                                   fg="green", font=("Arial", 10))
        self.lbl_master.pack(anchor="w", padx=10, pady=4)

        # ─── Botones de sincronización ────────────────────
        btn_frame = tk.LabelFrame(
            self.tab_sync, text=" Acciones ", font=("Arial", 10, "bold"))
        btn_frame.pack(fill="x", **pad)

        tk.Button(
            btn_frame,
            text="⬇  Sync-IN   (MASTER → SLAVE)",
            font=("Arial", 11),
            width=32, height=2,
            bg="#4a90d9", fg="white",
            command=self.run_sync_in
        ).pack(side=tk.LEFT, padx=12, pady=10)

        tk.Button(
            btn_frame,
            text="⬆  Sync-OUT  (SLAVE → MASTER)",
            font=("Arial", 11),
            width=32, height=2,
            bg="#5c9e5c", fg="white",
            command=self.run_sync_out
        ).pack(side=tk.LEFT, padx=12, pady=10)

        # ─── Barra de progreso ────────────────────────────
        prog_frame = tk.Frame(self.tab_sync)
        prog_frame.pack(fill="x", padx=16)

        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            prog_frame, variable=self.progress_var,
            maximum=100, length=600)
        self.progress_bar.pack(side=tk.LEFT, pady=4)

        self.lbl_progress = tk.Label(prog_frame, text="", font=("Arial", 9))
        self.lbl_progress.pack(side=tk.LEFT, padx=8)

        # ─── Última sincronización ────────────────────────
        last_frame = tk.LabelFrame(
            self.tab_sync, text=" Última sincronización ", font=("Arial", 10, "bold"))
        last_frame.pack(fill="x", **pad)

        self.lbl_last_sync = tk.Label(
            last_frame, text="Sin sincronizaciones registradas",
            font=("Arial", 10), fg="#555")
        self.lbl_last_sync.pack(anchor="w", padx=10, pady=6)

        # ─── Historial / log de errores ───────────────────
        log_frame = tk.LabelFrame(
            self.tab_sync, text=" Historial de sincronizaciones ", font=("Arial", 10, "bold"))
        log_frame.pack(fill=tk.BOTH, expand=True, **pad)

        cols = ("ID", "Tipo", "Fecha y hora", "Estado", "Filas", "Mensaje")
        self.log_tree = ttk.Treeview(log_frame, columns=cols, show="headings", height=10)

        widths = [40, 60, 150, 70, 60, 400]
        for col, w in zip(cols, widths):
            self.log_tree.heading(col, text=col)
            self.log_tree.column(col, width=w, anchor="w")

        scrollbar = ttk.Scrollbar(log_frame, orient="vertical",
                                  command=self.log_tree.yview)
        self.log_tree.configure(yscrollcommand=scrollbar.set)
        self.log_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.log_tree.tag_configure("ok",    background="#e8f5e9")
        self.log_tree.tag_configure("error", background="#ffebee")

        tk.Button(
            self.tab_sync, text="↺ Refrescar historial",
            command=self.refresh_history
        ).pack(anchor="e", padx=16, pady=4)

        # Cargar historial inicial
        self.refresh_history()


    def _build_sql_tab(self):
        self.sql_text = tk.Text(self.tab_sql, height=10, font=("Courier", 10))
        self.sql_text.pack(fill=tk.X, padx=8, pady=8)

        tk.Button(self.tab_sql, text="▶  Ejecutar SQL",
                  command=self.execute_sql).pack(pady=4)

        self.sql_result_frame = tk.Frame(self.tab_sql)
        self.sql_result_frame.pack(fill=tk.BOTH, expand=True)


    def run_sync_in(self):
        self._set_progress(0, "Iniciando Sync-IN…")
        tables_in = list(self.mapping["tables_in"].keys())
        total = len(tables_in)
        done  = [0]

        def progress(table, rows):
            done[0] += 1
            pct = (done[0] / total) * 100
            self._set_progress(pct, f"Sincronizando {table}… ({rows} filas)")

        def run():
            ok, msg = sync_in(self.slave_conn, self.master_conn,
                               self.mapping, progress_callback=progress)
            self.root.after(0, lambda: self._on_sync_done(ok, msg))

        threading.Thread(target=run, daemon=True).start()


    def run_sync_out(self):
        self._set_progress(0, "Iniciando Sync-OUT…")
        tables_out = list(self.mapping["tables_out"].keys())
        total = len(tables_out)
        done  = [0]

        def progress(table, rows):
            done[0] += 1
            pct = (done[0] / total) * 100
            self._set_progress(pct, f"Subiendo {table}… ({rows} cambios)")

        def run():
            ok, msg = sync_out(self.slave_conn, self.master_conn,
                                self.mapping, progress_callback=progress)
            self.root.after(0, lambda: self._on_sync_done(ok, msg))

        threading.Thread(target=run, daemon=True).start()

    def _on_sync_done(self, ok, msg):
        self._set_progress(100 if ok else 0, msg)
        if ok:
            messagebox.showinfo("Sincronización completa", msg)
        else:
            messagebox.showerror("Error en sincronización", msg)
        self.refresh_history()

    def _set_progress(self, pct, text):
        self.progress_var.set(pct)
        self.lbl_progress.config(text=text)
        self.root.update_idletasks()


    #  HISTORIAL


    def refresh_history(self):
        for row in self.log_tree.get_children():
            self.log_tree.delete(row)

        try:
            history = get_sync_history(self.slave_conn, limit=30)
            for h in history:
                sync_id, sync_type, dt, status, message, rows = h
                tag = "ok" if status == "OK" else "error"
                self.log_tree.insert("", "end", values=(
                    sync_id, sync_type,
                    str(dt)[:19], status, rows,
                    message or ""
                ), tags=(tag,))

            if history:
                last = history[0]
                self.lbl_last_sync.config(
                    text=f"{last[1]}  ·  {str(last[2])[:19]}  ·  {last[3]}  ·  {last[5] or ''}"
                )
        except Exception as e:
            self.lbl_last_sync.config(text=f"Error leyendo historial: {e}")

    #  ÁRBOL DE OBJETOS


    def on_tree_click(self, event):
        selected = self.tree.focus()
        text     = self.tree.item(selected, "text")
        parent   = self.tree.item(self.tree.parent(selected), "text")

        if text == "Tables":    self.load_tables()
        elif text == "Views":   self.load_tables()
        elif text in ("Procedures", "Functions"): self.load_procedures_and_functions()
        elif text == "Triggers": self.load_triggers()
        elif text == "Indexes":  self.load_indexes()
        elif text == "Users":    self.load_users()
        elif parent in ("Tables", "Views"):
            self.load_table_data(text)

    def load_tables(self):
        self.tree.delete(*self.tree.get_children(self.tables_node))
        self.tree.delete(*self.tree.get_children(self.views_node))
        tables, views = get_tables_and_views(self.slave_conn)
        for t in tables: self.tree.insert(self.tables_node, "end", text=t)
        for v in views:  self.tree.insert(self.views_node,  "end", text=v)

    def load_procedures_and_functions(self):
        self.tree.delete(*self.tree.get_children(self.procedures_node))
        self.tree.delete(*self.tree.get_children(self.functions_node))
        procs, funcs = get_procedures_and_functions(self.slave_conn, self.database)
        for p in procs: self.tree.insert(self.procedures_node, "end", text=p)
        for f in funcs: self.tree.insert(self.functions_node,  "end", text=f)

    def load_triggers(self):
        self.tree.delete(*self.tree.get_children(self.triggers_node))
        for t in get_triggers(self.slave_conn, self.database):
            self.tree.insert(self.triggers_node, "end", text=t)

    def load_indexes(self):
        self.tree.delete(*self.tree.get_children(self.indexes_node))
        for i in get_indexes(self.slave_conn):
            self.tree.insert(self.indexes_node, "end", text=i)

    def load_users(self):
        self.tree.delete(*self.tree.get_children(self.users_node))
        for u in get_users(self.slave_conn):
            self.tree.insert(self.users_node, "end", text=u)

    def load_table_data(self, table_name):
        self.tabs.select(self.tab_data)
        for w in self.tab_data.winfo_children():
            w.destroy()

        cursor = self.slave_conn.cursor()
        cursor.execute(f"SELECT * FROM `{table_name}` LIMIT 100")
        rows    = cursor.fetchall()
        columns = [d[0] for d in cursor.description]

        tbl = ttk.Treeview(self.tab_data, columns=columns, show="headings")
        tbl.pack(fill=tk.BOTH, expand=True)
        for col in columns:
            tbl.heading(col, text=col)
            tbl.column(col, width=110)
        for row in rows:
            tbl.insert("", "end", values=row)

    #  EDITOR SQL

    def execute_sql(self):
        query  = self.sql_text.get("1.0", tk.END).strip()
        cursor = self.slave_conn.cursor()
        try:
            cursor.execute(query)
            if cursor.description:
                rows    = cursor.fetchall()
                columns = [d[0] for d in cursor.description]
                for w in self.sql_result_frame.winfo_children():
                    w.destroy()
                tbl = ttk.Treeview(self.sql_result_frame, columns=columns, show="headings")
                tbl.pack(fill=tk.BOTH, expand=True)
                for col in columns:
                    tbl.heading(col, text=col)
                    tbl.column(col, width=120)
                for row in rows:
                    tbl.insert("", "end", values=row)
            else:
                self.slave_conn.commit()
                messagebox.showinfo("Éxito", "Sentencia ejecutada correctamente")
        except Exception as e:
            messagebox.showerror("Error SQL", str(e))

    #  LOGOUT
    def logout(self):
        self.slave_conn.close()
        self.master_conn.close()
        self.root.destroy()
        from login import LoginWindow
        LoginWindow().run()

    def run(self):
        self.root.mainloop()
