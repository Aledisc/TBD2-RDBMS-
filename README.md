RDBMS TBD2 - Proyecto del primer parcial

Por Jorge Discua - 22311096

La aplicación permite conectarse a un servidor MySQL y administrar los principales objetos de una base de datos utilizando sentencias SQL directas, sin emplear ORMs ni el esquema information_schema.
O sea, un RDBMS sencillo.
---

## Objetivo

Desarrollar una aplicación de escritorio que permita:

- Establecer conexión con un servidor MySQL.
- Visualizar los objetos principales de una base de datos.
- Crear tablas y vistas mediante interfaz gráfica.
- Generar y visualizar el DDL de objetos.
- Ejecutar sentencias SQL desde un editor integrado.

---

## Tecnologías Utilizadas

- Python 3.13  
- Tkinter  
- mysql-connector-python (VERSIÓN ESPECíFICA A USAR: 8.0.24, las nuevas me dieron problema) 
- MySQL 8  
- PyCharm  

---

## Arquitectura General

El sistema se encuentra dividido en módulos principales:

- login.py → Maneja autenticación y conexión.
- main_window.py → Ventana principal y lógica de interfaz.
- metadata.py → Obtención de información del motor MySQL.
- main.py → Punto de entrada de la aplicación.

Flujo general:

Login → Validación → Ventana principal → Interacción con objetos

---

## Objetos Soportados

- Tables  
- Views  
- Procedures  
- Functions  
- Triggers  
- Indexes (listado)  
- Users (listado)  

> !!! Algunos objetos como Packages, Sequences o Tablespaces no están disponibles en MySQL y por lo tanto no se implementaron.

---

## Funcionalidades

- Login y logout.
- Exploración de objetos mediante árbol.
- Visualización de registros de tablas y vistas.
- Editor SQL integrado.
- Creación visual de tablas.
- Creación visual de vistas.
- Generación de DDL:
  - Tables
  - Views
  - Procedures
  - Functions
  - Triggers

---

## Ejecución

1. Clonar repositorio.
2. Crear entorno virtual.
3. Instalar dependencias:

```bash
pip install mysql-connector-python==8.0.24

Ejecutar: 
python main.py