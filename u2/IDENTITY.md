# Identidad local U2

Configurada por instrucción explícita del usuario: X=8 ratificado y student=a008
(derivado de X). Curso c50 por sección 50; la equivalencia sección/cNN es asumida,
no una verificación documental docente. No acredita recursos ni ejecución cloud.

`identity.tfvars` está ignorado por Git y no es auto.tfvars: no altera defaults
reutilizables ni fixtures de pruebas. Para consumir esta configuración en una
operación futura autorizada, el root `u2/` necesita el argumento
`-var-file=identity.tfvars`; los roots `u2/aws` y `u2/azure` necesitan
`-var-file=../identity.tfvars`. No ejecutar operaciones cloud por este documento.
No declarar una variable student separada: la composición deriva a008 de X=8.
Build y destinos cloud siguen sin valores inventados.

El backend AWS local `aws/backend.hcl`, también ignorado, apunta exclusivamente a
`u2/c50/a008/aws/terraform.tfstate` en el bucket solicitado. No está inicializado
remotamente. CI y clones nuevos no reciben estos archivos ignorados: deberán
proporcionar parámetros autorizados explícitos cuando exista pipeline de despliegue.
