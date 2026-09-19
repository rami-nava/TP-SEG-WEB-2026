# Portal de Licitaciones — Ficticio S.A. (aplicacion deliberadamente vulnerable)

> ⚠️ **ADVERTENCIA**
> Esta aplicacion contiene **vulnerabilidades intencionales** y fue creada
> exclusivamente como **material educativo** para un Trabajo Practico de
> Seguridad en Aplicaciones Web.

Web de licitaciones de la empresa ficticia **Ficticio S.A.**, que compra
bienes/servicios buscando los mejores precios. Los proveedores presentan
propuestas y un administrador las gestiona.

Incluye una **cadena de 4 vulnerabilidades** que terminan en **RCE**:

1. **Stored XSS** → robar la sesion del administrador.
2. **Broken Authentication / Session Management** → suplantar al admin con su cookie.
3. **Path Traversal / LFI** → leer `config.py` y obtener la `SECRET_KEY`.
4. **Deserializacion insegura (pickle)** → forjar una cookie maliciosa → **RCE**,
   usado para borrar de la BD las propuestas con monto por debajo de un umbral configurable.

## Requisitos
- Python 3
- `pip install -r requirements.txt`

## Instalacion y ejecucion

# 1) (opcional) entorno virtual
python3 -m venv venv && source venv/bin/activate

# 2) dependencias
pip install -r requirements.txt

# 3) crear y precargar la base de datos (se puede repetir para reiniciar la BD con datos iniciales)
python init_db.py

# 4) levantar la web
python app.py


Luego abrir: **http://localhost:5000** o **http://127.0.0.1:5000** 



