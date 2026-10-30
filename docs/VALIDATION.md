# Auditoría y validaciones reales

Zona: America/Santiago. Resultados locales; no son ejecuciones de GitHub Actions.
Los registros crudos se mantienen en `artifacts/checks/` (ignorado), sujetos a
revisión antes de usarlos como evidencia. No contienen resultados AWS fabricados.

## Integración del Portal Operacional V1 — 27-10-2026

Base local inspeccionada: `feature/fase1-iac`, HEAD `9f4ceac`; árbol limpio salvo
los dos materiales oficiales nuevos. `origin/feature/fase1-iac` apunta localmente al
mismo commit, sin ejecutar fetch/push ni asumir una publicación nueva. La integración
posterior descrita aquí permanece sin commit y sin CI remoto.

### Material oficial e integración

- `templates/user_data_v1.sh.tpl`: 7774 bytes; SHA-256 comprobado
  `0f06f8f42390f0f38ea7e0587d6bb314caea734aa44a18645b62eaf06ce639fb`.
  No se modificó su lógica, HTML, CSS ni escapes `$${...}`.
- `docs/README_ESTUDIANTE.md`: leído completo y conservado sin modificaciones.
- El root renderiza la ruta fija con `templatefile()` y las cinco claves exactas:
  `student_name`, `student_number = tostring(var.list_number)`, `environment`,
  `portal_version = "v1"` y `project_name = "NexoAndes Portal Operacional"`.
  El resultado se pasa a `module.compute.user_data`; `aws_instance.portal` conserva
  `user_data_replace_on_change = true`.
- `student_id` conserva nombres/tags; `student_name` es un input obligatorio distinto.
  `list_number` sigue siendo la única fuente del número y ahora valida 1–254 según
  la guía. Default 8 produce `172.16.8.0/24`. `environment` exige `fase1`.
- Compute conserva endpoint metadata enabled, tokens required, hop limit 1, EBS gp3
  cifrado, IP pública, subnet y SG recibidos. Security conserva una única entrada
  pública TCP/80, sin SSH, y egreso TCP/80/443.
- La AMI por data source continúa siendo AL2023 x86_64, configurable con `ami_id`;
  región y tipo permanecen obligatorios. La plantilla requiere systemd, curl y
  dnf/yum/apt. El paquete nginx de AL2023 es compatible con el document root usado;
  otra familia debe verificarse antes del despliegue.

### Resultados locales de esta integración

| Control | Resultado real |
|---|---|
| SHA-256 oficial antes/después | PASS, coincide exactamente |
| `terraform fmt -check -recursive` | PASS |
| `terraform validate -no-color` | BLOQUEADO: el proceso no respondió y fue interrumpido tras espera prolongada |
| `terraform test -no-color` | BLOQUEADO por GetProviderSchema: 0 passed, 2 failed, 6 skipped |
| Terraform console aislada, sin provider | PASS: renderiza parámetros, `${path}` para Bash y `/health.txt` |
| Inspección previa de tests | Ambos `.tftest.hcl` usan `mock_provider "aws"`; ocho runs conservados |
| `scripts/check_repository.py` | PASS |
| Regresiones Python 3.13 | PASS: 20 tests |
| TFLint 0.61.0 | PASS inicial; dos repeticiones finales quedaron sin salida y se interrumpieron. El cambio intermedio fue solo validación 1–254 y pasó `terraform fmt` |
| Checkov 3.2.495, perfil del proyecto | PASS: 10, failed 0, skipped 0 |
| Git Bash `bash -n templates/user_data_v1.sh.tpl` | PASS |
| actionlint 1.7.7 sobre CI y candidato disabled | PASS, sin shellcheck externo |
| `Build-Submission.ps1 -Preview` | PASS: incluye plantilla, README docente y lock; no genera ZIP |
| Patrones dirigidos de secretos | PASS, sin coincidencias; no sustituye revisión humana |
| `git diff --check` | PASS |

El primer `bash` resuelto por PATH era WSL y agotó el tiempo al crear su VM; no
analizó el archivo. Se repitió con `AppData/Local/Programs/Git/bin/bash.exe` y pasó.
Terraform test volvió a fallar antes de las aserciones porque el provider AWS no
respondió a GetProviderSchema. Es consistente con el bloqueo x509/mTLS documentado
en ejecuciones anteriores de este entorno Codex; no se desactivó TLS ni se cambiaron
certificados. Repetir validate/test desde Git Bash del estudiante antes de CI.

No se ejecutaron plan, apply, destroy, llamadas AWS, escrituras Git/GitHub ni cambios
en `deploy.yml.disabled`. No hay evidencia de EC2 operativa, HTTP o limpieza.

## Preparación final anterior — histórico del 24-10-2026

Base auditada: `feature/fase1-iac`, árbol inicialmente limpio, HEAD
`e7f6025bc8fd7e221942c19d3fd0eb579809410b`, cinco commits sobre `main`
(`78692328cfa0536fd80334168a27c5fed9790eef`). Estos cambios nuevos son locales,
sin commit ni publicación. No hubo escrituras GitHub ni llamadas AWS.
Logs nuevos: `artifacts/predeploy/` (ignorado). Las secciones posteriores son
históricas y no representan el estado Git/remoto actual.

### Configuración y auditoría

- `variables.tf`: default de lista 8, conservando validación entera 0–255.
  Network sigue recibiendo el número como input sin default en el módulo.
- `main.tf`: tag `ListNumber` derivado del input; `Student` y los nombres dependen
  del identificador académico obligatorio, que no se inventó.
- `tests/architecture.tftest.hcl`: caso subnet 8 y aserción de identidad/tags.
  Se conservan ocho runs mock, incluido el caso de frontera 255 en otro módulo.
- `terraform.tfvars.example`: ejemplo público incompleto deliberadamente, sin región,
  tipo ni identidad arbitrarios. No se carga automáticamente. El empaquetador admite
  este ejemplo exacto y sigue excluyendo archivos de variables reales.
- Auditoría HCL: diez bloques de recursos, exclusivamente network/security/compute;
  entrada única TCP/80 pública sin SSH, salidas TCP/80 y 443 para bootstrap,
  EC2 con IP pública, IMDSv2 y EBS cifrado. Composición y dependencias conservadas.
  Es inspección estática, no un plan AWS. Fuente: `architecture-audit.json`.
- No se modificaron módulos, lock ni workflows. La plantilla oficial sigue ausente.

### Ejecuciones locales nuevas

| Comando/control | Resultado efectivo |
|---|---|
| `terraform fmt -check -recursive` | PASS, exit 0 |
| `terraform validate -no-color` | BLOQUEADO, exit 1, carga del esquema del provider |
| `terraform test -no-color` | BLOQUEADO, exit 1: 0 aprobados, 2 fallidos, 6 omitidos por esquema |
| `cidrsubnet("172.16.0.0/16", 8, 8)` en console aislada sin provider | PASS: `172.16.8.0/24`; verifica cálculo, no despliegue |
| `.venv/Scripts/python.exe -m unittest discover -s tests -p 'test_*.py' -v` | PASS: 20 tests |
| `.venv/Scripts/python.exe scripts/check_repository.py` | PASS, exit 0 |
| TFLint 0.61.0, recursive/max-workers=1/config absoluta y plugin local | PASS, exit 0 |
| Checkov 3.2.495, perfil existente | PASS: 10 aprobadas, 0 fallidas, 0 omitidas; alcance limitado al perfil |
| actionlint 1.7.7, CI y candidato disabled, `-shellcheck=` | PASS, exit 0; sin shellcheck externo |
| Parser PowerShell de scripts | PASS |
| `Build-Submission.ps1 -Preview` | PASS: 47 archivos, lock y ejemplo incluidos; sin generar ZIP |
| Patrones dirigidos de secretos | Sin coincidencias; no certifica ausencia absoluta de secretos |
| Gitignore | State, planes, credenciales, .venv y .tools excluidos; lock y ejemplo no ignorados |
| `git diff --check` | PASS |

Antes de ejecutar test se inspeccionaron ambos `.tftest.hcl`: usan
`mock_provider "aws" {}`, sin providers reales ni overrides. El DEBUG confirma
a las 13:48 UTC−03 el bloqueo local:
`authentication handshake failed: tls: failed to verify certificate: x509: certificate signed by unknown authority`.
Fuente: `artifacts/predeploy/provider-debug.log`. No se modificaron certificados,
TLS ni herramientas globales. Los nuevos asserts de lista 8 requieren una ejecución
Terraform completa en un entorno funcional. Los anteriores resultados Git Bash
(validate aprobado, ocho tests aprobados) fueron informados por el usuario y no
se atribuyen a esta ejecución.

### Evidencia remota comprobada, distinta de los cambios locales

Consulta REST pública de solo lectura: [Draft PR #1](https://github.com/JoacoZun/nexoandes-iac-u1/pull/1),
abierta hacia `main`, head `e7f6025`, creada 24-10-2026 a las 12:26:12 UTC−03,
**cero reviews registradas**. No se aprobó ni modificó la PR.

- [Run push 40106088973](https://github.com/JoacoZun/nexoandes-iac-u1/actions/runs/40106088973): success, iniciado 12:14:48 UTC−03.
- [Run pull_request 40106962247](https://github.com/JoacoZun/nexoandes-iac-u1/actions/runs/40106962247): success, iniciado 12:26:17 UTC−03.

Cada run tiene dos jobs aprobados: cuatro checks en dos ejecuciones sobre el mismo
HEAD. La API confirma pasos exitosos de init readonly, formato, validate, tests
mock, lint, seguridad y verificaciones Python. No se descargaron logs autenticados
ni se atribuyen esos éxitos a los cambios nuevos sin commit. Fuentes crudas:
`github-readonly.json` y `github-detail.json` en `artifacts/predeploy/`.
La nueva revisión deberá pasar CI en su SHA final.

Lock AWS 6.42.0 conservado: comparación HTTPS con el [manifiesto oficial](https://releases.hashicorp.com/terraform-provider-aws/6.42.0/terraform-provider-aws_6.42.0_SHA256SUMS)
confirma las entradas zh para linux_amd64 y windows_amd64:

- Linux: `5bcc36226fa5d8a3c37e41ac8cfd2b1eb73e7ae96f8418f6776dcaa16a987198`.
- Windows: `7e534c454cdeafe9cc225bea53397883bb96c54da6ea3421fd53dbc9dfc1bb90`.

Esto comprueba correspondencia de hashes publicados; no es una nueva verificación
de firma. El init Linux readonly ya consta aprobado en CI del HEAD.

### Límites y cierre pendiente

CI sigue sin operaciones AWS; `deploy.yml.disabled` permanece inactivo. La guía
debe autorizar autenticación, backend/locking, protección del plan y aprobación
real antes de habilitar el candidato. Academy Learner Lab [193444] no está
confirmado como entorno autorizado. Faltan plantilla oficial, guía vigente y
comprobación de la ficha oficial; región, tipo EC2 e identidad siguen pendientes.
No hay evidencia de plan AWS, apply, HTTP, drift ni destrucción. No se generaron
ZIP/PDF finales. Ver `RUBRIC.md`, `EVIDENCE.md` y `OPERATIONS.md`.

## Reauditoría del verificador Python — histórico anterior a los commits

Ejecución local del 24-10-2026 en `feature/fase1-iac`, conservando los cambios
existentes y HEAD `7869232`. Esta sección conserva aquella reauditoría y sus
resultados históricos, anteriores a la preparación final. Logs de esa etapa en
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
