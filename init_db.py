# ==========================================================================
#  init_db.py  --  Crea y precarga la base de datos SQLite (database.db)
# --------------------------------------------------------------------------
#  Al ejecutarse, si database.db existe, la recrea desde cero.
#
#      python init_db.py
# ==========================================================================

import os
import sqlite3

DB_PATH = "database.db"


def recrear_db():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print(f"[*] {DB_PATH} existente eliminado (se recrea desde cero).")

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # ---------------- Esquema ----------------
    c.execute("""
        CREATE TABLE usuarios (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            username       TEXT UNIQUE NOT NULL,
            password       TEXT NOT NULL,
            rol            TEXT NOT NULL,          -- 'admin' | 'usuario'
            nombre_empresa TEXT
        )
    """)

    c.execute("""
        CREATE TABLE licitaciones (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo       TEXT NOT NULL,
            descripcion  TEXT,
            estado       TEXT NOT NULL,            -- 'abierta' | 'cerrada'
            fecha_cierre TEXT
        )
    """)

    c.execute("""
        CREATE TABLE propuestas (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            licitacion_id  INTEGER NOT NULL,
            usuario_id     INTEGER NOT NULL,
            razon_social   TEXT,
            cuit           TEXT,
            monto          REAL,
            descripcion    TEXT,                   -- se renderiza con formato (Markup) sin sanitizar -> VECTOR XSS
            email_contacto TEXT,                   -- medio de contacto (obligatorio)
            estado         TEXT NOT NULL DEFAULT 'pendiente',
            FOREIGN KEY (licitacion_id) REFERENCES licitaciones(id),
            FOREIGN KEY (usuario_id)    REFERENCES usuarios(id)
        )
    """)

    # ---------------- Usuarios ----------------
    usuarios = [
        ("admin",       "admin123", "admin",   "Ficticio S.A."),
        ("proveedor_a", "passa123", "usuario", "Metalurgica Sur SRL"),
        ("proveedor_b", "passb123", "usuario", "Insumos del Norte SA"),
        ("atacante",    "hack123",  "usuario", "Consultora Sombra"),
    ]
    c.executemany(
        "INSERT INTO usuarios (username, password, rol, nombre_empresa) VALUES (?,?,?,?)",
        usuarios,
    )

    # ---------------- Licitaciones ----------------
    licitaciones = [
        ("Compra de 500 notebooks corporativas",
         "Adquisicion de 500 notebooks de gama corporativa con garantia extendida y soporte on-site.",
         "abierta", "2026-12-15"),
        ("Servicio de limpieza edilicia anual",
         "Contratacion del servicio integral de limpieza para las tres sedes de Ficticio S.A. durante 12 meses.",
         "abierta", "2026-11-30"),
        ("Provision de insumos de oficina",
         "Provision trimestral de insumos de oficina (papeleria, toner, articulos varios).",
         "cerrada", "2026-08-01"),
    ]
    c.executemany(
        "INSERT INTO licitaciones (titulo, descripcion, estado, fecha_cierre) VALUES (?,?,?,?)",
        licitaciones,
    )

    # ---------------- Propuestas ----------------
    propuestas = [
        # licitacion_id, usuario_id, razon_social, cuit, monto, descripcion, email_contacto, estado
        (1, 2, "Metalurgica Sur SRL",  "30-11111111-1",  120000.0,
         "Notebooks reacondicionadas, entrega en 30 dias.",
         "ventas@metalurgicasur.com", "pendiente"),
        (1, 3, "Insumos del Norte SA",  "30-22222222-2",  350000.0,
         "Equipos **nuevos** gama media.\nGarantia: 1 anio.",
         "contacto@insumosnorte.com", "pendiente"),
        (1, 4, "Consultora Sombra",     "30-33333333-3",  480000.0,
         "Equipos gama alta.\n**Incluye** soporte on-site por 2 anios.",
         "info@consultorasombra.com", "pendiente"),
        (2, 2, "Metalurgica Sur SRL",  "30-11111111-1",  750000.0,
         "Servicio de limpieza con personal propio y seguros al dia.",
         "ventas@metalurgicasur.com", "pendiente"),
        (2, 3, "Insumos del Norte SA",  "30-22222222-2", 1200000.0,
         "**Servicio integral**\n- Insumos incluidos\n- Maquinaria propia",
         "contacto@insumosnorte.com", "aprobada"),
        # Licitacion 3 (CERRADA / adjudicada): una seleccionada y las demas no seleccionadas.
        (3, 2, "Metalurgica Sur SRL",  "30-11111111-1", 2500000.0,
         "Provision anual completa con deposito dedicado.",
         "ventas@metalurgicasur.com", "seleccionada"),
        (3, 3, "Insumos del Norte SA",  "30-22222222-2",  90000.0,
         "Provision basica trimestral.",
         "contacto@insumosnorte.com", "no_seleccionada"),
    ]
    c.executemany(
        """INSERT INTO propuestas
           (licitacion_id, usuario_id, razon_social, cuit, monto, descripcion,
            email_contacto, estado)
           VALUES (?,?,?,?,?,?,?,?)""",
        propuestas,
    )

    conn.commit()
    conn.close()

    print(f"[+] Base de datos creada en {DB_PATH}")
    print(f"    - {len(usuarios)} usuarios")
    print(f"    - {len(licitaciones)} licitaciones")
    print(f"    - {len(propuestas)} propuestas")
    print("[+] Precarga de datos completada.")


if __name__ == "__main__":
    recrear_db()
