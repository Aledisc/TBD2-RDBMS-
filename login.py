
import tkinter as tk
from tkinter import messagebox
from db_connection import create_slave_connection, create_master_connection
import traceback

class LoginWindow:

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Sincronizador Pagila – TBD2")
        self.root.geometry("480x620")
        self.root.resizable(False, False)

        center = tk.Frame(self.root)
        center.pack(expand=True, pady=10)

        tk.Label(center, text="Sincronizador Pagila", font=("Arial", 18, "bold")).pack(pady=8)
        tk.Label(center, text="TBD2 – Master / Slave", font=("Arial", 11)).pack(pady=2)

        # ─── SLAVE (MySQL) ───────────────────────────
        slave_frame = tk.LabelFrame(center, text=" SLAVE — MySQL ",
                                    font=("Arial", 10, "bold"), padx=10, pady=10)
        slave_frame.pack(fill="x", padx=20, pady=8)

        self.slave_host = self._field(slave_frame, "Host",          0, "localhost")
        self.slave_user = self._field(slave_frame, "Usuario",       1, "root")
        self.slave_pass = self._field(slave_frame, "Password",      2, "123456",   show="*")
        self.slave_db   = self._field(slave_frame, "Base de datos", 3, "pagila_slave")

        # ─── MASTER (PostgreSQL) ──────────────────────
        master_frame = tk.LabelFrame(center, text=" MASTER — PostgreSQL ",
                                     font=("Arial", 10, "bold"), padx=10, pady=10)
        master_frame.pack(fill="x", padx=20, pady=8)

        self.master_host = self._field(master_frame, "Host",          0, "localhost")
        self.master_port = self._field(master_frame, "Puerto",        1, "5433")
        self.master_user = self._field(master_frame, "Usuario",       2, "postgres")
        self.master_pass = self._field(master_frame, "Password",      3, "12345",        show="*")
        self.master_db   = self._field(master_frame, "Base de datos", 4, "pagila")


        tk.Button(
            center,
            text="Conectar",
            width=25, height=2,
            font=("Arial", 11),
            command=self.login
        ).pack(pady=18)

    def _field(self, parent, label, row, default="", show=None):

        tk.Label(parent, text=label, anchor="w", width=14).grid(
            row=row, column=0, sticky="w", pady=4)
        entry = tk.Entry(parent, width=26, show=show)
        entry.insert(0, default)
        entry.grid(row=row, column=1, pady=4, padx=5)
        return entry

    def login(self):
        try:
            slave_host = self.slave_host.get()
            slave_user = self.slave_user.get()
            slave_pass = self.slave_pass.get()
            slave_db = self.slave_db.get()

            master_host = self.master_host.get()
            master_port = int(self.master_port.get())
            master_user = self.master_user.get()
            master_pass = self.master_pass.get()
            master_db = self.master_db.get()

            # conectar ──
            slave_conn = create_slave_connection(slave_host, slave_user, slave_pass, slave_db)
            if not slave_conn:
                messagebox.showerror("Error", "No se pudo conectar al SLAVE (MySQL)")
                return

            master_conn = create_master_connection(master_host, master_user, master_pass, master_db, port=master_port)
            if not master_conn:
                messagebox.showerror("Error", "No se pudo conectar al MASTER (PostgreSQL)")
                slave_conn.close()
                return

            messagebox.showinfo("Éxito", "Conexión exitosa a ambas bases de datos ✓")
            self.root.destroy()  # ← ahora sí, después de leer todo

            from main_window import MainWindow
            MainWindow(slave_conn, master_conn, slave_db).run()

        except Exception as e:
            import traceback
            messagebox.showerror("Error", traceback.format_exc())

    def run(self):
        self.root.mainloop()
