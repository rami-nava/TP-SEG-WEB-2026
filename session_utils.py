# ==========================================================================
#  session_utils.py  --  Manejo de la cookie de sesion personalizada
# --------------------------------------------------------------------------
#  La sesion NO usa flask.session (que serializa con JSON). En su lugar se
#  serializa un objeto Usuario con pickle y se firma con HMAC-SHA256.
#
#  VULNERABILIDAD 4 (Software and Data Integrity Failures):
#  leer_cookie() hace pickle.loads() sobre datos controlables por el cliente.
#  La firma HMAC valida INTEGRIDAD pero NO evita el RCE si la SECRET_KEY se
#  filtra. Con la clave, el atacante puede forjar una
#  cookie con un objeto malicioso cuyo __reduce__ ejecuta codigo arbitrario.
# ==========================================================================

import pickle
import hmac
import hashlib
import base64
from config import SECRET_KEY


class Usuario:
    """Objeto que viaja serializado dentro de la cookie de sesion."""

    def __init__(self, id, username, rol, nombre_empresa):
        self.id = id
        self.username = username
        self.rol = rol
        self.nombre_empresa = nombre_empresa

    def es_admin(self):
        return self.rol == "admin"


def crear_cookie(usuario):
    """Serializa el Usuario con pickle, lo firma con HMAC y lo codifica en b64."""
    data = pickle.dumps(usuario)
    firma = hmac.new(SECRET_KEY, data, hashlib.sha256).hexdigest()
    return base64.b64encode(data).decode() + "." + firma


def leer_cookie(valor):
    """Verifica la firma y deserializa. <-- pickle.loads inseguro (RCE)."""
    datos_b64, firma = valor.rsplit(".", 1)
    data = base64.b64decode(datos_b64)
    esperada = hmac.new(SECRET_KEY, data, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(esperada, firma):
        raise ValueError("Firma invalida")
    return pickle.loads(data)   # <-- deserializacion insegura (RCE)
