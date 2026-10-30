# Plantilla oficial del Portal Operacional V1

`user_data_v1.sh.tpl` fue entregada por el docente. SHA-256 verificado:
`0f06f8f42390f0f38ea7e0587d6bb314caea734aa44a18645b62eaf06ce639fb`.

El root la integra directamente mediante `templatefile()` y entrega cinco valores:
`student_name`, `student_number`, `environment`, `portal_version` y `project_name`.
No modificar la lógica, HTML, CSS ni las secuencias `$${...}` del archivo oficial.
El CI comprueba su hash y sintaxis Bash antes de validar Terraform.

La fixture en `tests/fixtures/` sigue siendo exclusiva de pruebas históricas y no
es un portal desplegable. No pasar secretos: `user_data` puede aparecer en state.
