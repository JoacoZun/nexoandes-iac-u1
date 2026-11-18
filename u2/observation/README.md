# Observación AWS U2: preparación local, no ejecución real

No se ejecutó HTTP real, AWS/Azure, refresh, rollback ni cambio de infraestructura.
El código solo observa/analiza; no incorpora comandos que inicien, cancelen o reviertan
operaciones. Los monitores requieren `--allow-network` y autorización posterior.
No se agregan credenciales ni defaults académicos: el ejemplo JSON tiene campos null
y es deliberadamente inválido hasta completarlo. X=8 sigue pendiente de ratificación.

## Herramientas

`observe.py http` observa únicamente GET `/api/check` del endpoint fijo del ALB:

- Planificación cada **2 s**, reloj monotónico, timeout duro **5 s** por proceso curl.
- Tres workers permiten peticiones solapadas cuando tardan más de 2 s, sin cambiar
  la cadencia a 5 s. No hay reintentos, redirects ni recuperación oculta de respuestas.
- curl usa `--disable` para ignorar .curlrc, no proxy, tamaño máximo de respuesta
  1 MiB y ningún argumento de autenticación. GET distinto de 200 sigue siendo fallo.
- Los slots atrasados/ocupados producen una fila `missed_schedule_no_retry`; no se
  envían ráfagas para rellenar el pasado. CSV/JSONL registran hora programada, inicio
  real UTC, duración, retraso, monotónico, HTTP, identidad, versión, build, instance ID,
  hash instalado, estado de metadata, comprobaciones y errores.

`observe.py controller` programa consultas cada **20 s** (límite evaluado <=30 s):

- Allowlist: STS GetCallerIdentity, ASG DescribeAutoScalingGroups,
  DescribeInstanceRefreshes y ELBv2 DescribeTargetHealth. Ninguna API de escritura.
- Cuenta/región/ASG/TG explícitos; comprueba cuenta esperada. Cuatro consultas
  secuenciales con timeout duro de 4 s cada una; AWS_MAX_ATTEMPTS=1, sin paginador.
  Si falla una consulta, se conserva como error; no se interpreta como recursos ausentes.
- Identifica un único refresh activo y exige el InstanceRefreshId fijado por el evento.
  Detecta controladores activos ajenos y otros refresh iniciados desde t0.
- Captura estado/razón/porcentaje/restantes, instances ASG con lifecycle/health/AZ/LT,
  destinos TG, capacidad saludable y referencias antiguas/nuevas/retiradas. La capacidad
  saludable es la intersección **InService + Healthy ASG + healthy Target Group**.
- Las cuatro consultas no son una transacción simultánea; se registra su duración.
  Sobrepasar cadencia/cobertura deja evidencia incompleta, nunca un éxito supuesto.

No registra stderr AWS ni respuestas completas que puedan incluir tokens. El JSONL
es canónico; CSV exporta campos de observación y neutraliza prefijos de fórmula.
Los archivos se abren en modo exclusivo y se vacían a disco tras cada registro.
No sobrescribe ni fusiona intentos. Las salidas reales deben ir en `runs/<run_id>/`
(ignorado); no publicar material crudo antes de revisión/saneamiento.

## Configuración, eventos y ventanas

Completar una copia de `run-config.example.json` con identidad ratificada, endpoint,
cuenta/región, ASG/TG, capacidad, builds y hashes de aplicación de v1/v2 y LT origen.
El hash de aplicación es `artifact_sha256` publicado por Portal; **no** el SHA del
bootstrap docente. Registrar aparte commit evaluado, plan/digest, aprobación, ejecución
del pipeline y referencias de imagen. No incluir secretos o planes binarios.

La LT destino puede ser `{ "id": null, "version": null }` SOLO para arrancar captura
antes del cambio. Terraform aún puede no haber asignado su versión numérica. Conservar
la configuración inicial y producir otro manifiesto final con la LT observada, mismo
run_id/endpoint/identidad/build/capacidad. El analizador final rechaza destino pendiente.
No se predice ni inventa la versión de LT. La captura no la utiliza para iniciar nada.

El pipeline futuro entrega un JSONL de eventos completo mediante actualización atómica:

1. `change_started`: run_id, timestamp_utc del inicio real de la operación y controller_id
   obtenido del proveedor. No usar la hora de un comando curl ni del fin de apply.
2. `stabilized`: mismo run_id/controller_id, timestamp_utc posterior a comprobaciones,
   controller_sample_seq del snapshot terminal y http_sample_seqs con respuestas
   correctas de **todos** los destinos activos, tomadas <=30 s antes de ese instante.

Las referencias deben apuntar a filas ya terminadas (finished_utc <= estabilización).
Un evento escrito a mano no prueba estabilización: el analizador contrasta estado,
LT, capacidad, destinos y respuestas. Duplicados, JSON incompleto o mezcla de runs
fallan; no se ignoran líneas rotas. Mantener relojes sincronizados y UTC explícita.

Los monitores arrancan **antes de t0−60 s** y continúan hasta al menos estabilización
**+120 s**, con muestra posterior que cubra el extremo. Un máximo de duración sin
ventana completa devuelve error. No reiniciar logs para borrar fallos.

`observe.py analyze` es offline. Delimita [t0−60, estabilización+120] dentro del registro
íntegro y exige:

- Cadencia programada HTTP 2 s/control 20 s, secuencias íntegras, extremos cubiertos,
  huecos HTTP <=7 s y control <=30 s. Detecta saltos UTC/monotónico >1 s.
- Cero fallos HTTP/funcionales dentro del intervalo. Antes: versión origen; transición:
  origen/destino; desde estabilización: solo destino. Identidad/build/hash/perfil y
  checks básicos/extendidos correctos, metadata válida, endpoint invariable.
- Correlación del backend HTTP con destinos saludables observados por el proveedor
  en snapshots cercanos (<=30 s); no equivale a una prueba continua entre consultas.
- Base saludable preservada, desired=min=base y max=base+margen, controlador fijado,
  estado final Successful (o recuperación RollbackSuccessful), LT numérica objetivo,
  destinos finales saludables y sin anteriores todavía drenando/activos.
- IDs nuevos disjuntos de los antiguos y respuesta funcional de cada backend final;
  también exige evidencia HTTP de los backends de baseline. Cambiar etiqueta o IP no basta.

`analysis.json` se crea sin sobrescribir y el proceso retorna 0 solo si accepted=true.
Falta de eventos o evidencia malformada aborta con error, no fabrica un reporte aprobado.
Errores anteriores/posteriores al intervalo se conservan y contabilizan aparte.
La aceptación solo se refiere al intervalo seleccionado, no oculta esos otros intentos.

Uso futuro (NO ejecutado aquí): los modos http y controller se ejecutan en procesos
separados, con config/events/run directory compartidos y `--allow-network`. Analizar
después con el manifiesto final. Para ver argumentos sin I/O: `python observe.py --help`.

## Gates propuestos: sin integración de despliegue habilitada

| Gate | Requisito y evidencia | Si falla |
|---|---|---|
| G0 Contexto | Ratificar X/curso, cuenta/endpoint, imagen, cuota y margen; conservar LT/build/artefacto v1 recuperables | No autorizar cambio |
| G1 Baseline | HTTP y control en marcha, >=60 s íntegros, función v1 y todos los destinos/capacidad base corroborados; ningún refresh activo | Conservar registros, corregir y empezar un intento nuevo |
| G2 Plan/autorización | SHA/código/variables/contexto y digest del plan revisados; un único responsable Terraform/provider; observadores sin permisos de escritura | No ejecutar controlador |
| G3 Cambio | Pipeline futuro inicia una sola operación; registrar t0/ID real y nueva LT; observadores solo consultan | Cualquier fallo se registra; decisión de detención/recuperación por responsable autorizado |
| G4 Estabilización | Controlador terminal esperado, LT objetivo, destinos saludables/base preservada y HTTP funcional de todos los activos | No marcar estabilizado ni aprobar por apply success |
| G5 Aceptación | +120 s observados y analizador accepted=true, revisar también registro íntegro y límites del muestreo | Evidencia incompleta/fallida; conservar intento y repetir protocolo completo |

Estos gates son diseño y comprobaciones de evidencia; no configuran un Environment
GitHub ni sustituyen aprobación humana. No hay job de despliegue ni credenciales.

## Rollback/recovery v2→v1: procedimiento no ejecutado

1. Conservar el intento v2 y sus fallos, ID de refresh, diagnóstico y recursos. Abrir
   una decisión autorizada con causa y artefacto/LT/imagen/build v1 recuperables.
2. Distinguir **rollback de un refresh activo** de **retorno tras uno terminado**.
   En el primero, evaluar requisitos reales de la API/provider; no asumir que admite
   rollback con esta integración. El código actual tiene auto_rollback=false y el
   provider no espera fin de Instance Refresh. No iniciar otro mientras haya uno activo.
3. Si se elige retorno planificado, esperar/reconciliar el controlador previo mediante
   mecanismo autorizado. Preparar código v1 con su build e imagen controlados, revisar
   nuevo plan/contexto y gate. No editar máquinas/state ni cambiar solo una etiqueta.
4. Usar otro run_id con operation_kind=recovery, from_version=v2, target_version=v1,
   LT origen real y destino numérico observado. La LT de retorno puede ser una nueva
   versión que reinstala el artefacto v1, y las EC2 pueden tener otros IDs/IP privadas.
5. Aplicar el mismo protocolo -60/+120, un único controlador y endpoint ALB estable.
   Registrar función v1, capacidad, IDs nuevos y resultado terminal real; conservar
   interrupción provocada como fallo, no presentarla como continuidad sin errores.
6. Alinear código/configuración con v1 finalmente elegida y revisar un plan posterior
   autorizado; no ejecutar plan en esta preparación. Si hay deriva, explicar/resolver
   con revisión, nunca editar state para ocultarla.

No se implementan comandos start/cancel/rollback-instance-refresh ni apply/destroy.
La integración futura deberá capturar el ID real iniciado por el provider y esperar
su estado final; este observador no compite por controlar el ASG.

## Evidencias previstas (no generadas como ejecución real)

| Familia | Artefactos futuros |
|---|---|
| E04 | Plan previo, gates/capacidad/detención/recuperación, commits/builds/imagen/LT y autorización |
| E05 | Run/refresh ID, JSONL del controlador, IDs/LT anteriores/nuevos, resultado terminal y retiro |
| E06 | http.jsonl/csv, controller.jsonl/csv, eventos, manifiestos inicial/final, análisis de cobertura/fallos/decisión |
| E07 | Run separado de recuperación, causa, mismo protocolo, versión/función restauradas y plan posterior coherente |
| E08 | Estado funcional final e inventario para limpieza independiente; limpieza no implementada aquí |

Registrar fuentes, UTC, CE, contexto, SHA y afirmación demostrada. Calcular hashes de
los archivos cerrados y conservar originales privados. El ZIP U1 no es un exportador
U2 validado de estos registros: preparar entrega saneada sin state/secretos/planes.

## Viabilidad de aislamiento del CI Linux

El workflow existente usa Ubuntu 24.04 y `sudo unshare --net`, habilita lo y ejecuta
validate/tests con rutas absolutas de Python/Terraform. Una network namespace separa
interfaces/rutas IPv4/IPv6; mantener lo permite el RPC local de los providers.
Es técnicamente compatible con mocks; init/pip requieren Internet **antes** de aislar.

No se ha probado un runner Linux/GitHub en esta sesión Windows. Comprobar sudo,
unshare/ip/setpriv, CONFIG_NET_NS/capacidades y acceso a binarios/paquetes; su disponibilidad
no se deduce de actionlint. `../scripts/ci_network_probe.py` está ahora integrado mediante
`run_offline_linux.sh` antes de cada comando aislado, en la misma namespace. Comprueba
interfaces/rutas locales, cambio de namespace respecto al host, lo activo y privilegios
reducidos; no hace conexiones externas ni modifica firewall. Los fallos impiden exec.

El workflow falla cerrado si no puede aislar; no sustituir por variables de entorno.
Solo la creación de namespace/lo usa sudo; después se baja al uid original, se quitan
capacidades/grupos, se activa NoNewPrivs y se limpia el entorno. Esto refuerza el bloqueo
de red, pero no es aislamiento completo de filesystem/procesos del host frente a código
hostil: ese modelo requiere un runner desechable dedicado. No borrar el bloqueo para
ejecutar monitores live: CI solo ejecuta funciones con I/O simulado.

Referencias: [AWS refreshes](https://docs.aws.amazon.com/cli/latest/reference/autoscaling/describe-instance-refreshes.html),
[ASG instances/capacidad](https://docs.aws.amazon.com/cli/latest/reference/autoscaling/describe-auto-scaling-groups.html),
[Target Health](https://docs.aws.amazon.com/cli/latest/reference/elbv2/describe-target-health.html),
[Linux network namespaces](https://man7.org/linux/man-pages/man7/network_namespaces.7.html),
[imagen runner Ubuntu 24.04](https://github.com/actions/runner-images/blob/main/images/ubuntu/Ubuntu2404-Readme.md).

## Dependencias y validación local

Captura futura: Python estándar >=3.10, curl y AWS CLI v2 en contexto autorizado;
sin paquetes pip para observar. Analizar/pruebas no necesita curl/AWS CLI instalados:
todo I/O es inyectado. Las regresiones se descubren con la suite U2 existente y no
ejecutan el bootstrap, sockets, AWS ni sleeps reales. Las fechas/IDs/builds de tests
son sintéticos y no constituyen evidencias de E05/E06/E07.

Preparación asistida por Codex para herramientas, pruebas sintéticas y runbook.

## Resultado de esta preparación

38 pruebas Python aprobadas (23 nuevas de observación y 15 existentes), con parser y
dependencias standalone de CI. Incluyen ciclo de actualización y retorno v2→v1 con
datos sintéticos, pérdida de muestras, fallo transitorio, reloj/cadencia, capacidad,
controladores competidores, identidad/build incorrectos, versiones/LT, cobertura de
todos los backends, opt-in de red, allowlist de solo lectura, archivos sin sobrescritura
y scheduler con reloj/executor simulados (sin esperar ni abrir conexiones).
Guards U2/AWS/Azure y actionlint del workflow existente: PASS. Hash docente intacto.
No se repitió Terraform: no se modificaron HCL/locks ni workflows en esta etapa.
No hay registros reales ni evidencias cloud generadas; solo pruebas temporales sintéticas.

Integración posterior de CI: **41 pruebas de regresión**, **26 de observación**.
Las dos nuevas de concurrencia usan reloj virtual y workers reales con un ejecutor
de timeout inyectado: inicios 0,2,4,6,8 s y timeout registrado a los 5 s; una pausa
virtual deja cuatro slots perdidos explícitos y hueco >7 s, sin reintentos para taparlo.
Otra prueba comprueba namespace/capacidades y negativas del preflight. El wrapper
tiene sintaxis Bash válida y rechaza Windows sin ejecutar comandos; el caso positivo
Linux solo podrá confirmarse en GitHub Actions. Sin cambios en los monitores live.
