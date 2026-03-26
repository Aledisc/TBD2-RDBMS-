# Sincronizador Pagila – TBD2

## Estructura del proyecto

```
pagila_sync/
├── 01_slave_schema.sql   ← Correr UNA vez en MySQL para crear toda la base de datos 
                           (OJO 👁️👁️👁️👁️ POSIBLE ERROR: Si no se tiene configurado el PATH de MySql
                           se tiene que buscar donde esta instalado pues)
├── mapping.json          ← Mapeo de tablas y campos entre motores
├── main.py               ← Punto de entrada
├── login.py              ← Ventana de conexión dual
├── main_window.py        ← Dashboard de sincronización
├── sync.py               ← Lógica Sync-IN y Sync-OUT
├── db_connection.py      ← Conexiones MySQL + PostgreSQL
└── metadata.py           ← Consultas de metadatos MySQL
```

## Instalación de dependencias

```bash
pip install mysql-connector-python psycopg2-binary
```
(VERSIÓN ESPECíFICA A USAR: 8.0.24, las nuevas me dieron problema) 

## Pasos para correr

1. **Crear el esquema SLAVE en MySQL:**
   ```bash
   mysql -u root -p < 01_slave_schema.sql
   ```

2. **Verificar que PostgreSQL con Pagila esté corriendo.**

3. **Ejecutar la app:**
   ```bash
   python main.py
   ```

4. En la pantalla de login:
   - SLAVE: `localhost / root / tu_password / pagila_slave`
   - MASTER: `localhost / postgres / tu_password / pagila`

5. En el Dashboard:
   - **Sync-IN** → Descarga catálogo del MASTER al SLAVE
   - **Sync-OUT** → Sube cambios locales del SLAVE al MASTER

## Flujo de datos

```
PostgreSQL MASTER (pagila)
        ↓ Sync-IN: actor, film, inventory, etc.
MySQL SLAVE (pagila_slave)
        ↓ Triggers capturan cambios en customer/rental/payment → _log
        ↑ Sync-OUT: sube _log al MASTER y los limpia
```
