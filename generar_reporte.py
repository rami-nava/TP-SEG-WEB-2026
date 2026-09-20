# ==========================================================================
#  Reporte GERENCIAL / RESUMEN de licitaciones.
#
#  Se ejecuta A MANO (o programado con cron / tarea semanal). Consulta la
#  base de datos EN EL MOMENTO y deja un archivo CSV en la carpeta reportes/
#  con la fecha actual en el nombre:  reportes/reporte_YYYY-MM-DD.csv
#
#  A diferencia de un volcado crudo de propuestas, este reporte muestra
#  UNA FILA POR LICITACION con metricas agregadas (cantidad de propuestas,
#  monto minimo/maximo y monto adjudicado). No incluye datos sensibles de
#  los proveedores (CUIT, email de contacto ni las ofertas individuales).
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
        """SELECT l.titulo   AS licitacion,
                  l.estado   AS estado_licitacion,
                  COUNT(p.id) AS cant_propuestas,
                  MIN(p.monto) AS monto_min,
                  MAX(p.monto) AS monto_max,
                  MAX(CASE WHEN p.estado IN ('aprobada', 'seleccionada')
                           THEN p.monto END) AS monto_adjudicado
           FROM licitaciones l
           LEFT JOIN propuestas p ON p.licitacion_id = l.id
           GROUP BY l.id, l.titulo, l.estado
           ORDER BY l.id"""
    ).fetchall()
    conn.close()

    def fmt(monto):
        return f"{monto:.0f}" if monto is not None else ""

    hoy = date.today().isoformat()
    nombre = f"reporte_{hoy}.csv"
    ruta = os.path.join(REPORTES_DIR, nombre)

    with open(ruta, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["licitacion", "estado_licitacion", "cant_propuestas",
                         "monto_min", "monto_max", "monto_adjudicado"])
        for fila in filas:
            writer.writerow([
                fila["licitacion"],
                fila["estado_licitacion"],
                fila["cant_propuestas"],
                fmt(fila["monto_min"]),
                fmt(fila["monto_max"]),
                fmt(fila["monto_adjudicado"]),
            ])

    print(f"[+] Reporte generado: {ruta}")
    print(f"    - {len(filas)} licitaciones incluidas")
    print(f"    - fecha del reporte: {hoy}")
    print("[+] Ya aparece en el panel admin -> 'Reportes descargables'.")


if __name__ == "__main__":
    generar_reporte()
