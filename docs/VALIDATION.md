# Auditoría y validaciones reales — 24 de octubre de 2026

Zona: America/Santiago. Resultados locales; no son ejecuciones de GitHub Actions.
Los registros crudos se mantienen en `artifacts/checks/` (ignorado), sujetos a
revisión antes de usarlos como evidencia. No contienen resultados AWS fabricados.

## Reauditoría del verificador Python — estado actual

Ejecución local del 24-10-2026 en `feature/fase1-iac`, conservando los cambios
existentes y HEAD `7869232`. Esta sección actualiza el estado; las secciones
posteriores conservan la auditoría inicial como historial. Logs nuevos en
`artifacts/recheck/`, excluidos de Git. No hubo instalación de Python/paquetes,
cambios de herramientas globales ni cambios de recursos Terraform.

### Error original y causa raíz comprobada

`.venv/Scripts/python.exe scripts/check_repository.py` devolvió exit 1 con
`Exactly one ingress resource required; no additional SSH/other ingress`.
Se inspeccionó el verificador completo y los 12 archivos de los tres módulos.
El entorno es Python 3.13.2, python-hcl2 8.1.4 y PyYAML 6.0.3.

La llamada `hcl2.load(stream)` de la línea 26 del verificador ANTERIOR conservaba
las comillas en las etiquetas y literales. El AST contenía la clave
`'"aws_vpc_security_group_ingress_rule"'`, mientras el filtro de las líneas 31–33
comparaba con `aws_vpc_security_group_ingress_rule`, sin esas comillas.
La extracción produjo 10 bloques de recursos pero **cero ingress reconocidos**.
No se trataba de dos entradas ni de una salida real contabilizada incorrectamente.
El diagnóstico reproducible está en `artifacts/recheck/parser-diagnosis.json`.

Inventario comprobado en `modules/security/main.tf`:

| Línea | Recurso | Dirección/alcance |
|---|---|---|
| 1 | `aws_security_group.web` | SG sin ingress inline |
| 8 | `aws_vpc_security_group_ingress_rule.http` | Una entrada TCP/80, `0.0.0.0/0` |
| 17 | `aws_vpc_security_group_egress_rule.bootstrap` | Salida TCP/80 y TCP/443 mediante for_each |

No hay ningún `aws_security_group_rule` en los módulos ni otras reglas de entrada.
Se detectó además un defecto latente: el filtro anterior contaba cualquier
`aws_security_group_rule` como ingress, aunque su `type` fuera `egress`.

### Corrección y justificación

- `scripts/check_repository.py`: usa la opción oficial
  `SerializationOptions(strip_string_quotes=True)` en python-hcl2 8, que normaliza
  etiquetas **y valores**. Conserva la API del parser de Checkov y su envoltura de
  atributos escalares, distinguiéndola de las listas CIDR. No se hicieron
  comparaciones por substring ni se quitaron restricciones de seguridad.
- La clasificación legacy utiliza `type` literal: solo `ingress` cuenta como
  entrada; `egress` no cuenta; una dirección desconocida falla explícitamente.
  Tanto reglas modernas como legacy deben cumplir TCP, puertos 80–80 y origen
  público IPv4 exacto, sin selectores de origen adicionales.
- Se conservan las prohibiciones de ingress inline y key_name; se rechazan también
  ingress inline dinámicos y multiplicidad no comprobable por count/for_each.
  El for_each del EGRESO existente sigue siendo válido.
- Se separaron funciones importables de la ejecución CLI mediante main guard para
  probar el parser/política sobre HCL temporal, sin ejecutar otros controles al importar.
- `tests/test_check_repository.py`: 20 tests con HCL real temporal y subcasos de
  HTTP válido, egress moderno/legacy, SSH en ambos formatos, segunda entrada,
  protocolo/puertos/orígenes incorrectos, dirección desconocida, inline/dynamic y
  count/for_each. Las pruebas no invocan Terraform ni AWS.
- `requirements-repository.txt` declara python-hcl2 8.1.4 y PyYAML 6.0.3 para
  `.venv`; `requirements-ci.txt` declara explícitamente bc-python-hcl2 0.4.3,
  usado por Checkov en Python 3.12. No se instalan ambos parsers juntos porque
  publican el mismo import `hcl2`.
- `.github/workflows/ci.yml`: ejecuta regresiones y verificador con el parser de
  Checkov y agrega un job aislado Python 3.13 con las dependencias del verificador.
  Se mantienen triggers, permisos de lectura y ausencia de operaciones AWS.
- `scripts/Invoke-Checks.ps1` prefiere `.venv` para el verificador/regresiones;
  Checkov conserva el Python 3.12 existente. README actualizado para esos entornos.

### Nuevas ejecuciones y resultados

| Comando/control | Resultado real de esta reauditoría |
|---|---|
| `.venv/Scripts/python.exe scripts/check_repository.py` | PASS, exit 0 |
| `.venv/Scripts/python.exe -m unittest discover -s tests -p 'test_*.py' -v` | PASS: 20 tests, exit 0, Python 3.13.2/python-hcl2 8.1.4 |
| Mismas regresiones con `.tools/python/python.exe` | PASS: 20 tests, exit 0, parser existente de Checkov |
| Verificador con `.tools/python/python.exe` | PASS, exit 0 |
| `.venv/Scripts/python.exe -m pip check` | PASS: No broken requirements found |
| `terraform fmt -check -recursive` | PASS, exit 0; no se reformateó ni modificó Terraform |
| `terraform validate -no-color` | FAIL/BLOQUEADO, exit 1: Failed to load plugin schemas / GetProviderSchema sin respuesta |
| `terraform test -no-color` | FAIL/BLOQUEADO, exit 1: 0 aprobados, 2 fallidos, 6 omitidos por carga del esquema del provider |
| TFLint 0.61.0, recursive/max-workers=1/config absoluta | PASS, exit 0, plugins existentes |
| Checkov 3.2.495, perfil existente | PASS, exit 0: 10 aprobadas, 0 fallidas, 0 omitidas |
| actionlint 1.7.7, CI y candidato disabled | PASS, exit 0, sin shellcheck externo |
| `git diff --check` | PASS, sin errores |
| Revisión de patrones de secretos y gitignore | Sin coincidencias dirigidas; .venv/.tools/state/planes/credenciales excluidos, lock no ignorado |

Antes de ejecutar Terraform test se volvieron a leer ambos `.tftest.hcl`: contienen
`mock_provider "aws" {}`, sin providers reales ni overrides de providers. Los apply
dentro de estas pruebas son operaciones mock; no se ejecutó apply/destroy por CLI.

Los resultados `validate válido` y `8 passed` informados por el usuario corresponden
a ejecuciones previas. **Esta sesión no los reprodujo**: el provider no devolvió su
esquema. No se debilitó ninguna aserción ni se atribuyó ese bloqueo al verificador.
El diagnóstico de mTLS de la auditoría inicial se conserva más abajo; no se
modificaron certificados, antivirus, firewall ni autenticación AWS.

También se confirmó nuevamente la causa local con
`terraform validate -no-tests -no-color` y log DEBUG: exit 1; el canal
`127.0.0.1:10000` rechazó el handshake con
`x509: certificate signed by unknown authority`. Fuente nueva:
`artifacts/recheck/provider-debug.log` (24-10-2026, 11:15, UTC−03:00).
No es un error de credenciales AWS. No se cambió código Terraform para intentar
ocultar este fallo ni se desactivó TLS.

No se ejecutó GitHub Actions remoto; los jobs solo quedaron revisados localmente.
`deploy.yml.disabled` sigue inactivo y no existe `deploy.yml`. No se configuraron
credenciales ni se ejecutaron operaciones remotas Git, PR o despliegue.
Siguen pendientes plantilla oficial, parámetros reales, guía institucional,
autenticación/backend, revisión PR y evidencias AWS/HTTP/limpieza. CE6 permanece
parcial mientras no se acrediten validación/pruebas completas y ejecución CI real.

Referencia técnica de la API consultada: Amplify Education. (s. f.). *python-hcl2
8.1.4: API y SerializationOptions*. https://github.com/amplify-education/python-hcl2/blob/v8.1.4/hcl2/api.py

## Estado inicial constatado

- Rama `feature/fase1-iac`, seguimiento de `origin/feature/fase1-iac`; HEAD `7869232`.
  `main` también apuntaba a `7869232`. No se hizo fetch ni se modificó el remoto.
- README y .gitignore versionados; 14 archivos Terraform existentes de cero bytes
  (5 en root y 9 en módulos),
  sin seguimiento. Directorios de plantilla, tests y workflows vacíos.
- Terraform 1.16.6 instalado en WinGet; el sandbox denegó su ejecución inicial.
  La ejecución autorizada fuera del sandbox sí confirmó la versión Windows AMD64.
- AWS CLI, TFLint y Checkov no estaban disponibles en PATH. Python de WindowsApps
  era un alias; se preparó Python 3.12.10 embebido dentro de `.tools/` para controles.
- Git reportó propietario diferente en sandbox. Se usó `-c safe.directory=...`
  limitado al comando, sin modificar configuración global. Origin coincide con
  el repositorio individual indicado.

## Resultados comprobados de la auditoría inicial (histórico)

| Comprobación | Resultado real |
|---|---|
| `terraform init -backend=false -input=false` | PASS: AWS Provider 6.42.0 descargado, firma HashiCorp verificada y lock generado |
| Init posterior `-lockfile=readonly -plugin-dir=.terraform/providers` | PASS, exit 0, usando provider local y módulos de pruebas registrados |
| `terraform fmt -recursive` y `terraform fmt -check -recursive` | PASS; comprobación final exit 0 |
| `terraform validate` / `validate -no-tests` | FAIL/BLOQUEADO, exit 1: mTLS local rechazado al cargar esquema del provider, certificado de autoridad desconocida |
| `terraform test` | Suite inicial falló por referencia inválida y plugin. Tras corregir referencia, ejecución filtrada del root: exit 1, 0 aprobados, 1 fallido y 3 omitidos por mTLS; no se certifica ninguna aserción |
| TFLint 0.61.0 `--init` | PASS: plugin AWS 0.40.0 instalado; firma y checksum verificados por el instalador |
| TFLint `--recursive --max-workers=1` | PASS, exit 0. Config raíz llama módulos locales; recorrido de subdirectorios adicional |
| Política `python scripts/check_repository.py` | PASS, exit 0: estructura, AST de ingreso único HTTP/sin key_name, YAML y acciones fijadas a SHA |
| Checkov 3.2.495, perfil `.checkov.yml` | PASS, exit 0: 10 comprobaciones aprobadas, 0 fallidas, 0 omitidas en el perfil seleccionado |
| actionlint 1.7.7, CI y candidato desactivado | PASS, exit 0, sin shellcheck externo. ZIP oficial verificado por checksum |
| Parser PowerShell sobre scripts | PASS de sintaxis; no equivale a ejecutar verificación AWS o limpieza |
| Búsqueda de patrones de secretos | Sin coincidencias de claves AWS AKIA/ASIA, tokens GitHub ni cabeceras de claves privadas en archivos de proyecto |
| `git diff --check` | Sin errores de whitespace en cambios versionados; archivos nuevos revisados además con parsers/controles |
| Previsualización de ZIP `Build-Submission.ps1 -Preview` | PASS, exit 0: incluye lock, módulos, tests, workflows y docs; excluye herramientas/state/planes; no crea ZIP |
| Reglas de ignore | PASS: herramientas, cache Terraform, artefactos, tfvars, state, planes y .aws ignorados; lock NO ignorado |

El comando offline usa argumentos entre comillas/array en PowerShell para evitar
que `-plugin-dir=.terraform/providers` se divida en argumentos posicionales.
El lock real incluye hashes publicados y selección 6.42.0; no se inventó su contenido.
CI usa `-lockfile=readonly`. Las herramientas y paquetes locales no entran en Git/ZIP.

## Incidencias y correcciones

1. Tras añadir módulos alternativos de test hubo que repetir init para registrarlos.
2. `expect_failures` no admite la referencia a recurso de un módulo hijo utilizada
   inicialmente. La prueba negativa se movió al módulo compute como módulo bajo
   prueba, apuntando directamente a `aws_instance.portal`.
3. Hubo timeouts/GetProviderSchema sin respuesta del provider AWS en Windows.
   Se repitió de forma aislada, aumentó timeout de arranque y limpiaron únicamente
   procesos de esta sesión que habían quedado huérfanos. No se deshabilitaron
   firewall, antivirus ni otras protecciones. El diagnóstico aislado finalmente
   registró `transport: authentication handshake failed: tls: failed to verify
   certificate: x509: certificate signed by unknown authority` en la conexión
   local `127.0.0.1` entre Terraform y provider. Esto bloquea obtener el esquema;
   no equivale a un error de autenticación con AWS ni demuestra un fallo HCL.
   La causa externa del certificado no se atribuye a un producto específico.
4. Se limitó TFLint a un worker para reducir concurrencia. CI y runner local pasan
   configuración absoluta para que cada carpeta reciba también las reglas AWS.
5. El parser HCL de Checkov devuelve atributos como listas; se corrigió el acceso
   a literales del control de red y después pasó. No era una regla HTTP incorrecta.
6. Windows PowerShell convierte stderr nativo redirigido en ErrorRecord. El runner
   captura el exit code con ErrorActionPreference local apropiada, sin confundir
   trazas informativas con fallos. TFLint terminó en 0 pese a trazas debug en stderr.
7. El pin TFLint v4 era un tag anotado: se resolvió a commit
   `90f302c255ef959cbfb4bd10581afecdb7ece3e6`. No se dejó un hash supuesto.
8. La primera llamada a Checkov fue durante instalación incompleta y falló por
   módulo aún ausente. No se interpreta como análisis de seguridad ejecutado.
   Tras completar instalación se repitió: 10 PASS, 0 FAIL, exit 0.
9. Se consultó Docker local como alternativa Linux de validación: cliente presente,
   daemon `dockerDesktopLinuxEngine` no disponible. No se inició Docker ni se
   alteraron servicios o certificados para sortear el problema. WSL solo enumeró
   `docker-desktop`; no hay una distribución Ubuntu independiente disponible.
10. La política de Windows PowerShell bloqueó scripts .ps1 al invocarlos directamente.
    La previsualización del ZIP pasó con RemoteSigned limitado al proceso, sin
    modificar política global ni generar una entrega final. Se documentó el comando.

Los cinco controles quedan: formato PASS, validación BLOQUEADA por mTLS, pruebas
sin suite final aprobada por el mismo bloqueo, lint PASS y seguridad PASS para
el perfil declarado. No presentar esto como cinco controles aprobados. Ejecutar
validate/test en una consola/entorno donde el canal local del provider sea confiable
o en CI Linux autorizado, sin desactivar TLS ni introducir credenciales AWS.

En Windows el filtro de la ejecución final fue `-filter=tests\architecture.tftest.hcl`.
El intento con separadores `/` no seleccionó pruebas y devolvió 0 con advertencia;
no se contó como éxito. El intento con ruta nativa sí ejecutó el archivo corregido
y dejó el mismo error x509 en `test-debug.log`. El archivo `modules.tftest.hcl`
no se volvió a ejecutar después de confirmar este bloqueo común del provider.
La previsualización final del ZIP listó 44 archivos y ninguna ruta prohibida.
HEAD final sigue en `7869232`, sobre `feature/fase1-iac`, con cambios locales sin commit.

## No ejecutado ni acreditado

Plan contra AWS real, apply, destroy, autenticación, configuración real de backend,
consulta AWS, HTTP del portal, aprobación de environment, corrida de Actions,
commits/push/PR/revisión, ZIP final y PDF final. Los scripts y el workflow candidato
son preparación para esas etapas, no evidencias de haberlas completado.

El usuario confirmó que obtendrá los datos institucionales después; por tanto no
se rellenan región, número de lista, tipo EC2, identidad, autenticación ni backend.
La plantilla docente original sigue ausente. No se ha añadido un portal sustituto.
