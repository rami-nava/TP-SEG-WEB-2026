# ==========================================================================
#  Se ejecuta A MANO (o programado con cron / tarea semanal). Consulta la
#  base de datos EN EL MOMENTO y deja un archivo CSV en la carpeta reportes/
#  con la fecha actual en el nombre:  reportes/reporte_YYYY-MM-DD.csv
#
#      python generar_reporte.py
# ==========================================================================

import os
import csv
import sqlite3
from datetime import date

DB_PATH = "database.db"
REPORTES_DIR = "reportes"


def generar_reporte():
    if not os.path.exists(DB_PATH):
        print(f"[!] No existe {DB_PATH}. Ejecuta primero:  python init_db.py")
        return

    os.makedirs(REPORTES_DIR, exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    filas = conn.execute(
        """SELECT l.titulo        AS licitacion,
                  p.razon_social  AS proveedor,
                  p.cuit          AS cuit,
                  p.email_contacto AS contacto,
                  p.monto         AS monto,
                  p.estado        AS estado
           FROM propuestas p
           JOIN licitaciones l ON l.id = p.licitacion_id
           ORDER BY l.id, p.monto ASC"""
    ).fetchall()
    conn.close()

    hoy = date.today().isoformat()      
    nombre = f"reporte_{hoy}.csv"
    ruta = os.path.join(REPORTES_DIR, nombre)

    with open(ruta, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["licitacion", "proveedor", "cuit", "contacto",
                         "monto", "estado"])
        for fila in filas:
            writer.writerow([
                fila["licitacion"], fila["proveedor"], fila["cuit"],
                fila["contacto"],
                f"{fila['monto']:.0f}" if fila["monto"] is not None else "",
                (fila["estado"] or "").replace("_", " "),
            ])

    print(f"[+] Reporte generado: {ruta}")
    print(f"    - {len(filas)} propuestas incluidas")
    print(f"    - fecha del reporte: {hoy}")
    print("[+] Ya aparece en el panel admin -> 'Reportes descargables'.")


if __name__ == "__main__":
    generar_reporte()
