# Ejecución real v1 a v2: observación sin control del despliegue

Preparación realizada con outputs Terraform y perfil nexoandes-u2, solo lectura.
Manifiesto privado ignorado: runs/u2-v1-v2-20261117-01/config.initial.json.
preparation.json conserva snapshots y respuestas reales de ambos backends v1.
La captura de baseline NO se ha iniciado ni se ha iniciado ningún refresh.
La preparación puntual no reemplaza el baseline continuo.

El hash v1 se contrasta con la aplicación que responde. El hash esperado v2 se
calcula del portal_base.py y portal_release.py que instala la plantilla docente
intacta (SHA256 de base + byte NUL + release). No es evidencia de despliegue v2.
Se conserva el build real de origen para ambas releases porque el mismo código
docente contiene las dos versiones. La operación futura debe usar exactamente
ese build y artefacto, app_version=v2, enable_instance_refresh=true y la misma AMI
controlada. Si se decide otro build/artefacto, preparar otro manifiesto antes de
iniciar monitores; no editar un intento en marcha ni atribuirle evidencia anterior.

## Comandos Git Bash

Desde /c/Users/zunig/OneDrive/Desktop/nexoandes-iac-u1:

```bash
bash u2/observation/run-experiment.sh preflight u2/observation/runs/u2-v1-v2-20261117-01
```

Terminal A, dejar en ejecución:

```bash
bash u2/observation/run-experiment.sh http u2/observation/runs/u2-v1-v2-20261117-01
```

Terminal B, dejar en ejecución:

```bash
bash u2/observation/run-experiment.sh controller u2/observation/runs/u2-v1-v2-20261117-01
```

Terminal C, esperar al menos 70 s DESPUÉS de arrancar ambos:

```bash
sleep 70
bash u2/observation/run-experiment.sh baseline u2/observation/runs/u2-v1-v2-20261117-01
tail -n 2 u2/observation/runs/u2-v1-v2-20261117-01/http.jsonl
tail -n 1 u2/observation/runs/u2-v1-v2-20261117-01/controller.jsonl
```

El baseline requiere cobertura de 60 s, muestras recientes, cero fallos HTTP,
ambos backends y capacidad saludable. No autoriza el cambio ni lo ejecuta.
Mantener monitores en marcha; si se retrasa la operación, repetir el gate.
HTTP: cada 2 s, timeout 5 s y tres workers. Control: cada 20 s. Sin reintentos
ocultos. Se generan http.jsonl/csv y controller.jsonl/csv, sin sobrescritura.

## Integración de eventos

experiment.py controller usa únicamente las cuatro consultas allowlisted de
observe.py. Antes de armarse, rechaza refresh activo o capacidad insuficiente.
En la MISMA lectura DescribeInstanceRefreshes usada por la muestra, descubre
un único refresh con StartTime posterior al armado. Publica change_started
atómicamente con StartTime e InstanceRefreshId del proveedor, y fija ese ID
antes de evaluar la muestra: no hay watcher externo compitiendo por eventos.
Rechaza más de un refresh nuevo y preserva fallos en registros.

Después de persistir una muestra terminal Successful, exige LT numérica nueva,
retiro completo de IDs anteriores, capacidad saludable y respuestas v2 recientes
de TODOS los destinos con build/hash/función correctos. Solo entonces crea
config.final.json con LT observada y publica stabilized con UTC real y referencias
a controller_sample_seq y http_sample_seqs ya terminadas. No inventa t0 ni
estabilización al terminar apply. Nunca escribe eventos desde otra terminal.

Los monitores paran tras estabilización +120 s y cobertura de extremo. Si el
controlador falla o falta evidencia, no hay stabilized: al límite de 3600 s
fallan, conservando todos los registros. El análisis no aprueba por tiempos solos.
Las consultas AWS no son atómicas; un cambio durante una consulta puede producir
evidencia ambigua y rechazo conservador. No se reescriben muestras para ocultarlo.

Una vez terminados AMBOS procesos:

```bash
bash u2/observation/run-experiment.sh analyze u2/observation/runs/u2-v1-v2-20261117-01
```

Solo exit 0 y accepted=true acreditan el protocolo muestreado: intervalo
t0-60 hasta estabilización+120, huecos HTTP <=7 s y control <=30 s, sin fallos,
reemplazo y capacidad verificados. El éxito del monitor no equivale a aceptación.
analysis.json no se sobrescribe. No reiniciar logs ni borrar intentos fallidos.

## Pendiente antes del cambio

Gate baseline real y responsable autorizado para ejecutar un único cambio
Terraform/provider; no existe pipeline de despliegue U2 habilitado. Este runner
no hace plan/apply, no inicia refresh ni gestiona credenciales. El perfil debe
seguir vigente durante toda la ventana y el ALB permitir HTTP desde el ejecutor.
No publicar evidencia cruda sin revisión. El intento contiene referencias reales,
no credenciales; no leer ni copiar archivos de credenciales para ejecutarlo.
