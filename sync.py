"""
sync.py  –  Lógica de sincronización Master ↔ Slave
Proyecto: Sincronizador Pagila | TBD2
"""

import json
import datetime
import mysql.connector
import psycopg2
from psycopg2.extras import RealDictCursor
import os

# ──────────────────────────────────────────────
#  Carga del mapping
# ──────────────────────────────────────────────

def load_mapping(path=None):
    if path is None:
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mapping.json")
    with open(path, "r") as f:
        return json.load(f)


# ──────────────────────────────────────────────
#  Conexiones
# ──────────────────────────────────────────────

def connect_slave(host, user, password, database):
    """Conexión al SLAVE (MySQL)."""
    return mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        database=database,
        connection_timeout=5
    )

def connect_master(host, user, password, database, port=5432):
    """Conexión al MASTER (PostgreSQL)."""
    return psycopg2.connect(
        host=host,
        user=user,
        password=password,
        dbname=database,
        port=port,
        connect_timeout=5
    )


# ──────────────────────────────────────────────
#  Registro de resultado en sync_log
# ──────────────────────────────────────────────

def _log_sync(slave_conn, sync_type, status, message="", rows=0):
    cursor = slave_conn.cursor()
    cursor.execute(
        """INSERT INTO sync_log (sync_type, sync_datetime, status, message, rows_affected)
           VALUES (%s, %s, %s, %s, %s)""",
        (sync_type, datetime.datetime.now(), status, message, rows)
    )
    slave_conn.commit()


# ──────────────────────────────────────────────
#  SYNC-IN  (MASTER → SLAVE)
# ──────────────────────────────────────────────

def sync_in(slave_conn, master_conn, mapping, progress_callback=None):
    tables_in  = mapping["tables_in"]
    master_cur = master_conn.cursor(cursor_factory=RealDictCursor)
    slave_cur  = slave_conn.cursor()

    total_rows = 0
    errors     = []

    # Columnas exactas por tabla (solo las que existen en MySQL)
    columns_map = {
        "actor":         ["actor_id", "first_name", "last_name", "last_update"],
        "category":      ["category_id", "name", "last_update"],
        "language":      ["language_id", "name", "last_update"],
        "film":          ["film_id", "title", "description", "release_year",
                          "language_id", "rental_duration", "rental_rate",
                          "length", "replacement_cost", "rating", "last_update"],
        "film_actor":    ["actor_id", "film_id", "last_update"],
        "film_category": ["film_id", "category_id", "last_update"],
        "country":       ["country_id", "country", "last_update"],
        "city":          ["city_id", "city", "country_id", "last_update"],
        "address":       ["address_id", "address", "address2", "district",
                          "city_id", "postal_code", "phone", "last_update"],
        "store":         ["store_id", "manager_staff_id", "address_id", "last_update"],
        "staff":         ["staff_id", "first_name", "last_name", "address_id",
                          "email", "store_id", "active", "username", "last_update"],
        "inventory":     ["inventory_id", "film_id", "store_id", "last_update"],
    }

    order = [
        "language", "actor", "category", "country", "city",
        "address", "store", "staff", "film", "film_actor",
        "film_category", "inventory"
    ]

    # Desactivar foreign keys mientras insertamos
    slave_cur.execute("SET FOREIGN_KEY_CHECKS = 0")
    slave_conn.commit()

    for table in order:
        info    = tables_in[table]
        pk      = info["pk"]
        columns = columns_map[table]
        col_str = ", ".join(columns)

        try:
            master_cur.execute(f"SELECT {col_str} FROM {table}")
            rows = master_cur.fetchall()

            if not rows:
                continue

            placeholder  = ", ".join(["%s"] * len(columns))
            pk_list      = [pk] if isinstance(pk, str) else pk
            update_parts = ", ".join(
                f"`{c}` = VALUES(`{c}`)"
                for c in columns if c not in pk_list
            )

            sql = (
                f"INSERT INTO `{table}` ({col_str}) VALUES ({placeholder}) "
                f"ON DUPLICATE KEY UPDATE {update_parts}"
            )

            values = [tuple(row[c] for c in columns) for row in rows]
            slave_cur.executemany(sql, values)
            slave_conn.commit()

            total_rows += len(rows)
            if progress_callback:
                progress_callback(table, len(rows))

        except Exception as e:
            errors.append(f"{table}: {e}")
            slave_conn.rollback()

    # Reactivar foreign keys
    slave_cur.execute("SET FOREIGN_KEY_CHECKS = 1")
    slave_conn.commit()

    if errors:
        msg = " | ".join(errors)
        _log_sync(slave_conn, "IN", "ERROR", msg, total_rows)
        return False, msg

    _log_sync(slave_conn, "IN", "OK", "Sync-IN completado", total_rows)
    return True, f"Sync-IN OK — {total_rows} filas sincronizadas"

def sync_out(slave_conn, master_conn, mapping, progress_callback=None):
    """
    Lee los _log del SLAVE, aplica los cambios en PostgreSQL (MASTER),
    y limpia los _log si todo fue exitoso.
    """
    tables_out = mapping["tables_out"]
    slave_cur  = slave_conn.cursor(dictionary=True)
    master_cur = master_conn.cursor()

    total_rows = 0
    errors     = []

    for table, info in tables_out.items():
        log_table    = info["log_table"]
        master_table = info["master_table"]
        pk           = info["pk"]
        fields       = info["fields"]

        try:
            # 1. Leer entradas del log ordenadas por log_id (cronológico)
            slave_cur.execute(
                f"SELECT * FROM `{log_table}` ORDER BY log_id ASC"
            )
            log_rows = slave_cur.fetchall()

            if not log_rows:
                continue

            for log_row in log_rows:
                op  = log_row["operation"]
                pk_val = log_row[pk]

                if op == "D":
                    master_cur.execute(
                        f"DELETE FROM {master_table} WHERE {pk} = %s",
                        (pk_val,)
                    )

                elif op in ("I", "U"):
                    values = {f: log_row[f] for f in fields}
                    col_str     = ", ".join(values.keys())
                    placeholder = ", ".join(["%s"] * len(values))
                    val_list    = list(values.values())

                    # PostgreSQL: INSERT … ON CONFLICT DO UPDATE
                    update_parts = ", ".join(
                        f"{c} = EXCLUDED.{c}"
                        for c in values if c != pk
                    )
                    sql = (
                        f"INSERT INTO {master_table} ({col_str}) "
                        f"VALUES ({placeholder}) "
                        f"ON CONFLICT ({pk}) DO UPDATE SET {update_parts}"
                    )
                    master_cur.execute(sql, val_list)

            master_conn.commit()
            total_rows += len(log_rows)

            # 2. Limpiar el log
            slave_cur.execute(f"DELETE FROM `{log_table}`")
            slave_conn.commit()

            if progress_callback:
                progress_callback(table, len(log_rows))

        except Exception as e:
            errors.append(f"{table}: {e}")
            master_conn.rollback()
            slave_conn.rollback()

    if errors:
        msg = " | ".join(errors)
        _log_sync(slave_conn, "OUT", "ERROR", msg, total_rows)
        return False, msg

    _log_sync(slave_conn, "OUT", "OK", "Sync-OUT completado", total_rows)
    return True, f"Sync-OUT OK — {total_rows} cambios subidos al MASTER"


# ──────────────────────────────────────────────
#  Historial de sincronizaciones
# ──────────────────────────────────────────────

def get_sync_history(slave_conn, limit=20):
    cursor = slave_conn.cursor()
    cursor.execute(
        """SELECT sync_id, sync_type, sync_datetime, status, message, rows_affected
           FROM sync_log ORDER BY sync_id DESC LIMIT %s""",
        (limit,)
    )
    return cursor.fetchall()
