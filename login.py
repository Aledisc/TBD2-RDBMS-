import tkinter as tk
from tkinter import messagebox
from db_connection import create_connection
import mysql.connector
from main_window import MainWindow

class LoginWindow:

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Login - Database Manager TBD2")
        self.root.geometry("1500x700")

        center_frame = tk.Frame(self.root)
        center_frame.pack(expand=True)

        tk.Label(center_frame, text="Proyecto: Database manager - TBD2", font=("Arial", 20)).pack(pady=30)

        
        tk.Label(center_frame, text="Host").pack(pady=15)
        self.host_entry = tk.Entry(center_frame, width=40)
        self.host_entry.pack(ipady=5)

        tk.Label(center_frame, text="Usuario").pack(pady=15)
        self.user_entry = tk.Entry(center_frame, width=40)
        self.user_entry.pack(ipady=5)

        tk.Label(center_frame, text="Password").pack(pady=15)
        self.password_entry = tk.Entry(center_frame, width=40, show="*")
        self.password_entry.pack(ipady=5)

        tk.Label(center_frame, text="Base de Datos").pack(pady=15)
        self.db_entry = tk.Entry(center_frame, width=40)
        self.db_entry.pack(ipady=5)

        self.login_button = tk.Button(
            center_frame,
            text="Conectar",
            width=20,
            height=2,
            command=self.login
        )
        self.login_button.pack(pady=40)

    def login(self):
        try:
            print("Botón presionado")

            host = self.host_entry.get()
            user = self.user_entry.get()
            password = self.password_entry.get()
            database = self.db_entry.get()
            #CONSTANTE SOLO PARA AUTOMATIZAR TESTING QUITAR EN ENTREGA FINAL OJALA LEAS ESTO YO DEL FUTURO!!!
            self.host_entry.insert(0, "localhost")
            self.user_entry.insert(0, "root")
            self.password_entry.insert(0, "123456")
            self.db_entry.insert(0, "tbd2_python")

            print("Intentando conectar...")
            conn = create_connection(host, user, password, database)

            if conn:
                print("Conectado con exito")
                messagebox.showinfo("Éxito", "Conexión exitosa")
                print("Conectado correctamente")
                self.root.destroy()

                main_app = MainWindow(conn, database)
                main_app.run()
            else:
                messagebox.showerror("Error", "No se pudo conectar")

        except Exception as e:
            print("ERROR GENERAL:", e)
            messagebox.showerror("Error", str(e))


    def run(self):
        self.root.mainloop()
