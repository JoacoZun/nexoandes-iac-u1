# CI U2: controles sin despliegue

Workflow exclusivo `.github/workflows/u2-ci.yml`; no modifica ni llama workflows U1.
Push a cualquier rama y pull_request, filtrados por `u2/**` o el propio workflow.
No workflow_dispatch/deploy/environment, credenciales, OIDC, apply/destroy ni plan CLI.
Permiso único contents:read, checkout sin persistir token, acciones fijadas por SHA,
Ubuntu 24.04, timeout 15 min, concurrencia cancelable y matriz de tres roots.

Cada root ejecuta guard Python, fmt-check, init con backend=false/lockfile=readonly,
validate y seis runs Terraform. Terraform 1.16.6; locks existentes AWS 6.42.0 y AzureRM
4.65.0 preservados. `u2/` no requiere providers/lock; sus módulos son contratos puros.
No se usa el lock ni el backend de U1. No se publican state, planes o inventarios.

El guard común recorre módulos locales realmente referenciados (incluida composición
compartida), exige mocks del provider correcto y command=plan en cada test, verifica
hash docente y provider/versión/lock, y rechaza data sources, provisioners, imports,
providers alternativos/aliases/remappings, módulos externos y tests no auditados.
Los guards complementarios existentes de AWS/Python y Azure siguen ejecutándose.
Las dependencias Python están fijadas en requirements-ci.txt, separadas de Checkov/U1.

Init requiere Internet para distribuir providers/paquetes, no autenticación cloud.
Después, validate, guards, tests Python y tests Terraform pasan por
`scripts/run_offline_linux.sh`. Cada comando crea una namespace nueva, habilita lo,
quita grupos/capacidades/posibilidad de elevación y vuelve al uid del runner. Limpia
el entorno heredado y conserva solo HOME/PATH/librerías y controles locales necesarios.
ANTES de exec, dentro de ESA MISMA namespace y con esos privilegios reducidos,
`ci_network_probe.py` comprueba namespace distinta de la original, solo lo activo,
sin rutas externas IPv4/IPv6 ni default, NoNewPrivs=1 y capacidades en cero.
Loopback permite RPC entre Terraform y provider local. Si sudo/unshare/ip/setpriv o
preflight fallan, el comando no se ejecuta; no hay fallback con red ni `|| true`.
La suite `test_observation*.py` es explícita en la celda u2 y también forma parte de
la regresión completa. No usa --allow-network ni ejecuta bootstrap o infraestructura.

La ejecución local Windows usa Terraform portátil y guards/mock tests, pero no puede
replicar la network namespace Linux. No equivale a un run GitHub Actions. El workflow
solo podrá ejecutarse remotamente tras publicar los archivos por una acción autorizada
posterior; no se hizo commit/push/dispatch en esta preparación.

Limitaciones: los guards comprueban la configuración actual, no sustituyen una revisión
de código; las pruebas mock no demuestran permisos, cuota, compatibilidad real de imagen,
Portal ni continuidad. Al añadir roots/providers/tests, actualizar guard y regresiones
explícitamente. El workflow U1 existente sigue teniendo sus propios triggers y podría
ejecutarse también en PR; no se cambió su alcance para ocultarlo.

Para reproducir localmente, desde el repositorio con dependencias Python disponibles:

```powershell
./.tools/python/python.exe -B u2/scripts/check_ci_safety.py u2
./.tools/python/python.exe -B u2/scripts/check_ci_safety.py u2/aws
./.tools/python/python.exe -B u2/scripts/check_ci_safety.py u2/azure
./.tools/python/python.exe -B -m unittest discover -s u2/tests -p 'test_*.py' -v
./.tools/python/python.exe -B u2/azure/tests/check_offline.py
```

Después, en cada root, con binario Terraform 1.16.6: fmt -check -diff -recursive;
init -backend=false -input=false -lockfile=readonly; validate; test. Siempre detener
la secuencia si un control falla. No ejecutar terraform plan/apply/destroy ni scripts U1.

Preparación asistida por Codex para workflow, guards y validaciones locales.

## Resultados locales de esta preparación

| Root | Guard | fmt-check | init backend=false / lock readonly | validate | Terraform test |
|---|---|---|---|---|---|
| u2/ | PASS | PASS | PASS | PASS | 6 passed, 0 failed |
| u2/aws/ | PASS | PASS | PASS | PASS | 6 passed, 0 failed (mock) |
| u2/azure/ | PASS | PASS | PASS | PASS | 6 passed, 0 failed (mock) |

15 pruebas Python aprobadas con python-hcl2 8.1.4/PyYAML 6.0.3, las dependencias
standalone de CI preparadas en .tools/u2-ci-deps (ignorado, sin alterar Checkov).
Compatibilidad de parseo normalizada para labels, valores y metadata del parser 8;
los guards previos también funcionan con el fork local de Checkov.
Guard complementario Azure aprobado con dependencias de CI. Actionlint aprobado
sobre u2-ci.yml, sin shellcheck externo. Sin cambios en locks o workflows U1.

No se ejecutó GitHub Actions, Linux/unshare ni descarga de providers para Linux.
La instalación y los tests locales usan Windows AMD64; los checksums publicados
en los locks se conservan para la inicialización readonly del runner Linux.

## Observación: regresiones y revisión posterior

La suite descubre automáticamente `tests/test_observation.py`: sus funciones usan
I/O, relojes, procesos y evidencia sintéticos; no ejecuta los modos live de los monitores.
La preparación de observación aporta 23 casos nuevos, 38 pruebas Python en total.
Todos pasan con las dependencias standalone de CI. No se repitieron tests Terraform
porque no cambió HCL, providers ni locks en esa preparación.

La primera etapa solo preparó el preflight. En la integración posterior quedó conectado
a cada comando aislado del workflow, junto con las pruebas concurrentes de observación.
La comprobación real positiva de kernel/capacidades del runner sigue pendiente de CI.

## Integración de preflight y cadencia: resultado local

- Actionlint: PASS (sin shellcheck externo). Bash `-n` del wrapper: PASS.
- Ejecución del wrapper en Windows/Git Bash: rechazo esperado con exit 1 por no ser
  Linux; no intentó sudo/unshare ni ejecutó el comando solicitado. No se instaló Linux.
- Guards de los tres roots: PASS; regresión Python: **41/41** con dependencias de CI.
- Suite de observación explícita: **26/26**, incluidas dos pruebas concurrentes nuevas.
- Reloj virtual y tres workers: solicitudes en t=0,2,4,6,8 pese a timeouts de 5 s;
  cada uno conserva timeout_5s en JSONL y CSV. No hay red, curl real ni espera de 5 s.
- Pausa virtual de 10 s: cuatro slots perdidos registrados sin reintento, secuencias
  completas, hueco >7 s y cobertura rechazada. Los logs son temporales/sintéticos.
- Nuevas negativas de preflight: namespace sin cambiar/desconocida, lo down, interfaz
  o ruta externa/default, root, capacidades residuales o elevación habilitada => rechazo.

Pendiente exclusivo de GitHub Actions: confirmar sudo no interactivo, soporte real de
CONFIG_NET_NS/unshare/setpriv, acceso a binarios/paquetes tras bajar privilegios y RPC
de providers con lo. El preflight imprimirá evidencia del kernel en cada comando.
La inspección local Windows y actionlint no certifican esa ejecución. No se cambió
HCL, locks ni workflows U1; no se repitió Terraform para cambios solo de CI/Python.
