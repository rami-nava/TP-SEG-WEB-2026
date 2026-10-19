# INSTRUCTIVO — Como funciona la web

## 1. Ficticio S.A. y el flujo de licitaciones
**Ficticio S.A.** es una empresa (ficticia) que compra bienes y servicios
buscando los mejores precios. Para eso publica **licitaciones**: convocatorias
abiertas donde los **proveedores** registrados presentan **propuestas** con su
oferta economica y el detalle de lo que ofrecen. El **administrador** de la
empresa revisa las propuestas de cada licitacion y define su estado
(pendiente / aprobada / rechazada / seleccionada / no seleccionada).

## 2. Roles
| Rol | Quien es | Que puede hacer |
|-----|----------|-----------------|
| **usuario** (proveedor) | Empresas proveedoras | Ver licitaciones abiertas, presentar propuestas, seguir el estado de sus propias propuestas, editar su perfil. |
| **admin** | Personal de Ficticio S.A. (admin pleno) | Todo lo del panel de administracion: crear licitaciones, ver TODAS las propuestas, descargar reportes internos y **adjudicar** (seleccionar la propuesta ganadora, lo que cierra la licitacion). |
| **adminRevision** | Personal de revision de Ficticio S.A. | Entra al panel y revisa propuestas: **solo puede aprobar/rechazar** (y marcar pendiente). **No puede adjudicar**: no ve la opcion "Seleccionada" y el endpoint le responde `403` si la fuerza. |

## 3. Recorrido por las pantallas
| Ruta | Pantalla | Proposito |
|------|----------|-----------|
| `/` | **Index** | Listado publico de licitaciones (tarjetas con estado y fecha de cierre). |
| `/login` | **Login** | Autenticacion. Emite la cookie de sesion. |
| `/logout` | — | Cierra la sesion (borra la cookie). |
| `/propuesta/<id>` | **Nueva propuesta** | Formulario para que un proveedor logueado presente una oferta: razon social, CUIT, monto, **descripcion**, observaciones. |
| `/mis-propuestas` | **Seguimiento** | El proveedor ve el estado de sus propias propuestas. |
| `/perfil` | **Perfil** | Datos de la cuenta; permite editar el nombre de la empresa. |
| `/admin` | **Panel admin** | (solo admin) Lista de licitaciones con conteo de propuestas + reportes descargables. |
| `/admin/licitacion/<id>` | **Propuestas de una licitacion** | (solo admin) Tabla con todas las propuestas de esa licitacion, incluida la descripcion. |
| `/admin/nueva-licitacion` | **Nueva licitacion** | (solo admin) Alta de una licitacion. |
| `/admin/descargar?file=...` | — | (solo admin) Descarga de reportes internos. |