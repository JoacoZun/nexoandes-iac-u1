# Dependencia docente pendiente

Aquí se debe incorporar `user_data_v1.sh.tpl` ORIGINAL proporcionado por el docente.
No se ha recibido y no se incluye un reemplazo. La fixture en `tests/fixtures/`
solo prueba el renderizado con mocks, no sirve un portal y no es desplegable.

Antes de planificar: confirmar sistema operativo/arquitectura, variables que
espera el script, permisos y dependencias de red. Configurar
`user_data_template_path` y `portal_parameters` según ese contrato real.
Terraform interpreta `${...}` y `%{...}`: si existen expansiones shell literales,
escaparlas como `$${...}` y `%%{...}` únicamente donde corresponda, conservando
la lógica original. Registrar origen, fecha y SHA256 del archivo recibido y
documentar cada ajuste. No pasar secretos: user_data puede aparecer en state.

Un renderizado vacío, archivo ausente o variable de plantilla faltante bloquea
la precondición de EC2. Esto no certifica que una plantilla arbitraria sea oficial:
esa autenticidad debe revisarse en PR antes de habilitar un despliegue.
