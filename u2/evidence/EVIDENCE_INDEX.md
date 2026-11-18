> Versión pública saneada: rutas privadas, IP pública e IDs EC2 ocultos; resultados técnicos conservados. Los originales externos y el borrador A01 no se publican.

# Índice de evidencias NexoAndes U2 — E01–E10

Inventario local preparado el 2026-11-17 (America/Santiago). No se consultaron
cuentas cloud ni GitHub para elaborar este índice. Las capturas existentes se
inspeccionaron visualmente; los originales no se editaron ni renombraron.
Actualización de consolidación 2026-11-18: 22 copias saneadas generadas en assets/
con resultados técnicos preservados y máscaras opacas; ver manifiestos.
Actualización 2026-11-18: se generó el diagrama A02 desde Mermaid, separado de
las capturas reales y de la imagen anterior A01, conservada como borrador.
Los nombres de archivo no certifican hora UTC: usar las horas visibles del contenido
cuando existan y los timestamps UTC de JSONL. Algunas respuestas corresponden al
2026-11-18 UTC, aunque la sesión local sea del día 17.

**Identidad:** X=8 ratificado por el usuario, student=a008 derivado, course=c50
(equivalencia asumida con sección 50). Región AWS observada: us-east-1.
**Commit local comprobado:** dc0f4a0a0f8435db2d164aa325b175ad86134437,
2026-11-17T22:45:36-03:00. El build del Portal es
`a494cd6e5cb96c4ec17b454ccc810e3b0360c76e-local`: no confundirlo con el commit
posterior de documentación dc0f4a0.

## Cómo leer este índice

- **REAL:** archivo/captura observado; demuestra solo lo visible o registrado.
- **INCIDENTE:** intento fallido y sus efectos; no se convierte en evidencia de éxito.
- **EXCEPCIÓN DOCENTE:** Azure solo código, autorizada en S6 según declaración del
  usuario; no equivale a despliegue y no se inventa respaldo escrito del docente.
- **LOCAL/MOCK:** código o prueba sintética; no es consulta al proveedor.
- **FALTANTE/PARCIAL:** no se localizó respaldo suficiente en el ámbito inventariado;
  no significa que el hecho sea falso ni obliga a recrear recursos para fotografiarlo.

E01–E10 usan el agrupamiento acordado para esta entrega. No renumeran los criterios
ni las familias originales de la evaluación: por ejemplo, los conjuntos E03–E05 de
este índice contribuyen a la familia docente E03; el incidente E06 se relaciona con
familias docentes E04–E06 sin acreditar reemplazo E05; E07 se limita a recuperación
de configuración. Azure y GitHub son conjuntos complementarios E09/E10.

## Consolidación para la ficha PDF — 2026-11-18

**Preparación lista para maquetar, con limitaciones declaradas.** Se conservan
los 22 originales; se generaron 22 copias saneadas en assets/, de las cuales 17
son principales y cinco de reserva. No se recrearon resultados ni se generó
un PDF en esta operación. No se bloqueará su construcción por logs históricos
no localizados: se documentan como evidencia parcial.

- [PDF_MANIFEST.json](PDF_MANIFEST.json): manifiesto compacto de E01–E10,
  afirmaciones permitidas, criterios, imágenes principales/reserva y faltantes.
- [ASSETS_PROVENANCE.json](ASSETS_PROVENANCE.json): procedencia, fechas,
  dimensiones, hashes originales/saneados y rectángulos de redacción de cada copia.
- [assets/README.md](assets/README.md): método y límites de saneamiento.
- **E01:** usar E01_arquitectura.svg definitivo y su hash A02; nunca A01 borrador.
- **E09:** documentación local/mocks y excepción S6; no hay imagen específica de
  validate/tests localizada y no se fabricó una. Puede maquetarse como texto
  respaldado por fuentes del commit y referencia a C22.

Saneamiento: máscaras negras opacas y eliminación de metadata PNG, sin generar
texto nuevo en las capturas ni modificar resultados. Revisión visual de las 22
copias y comparación píxel a píxel: fuera de las máscaras no hay diferencias.
Se preservan UTC visibles, HTTP 200/v1, salud, conteos, error 403/SCP, LT numéricas,
Destroy complete y checks CI; se ocultan datos personales y referencias sensibles.
La redacción de IDs limita su correlación pública: los hashes/procedencia conservan
la trazabilidad privada. Este índice público no distribuye rutas privadas ni IDs
reales; el constructor debe consumir únicamente el manifiesto compacto.

### Selección E02–E10

| Conjunto | Capturas para el cuerpo | Complemento/límite |
|---|---|---|
| E02 | C05 | Identidad real; backend documentado, no captura de locking |
| E03 | C01, C02 | Plan inicial y direcciones de state; apply completo no localizado |
| E04 | C07, C08, C09 | ASG/ALB/TG históricos; distinguir sesiones de IDs |
| E05 | C06, C18 | Función v1 y HTTP; C18 posterior a recuperación; C03 fallo inicial conservado |
| E06 | C11, C13, C15 | Baseline, plan y SCP; no actualización exitosa |
| E07 | C16, C17 | Recuperación de configuración; referencia C18 sin duplicarla |
| E08 | C19, C20, C21 | Plan, 20 bajas y consultas ASG/ALB/VPC; no limpieza exhaustiva |
| E09 | Sin captura específica | Documentación Azure offline y excepción S6; referencia C22 |
| E10 | C22 | CI dc0f4a0 y PR #3; no prueba merge/revisión |

Reservas: C03 (fallo inicial), C04 (salud de proceso), C10 (ASG redundante),
C12 (segundo baseline) y C14 (detalle de plan). Todas tienen copia saneada.

### Inventario de copias saneadas

SHA-256 de cada copia final; hashes originales y fechas completas en procedencia.
Las fechas explícitas se toman de la imagen cuando existen; filesystem/nombre de
archivo se registran separados y no certifican el momento real de una operación.

| ID | Copia local | Uso | Criterios | SHA-256 saneado |
|---|---|---|---|---|
| C01 | [assets/C01.png](assets/C01.png) | Principal | CE3 | `e5c9a3569bf0299328a40a6cf5d4f0e6cbf68719a503176dec238f335312f170` |
| C02 | [assets/C02.png](assets/C02.png) | Principal | CE3, CE8 | `35a6ec8627de751aecc77d3949308c4c1b5f5ec600161e4d701ad7f45771908c` |
| C03 | [assets/C03.png](assets/C03.png) | Reserva | CE3, CE6 | `71abf7b909c637f0389cf3d1d4deb276b0b0ad07a8230dd01474010a3b3385a8` |
| C04 | [assets/C04.png](assets/C04.png) | Reserva | CE3 | `f5251214377ab4f19095642f62ec75869dad2921fc9c87ca92cb9eccd87439f8` |
| C05 | [assets/C05.png](assets/C05.png) | Principal | CE3, CE8 | `69b0a685207f796d9f27557fee4032de4433dbde40f98acb640660a8c60930c5` |
| C06 | [assets/C06.png](assets/C06.png) | Principal | CE3 | `50cdef8b0b8ed468f7c187715ab1163b88549603eba8cd88e9dd46fc6f6d4939` |
| C07 | [assets/C07.png](assets/C07.png) | Principal | CE3, CE6 | `d93fdfa7b9acae0b57c98683c476471b1a4f026c4755d7a6c3d6981cc00a4bc8` |
| C08 | [assets/C08.png](assets/C08.png) | Principal | CE1, CE3 | `9508fceebb287b9fcb40a0632eb48e37de7979ea1f32cb5a19853ea2fd4c995c` |
| C09 | [assets/C09.png](assets/C09.png) | Principal | CE3, CE6 | `d6a733d28c721f5f613e4382e70fce9063531a1c5a4ccf57a39e7ecacc271267` |
| C10 | [assets/C10.png](assets/C10.png) | Reserva | CE3, CE6 | `8a3022330428c026e3ceb35ae38452956a8210c54f6400f84dcb0b8d20275a41` |
| C11 | [assets/C11.png](assets/C11.png) | Principal | CE6 | `47f7ed9efea5ef7c34e6344403f1a95a342d8d5a51002e6872973f8b09556900` |
| C12 | [assets/C12.png](assets/C12.png) | Reserva | CE6 | `caae0ac4ea067fc353953294971713da462ed3492f24b354a3cef7a5fc957c9e` |
| C13 | [assets/C13.png](assets/C13.png) | Principal | CE4, CE6 | `06b88b595f4231665b14be3b3ac527a5d8da7a07ce6c129839db2151cc830eb0` |
| C14 | [assets/C14.png](assets/C14.png) | Reserva | CE4, CE6 | `27cf5d23f39c57c63b33a3d3b50ae15f057e398288fe5fabd86dde93d5040659` |
| C15 | [assets/C15.png](assets/C15.png) | Principal | CE5, CE6, CE8 | `59c148c9ffa2d0bf07c184f8892fe631d995400ee044ec4b28373ad22712dd42` |
| C16 | [assets/C16.png](assets/C16.png) | Principal | CE7 | `92b5e7cad49ef2393b646048b050eb34f19c179edc1b18db37f1dd898b9050eb` |
| C17 | [assets/C17.png](assets/C17.png) | Principal | CE7 | `521c6e8056be6257fe9e23c7bf74be6b4297c14f9f13386371b7edb47462129b` |
| C18 | [assets/C18.png](assets/C18.png) | Principal | CE3, CE7 | `c57485f66e56ca0ad1e4855bf6804a482940c2055098667e455872e1432cdb44` |
| C19 | [assets/C19.png](assets/C19.png) | Principal | CE8 | `6063ef1566076b1e3eebcb5ff5c14fadbc3218141d2d9b9d23e6e53e88d6cc9b` |
| C20 | [assets/C20.png](assets/C20.png) | Principal | CE8 | `b60a1a434baddb169b12c7e6b50cb1ce895f87686f1dab02f10843999d8d2ccb` |
| C21 | [assets/C21.png](assets/C21.png) | Principal | CE8 | `6f21d08ac80ebbf0b429b747999f7df5a714f7dfee852f2b7e7cec632860f1c6` |
| C22 | [assets/C22.png](assets/C22.png) | Principal | CE8 | `2919ec7af7e8c220522ff79bb5f3ae994ade2ec5090fc878c230c2341e149ac7` |

Faltantes que se DECLARAN sin bloquear la ficha: log completo del apply inicial,
apply de recuperación y plan posterior; limpieza por categorías adicionales y state
vacío; captura terminal específica Azure y referencia escrita S6; URLs/IDs completos
de runs CI y revisión del PR. No rellenarlos con resultados nuevos o ficticios.
El reemplazo v2 y rollback funcional no son capturas pendientes que deban inventarse:
no están acreditados, y el relato debe decirlo expresamente.

## E01 — Arquitectura

**Estado: A02 MERMAID generado desde Terraform y renderizado localmente; A01 conservado como BORRADOR.**

### A02 — Diagrama canónico generado desde Terraform (2026-11-18)

Fuente editable y exportaciones realmente generadas, dentro del repositorio:

| Archivo | Ruta | Bytes | SHA-256 |
|---|---|---:|---|
| MMD | [E01_arquitectura.mmd](E01_arquitectura.mmd) | 6823 | `3be774bdac59791f028f33f2f145b6fa54cd5f4daf77ab82f80011b37094c926` |
| SVG | [E01_arquitectura.svg](E01_arquitectura.svg) | 78686 | `97992071d87663a99317da2264379f1e22be7938c1484e693505585c9b2ee038` |
| PNG | [E01_arquitectura.png](E01_arquitectura.png) | 430291 | `0d20b85bc58f4baaa49a07f161a6ea8be305c00cf919c1179653cbdf7bdbb59b` |

A02 se construyó leyendo exclusivamente recursos/relaciones Terraform de
`../aws/modules/infrastructure/{network,security,service,compute}.tf`,
`../azure/modules/infrastructure/{network,compute}.tf`, contratos
`../modules/portal_aws/main.tf` y `../modules/portal_azure/main.tf`, más identidad
local y parámetros AWS. No se copiaron las relaciones de A01 ni de las láminas docentes.
Los estados históricos y la nota INC-U2-001 se referencian a E03–E08; el dibujo
no crea evidencia adicional ni certifica existencia actual de recursos.

Contiene ALB dentro de VPC, asociación a ambas subredes, Route Table/asociaciones
con ruta 0.0.0.0/0 a IGW, LT/ASG gestionando EC2 dinámicas y vínculo ASG/TG.
Azure muestra RG con VNet/subnet, Public IP, NIC, NSG y VM; asociación NSG a NIC,
NIC a subnet/Public IP y VM a NIC, sin asociación NSG/subnet ficticia.
Las EC2 dentro de A/B son posiciones ilustrativas de instancias dinámicas: el
código no garantiza una instancia fija por AZ. Flechas finas con punta = HTTP;
líneas sin punta = referencias/asociaciones; gruesas = gestión; punteadas = notas.

Leyendas explícitas: **AWS desplegado históricamente y posteriormente eliminado**;
**Azure solo código, no desplegado**, excepción S6 informada; reemplazo bloqueado
por SCP y /health no demuestra continuidad. No hay costos, IP asignadas, IDs,
conexión entre nubes, evidencias v2 o rollback funcional inventados.

Renderizado offline con Mermaid incluido en @oai/artifact-tool, Playwright y
Chromium headless ya instalados; no se instaló ningún paquete. Se bloquearon las
solicitudes externas del navegador y se sirvieron únicamente módulos locales en
memoria. Fue necesario seleccionar el Chromium local existente por un desajuste
con la versión esperada por Playwright. No se modificaron dependencias instaladas.
Mermaid.parse y render: PASS; PNG 4461x2694 píxeles, SVG inspeccionado mediante
su exportación PNG. SVG permite zoom para las etiquetas técnicas y asociaciones.
No se ejecutaron Terraform ni consultas cloud para producir este diagrama.

Datos no verificables aquí: ubicación/imagen/tamaño/destino reales Azure, IP
actual del cliente y direcciones asignadas, distribución futura del ASG o estado
cloud actual. Por ello no se representan valores inventados. El máximo de 3
es configuración, no una garantía universal ante cualquier evento.

### A01 — Imagen anterior del usuario, conservada como BORRADOR

Archivo original existente:
Arquitectura multi-cloud AWS y Azure validada.png (fuente externa no distribuida).
No está guardado como `u2/evidence/E01_arquitectura.png`; el usuario identificó
este original como el diagrama solicitado. Se revisó el contenido de la imagen
adjunta; no se modificó, copió ni renombró el archivo.

SHA-256: `a76f0ac203faf99c75024e82a592b606f41b8c6a4e707190fb6c6d1063d3c554`.
Tipo: ilustración de arquitectura elaborada para la entrega, **no captura del
proveedor ni prueba independiente de ejecución**. El hash identifica este original
sin corregir; si se edita la imagen, debe recalcularse y conservarse la trazabilidad.

La identidad X=8/a008/c50, los CIDR AWS y Azure, las AZ, t3.micro, Portal v1,
capacidad configurada 2/2/3, IMDSv2 y EBS gp3 cifrado concuerdan con el código.
El CIDR [CIDR_PUBLICO_OCULTO] coincide con deployment.tfvars y capturas históricas:
no se verificó que siga siendo la IP pública actual del equipo.

**Distinción de estado:** AWS fue desplegado y verificado en la sesión histórica,
y posteriormente eliminado según C19–C21, con los límites de E08. Azure está
implementado/validado solo como código por excepción docente S6 informada por el
usuario; **Azure NO fue desplegado**. El título del archivo no acredita validación
cloud de Azure. No hay prueba de reemplazo v2 ni rollback funcional v2->v1.

### Observaciones históricas del borrador A01 (no del nuevo A02)

1. **ALB dentro de la VPC y asociado a ambas subredes.** La imagen deja su caja
   fuera del contorno de VPC. Terraform lo crea con subnets de esa VPC. Mantener
   cliente y resolución DNS fuera, pero representar el ALB dentro de VPC con
   asociación a ambas subredes/AZ; DNS es resolución de nombre, no un recurso en
   serie que transporte el HTTP.
2. **ASG distribuido entre subredes, no propietario de ellas.** La caja ASG contiene
   gráficamente las subredes; invertir la contención: subredes pertenecen a VPC,
   instancias pertenecen a sus subredes y son gestionadas por ASG. Vincular LT al
   ASG para aprovisionamiento, distinto de las flechas de tráfico TG->EC2.
3. **Route Table asociada a las subredes A/B.** La flecha junto al ASG resulta
   ambigua. Dibujar asociaciones a cada subnet y anotar ruta 0.0.0.0/0 -> IGW;
   la ruta local es la de VPC. No representar Route Table como filtro de tráfico.
4. **NIC Azure en RG y asociada a subnet.** La NIC está dibujada fuera del RG/VNet
   y su flecha entra a VNet. La NIC es un recurso del RG; su ip_configuration
   referencia subnet y Public IP. Representar esas asociaciones y VM->NIC. La
   Public IP también es recurso del RG, no una VM/recurso ajeno a ese contexto.
5. **NSG asociado a NIC.** El escudo está dentro de subnet junto a VM sin relación
   explícita. El código utiliza network_interface_security_group_association,
   no asociación de NSG a subnet. Indicar HTTP desde CIDR autorizados, deny del
   resto de entrada y ausencia de SSH abierto; no sugerir egreso NSG limitado a
   80/443, pues Azure conserva sus reglas outbound predeterminadas.
6. **Seguridad y direcciones de bootstrap.** La leyenda EC2 debe decir claramente
   “TCP/80 solo desde SG del ALB”. Añadir IPv4 pública EC2 para salida por IGW
   según LT, aunque el SG impide HTTP directo; map_public_ip_on_launch=false en
   subnet no elimina la solicitud explícita de IPv4 de la LT. Las IP privadas
   Azure son dinámicas y la Public IP estática la asignaría Azure: sin números
   inventados. El diagrama no inventa esos números, pero conviene explicitarlo.
7. **Estado histórico visible desde el encabezado AWS.** Cambiar “Desplegado y
   validado” por “Desplegado y validado históricamente; posteriormente eliminado”.
   Mantener nota destroy complete, limitada a los recursos gestionados y consultas
   C20/C21: no certificar ausencia global de todo recurso ni borrado del bucket U1/U2.
8. **Azure: costos/suscripción no prueban despliegue.** El recuadro Azure for
   Students / suscripción visible / USD 0.00 es contexto de capturas de suscripción,
   no costo del Portal Azure U2 ni prueba de cuota/crédito/gratuidad. Retirarlo del
   flujo técnico o etiquetarlo como contexto histórico separado. Mantener explícita
   excepción S6 y validación local/CI, no validación cloud.
9. **No sobredimensionar la verificación.** /health=200 solo acredita proceso;
   /api/check verifica función/metadata de la respuesta observada, no disponibilidad
   continua. CI OK y mocks OK no prueban AMI/imagen Azure, permisos o ejecución real.
   La nota SCP es coherente: no cambiarla a “actualización exitosa”.

### Omisiones para completar la evidencia E01

Añadir una leyenda de flechas: tráfico, asociaciones de red y gestión Terraform;
marcar Azure como arquitectura propuesta de código. Referenciar módulos/providers
AWS/Azure y state/contextos separados (sin secretos). El build puede abreviarse en
la imagen si se remite a E02/E05 y al manifiesto con el valor completo. No dibujar
conexión, replicación ni failover AWS<->Azure; el original no los representa.

### Contrato de referencia comprobado

| Elemento | Contenido respaldado por el código y evidencia histórica | Afirmación que no debe darse por comprobada |
|---|---|---|
| Identidad | X=8, a008 derivado y c50 según configuración local; equivalencia sección 50 asumida | Identidad de ejemplo X=7/a007/c01 como si fuera la del alumno |
| AWS red | VPC 10.8.0.0/16; subredes 10.8.10.0/24 en us-east-1a y 10.8.20.0/24 en us-east-1b; ruta 0.0.0.0/0 a IGW | Red U1 172.16.8.0/24 como red AWS U2; NAT Gateway no implementado |
| AWS tráfico | Cliente autorizado -> ALB público HTTP:80 -> TG tipo instance HTTP:80 -> EC2; health check /health | HTTPS/TLS configurado o acceso HTTP directo permitido a EC2; /api/check como health check del TG |
| AWS seguridad | SG del ALB admite CIDR configurados; SG EC2 recibe TCP/80 solo del SG ALB; egreso EC2 TCP/80 y 443 | HTTP abierto globalmente por defecto, SSH abierto o salida sin restricciones de puerto |
| AWS capacidad | ASG mínimo/deseado 2, máximo configurado 3; LT con IMDSv2 y disco gp3 cifrado de 8 GiB | Tres instancias permanentes, autoescalamiento dinámico implementado o máximo absoluto garantizado en toda circunstancia |
| AWS direcciones | Endpoint es DNS del ALB; LT solicita IPv4 pública para bootstrap, sin IP fija declarada | IP del ALB/EC2 inventada o IP histórica presentada como vigente |
| AWS estado | Despliegue histórico y eliminación posterior respaldados parcialmente por C01–C21 | Infraestructura AWS actualmente operativa; reemplazo v2 exitoso o rollback funcional v2->v1 |
| Azure red | VNet 172.20.8.0/24 y subnet 172.20.8.0/26 en código | CIDR docente X=7 o direcciones reales de Azure no observadas |
| Azure recursos | RG, VNet/subnet, NSG asociado a NIC, Public IP Standard estática, VM Linux y disco administrado | ALB/ASG Azure, VM Windows u otros recursos no declarados |
| Azure tráfico | Cliente autorizado -> Public IP de NIC -> VM HTTP:80; IP privada dinámica; salida explícita por Public IP | IP pública/privada concreta, ubicación, tamaño o imagen de prueba como parámetros Azure reales; NSG con egreso limitado solo a HTTP/HTTPS |
| Azure Portal | Siempre v1, custom_data base64; sin contraseña ni SSH abierto | Azure desplegado, respuesta HTTP/metadata real, actualización v2 o limpieza Azure ejecutada |
| Relación entre nubes | Contextos y state separados; composición común local, no conexión de red | Peering, replicación, failover, balanceo o tráfico AWS<->Azure |


Fuentes: `../aws/modules/infrastructure/{network,security,service,compute}.tf`,
`../aws/deployment.tfvars`, `../modules/portal_azure/main.tf`,
`../azure/main.tf`, `../azure/modules/infrastructure/{network,compute}.tf`
y capturas históricas C01–C22. La lámina docente D01 es otra imagen y conserva
su clasificación como referencia, no evidencia propia.

**Entrega:** usar A02 como fuente/exportación; A01 permanece borrador histórico
sin alteraciones. No se requiere reconstruir infraestructura para documentar la arquitectura.
Referencia: CE1–CE2 / familia docente E01.

## E02 — Identidad y backend

**Estado: REAL parcial + configuración LOCAL.**

C05 y C18 muestran X=8/a008/c50 y build en Portal real. `../IDENTITY.md` y
`../aws/BACKEND.md` describen origen de identidad y separación. Archivos locales
ignorados existentes: `../identity.tfvars` y `../aws/backend.hcl`; no se publican
credenciales ni state. Destino U2 documentado:
`nexoandes-tfstate-est8-1793333880`, us-east-1,
`u2/c50/a008/aws/terraform.tfstate`, encrypt=true, use_lockfile=true.
Debe mantenerse distinto de `fase1/terraform.tfstate`; compartir bucket no prueba
segregación IAM. Azure conserva backend parcial independiente y no inicializado aquí.

**Falta:** evidencia saneada del destino backend realmente utilizado en la ejecución,
locking y correspondencia con identidad, sin adjuntar `.terraform/terraform.tfstate`
ni state/planes. No se verificó de nuevo el bucket ni su política.
Referencia: CE3/CE8 / familia docente E02.

## E03 — Plan y despliegue AWS

**Estado: REAL parcial.** C01 muestra el plan inicial de 20 recursos; C02 muestra
20 direcciones del state AWS U2. C04–C09 respaldan recursos y Portal operativos
posteriormente. No se afirma que exista un pipeline U2 de despliegue habilitado:
los comandos capturados son locales; el workflow U2 registrado es offline.

**Falta:** captura/log completo del apply inicial y outputs saneados, referencia
inequívoca de ejecución/revisión/autorización y plan posterior de coherencia.
La existencia de recursos no acredita por sí sola despliegue mediante pipeline.
El plan v2 existente pertenece a E06, no al despliegue inicial.
Referencia: CE3/CE8 / familia docente E03.

## E04 — ASG y Target Group

**Estado: REAL.** C07 muestra ASG con mínimo/deseado 2 y máximo 3; C08 ALB HTTP
activo; C09 dos destinos healthy; C10 dos instancias Healthy/InService en dos AZ.
`preparation.json` y controller.jsonl/csv conservan snapshots posteriores del run
`u2-v1-v2-20261117-01`.

**Límite importante:** C07/C09 muestran IDs de una sesión temprana distintos de los
registrados en el baseline nocturno. No presentarlos como las mismas máquinas.
En el run nocturno los originales registrados son [ID_EC2_OCULTO] e
[ID_EC2_OCULTO]; la captura C17 no imprime sus IDs y solo muestra LT de cada instancia.
**Falta:** correlacionar explícitamente los cambios de sesión/IDs y sus tiempos;
no deducir reemplazo v1→v2 de esa diferencia histórica.
Referencia: CE3/CE6 / familias docentes E03/E06.

## E05 — Portal v1 y HTTP

**Estado: REAL, con fallo histórico conservado.** C03 registra timeout inicial;
C04 salud de proceso; C05/C06 Portal y función v1; C18 HTTP 200 y comprobación
funcional después de recuperar configuración. El JSONL del run contiene 1.800
muestras HTTP, todas v1, sin errores en el campo errors, entre
2026-11-17T23:26:07.084+00:00 y 2026-11-18T00:26:05.071+00:00.
Esto no acredita disponibilidad fuera del intervalo ni durante cada instante.

Build observado: `a494cd6e5cb96c4ec17b454ccc810e3b0360c76e-local`.
Hash aplicación v1: `82f7e3a976f7ec7b46f739244e44e47b59a73aa840e0269870d3b0f42e1fd7fa`.
El hash esperado local v2 es
`67bed5e66dc15cdc1b6d69a6963e44f011220a3d9f4fd1c24a9887c676f7b017`:
no es prueba de una respuesta v2 real.
**Falta:** integrar extracto saneado de HTTP con secuencias/IDs y UTC en ficha;
no ocultar C03 ni inferir continuidad de una sola captura.
Referencia: CE3/CE6 / familias docentes E03/E06.

## E06 — Experimento v1→v2 bloqueado por SCP

**Estado: INCIDENTE REAL INC-U2-001; NO reemplazo exitoso.**

C11/C12 prueban gates BASELINE READY; C13/C14, plan y revisión de LT/ASG.
C15 registra modificación de LT y denegación HTTP 403 de
`autoscaling:StartInstanceRefresh`, con explicit deny en una SCP del Learner Lab.
El apply pudo dejar cambios parciales de configuración; no fue una transacción revertida.
No se afirma que se iniciara un refresh ni que EC2 fueran reemplazadas por v2.

El run contiene config.initial.json, preparation.json, http/controller JSONL y CSV,
v2.tfplan y v2-plan.sha256. El plan binario es privado y está EXCLUIDO de la entrega.
No existen events.jsonl, config.final.json ni analysis.json en el run inventariado:
no se fabrican change_started/stabilized para una API denegada.
Los monitores terminaron por `max_duration_without_complete_window`, no aceptación.
Controller: 180 muestras, tres errores TimeoutExpired, LT de instancias observada=1.

**Falta:** incorporar a bitácora la hora/operación exacta del fallo y decisión de
recuperación, respaldadas por C15; respuesta docente sobre alcance afectado si existe.
No suplir la ausencia de reemplazo con capturas sintéticas o nuevos intentos no autorizados.
Referencia: CE2/CE4/CE5/CE6/CE8; familias docentes E04–E06, con CE5 NO acreditado.

## E07 — Recuperación de configuración v1

**Estado: REAL parcial; NO rollback funcional v2→v1.**

C16 muestra el plan v1/refresh=false. C17 muestra ASG apuntando a LT v3, deseado=2,
y dos instancias originales que siguen con LT v1, Healthy/InService. C18 acredita
respuesta v1 funcional posterior. La recuperación informada restablece la configuración
para futuras instancias; no significa que las originales pasaran por v2.

**Falta:** log/captura final del apply de recuperación, confirmación saneada del
contenido v1 de LT v3 y plan posterior sin cambios no intencionados. No asignar
cumplimiento pleno a CE7 con un rollback funcional que no ocurrió.
Referencia: CE7/CE8 / familia docente E07, limitada a la acción demostrada.

## E08 — Limpieza AWS

**Estado: REAL con cobertura parcial de comprobación independiente.**

C19: plan de 20 bajas. C20: Terraform informa 20 recursos destruidos. C21:
consultas posteriores devuelven ASG U2=0, ALB U2=[] y VPC U2=0.
Son capturas históricas existentes, no operaciones ejecutadas al crear este índice.
No se afirma ausencia global de recursos ni borrado del bucket compartido/state U1.

**Falta:** state list vacío saneado y comprobación independiente de EC2/EBS,
Launch Template, Target Group y demás categorías requeridas, si se dispone de registros.
No hacer nuevas consultas cloud por este índice ni borrar state/evidencias para completar una captura.
Referencia: CE8 / familia docente E08.

## E09 — Azure validado solo como código

**Estado: LOCAL/MOCK + EXCEPCIÓN DOCENTE. Azure NO fue desplegado.**

`../azure/EVALUATION.md` registra autorización de clase S6 informada por el usuario,
recursos, identidad, Portal v1, seguridad y validación local: fmt/validate, seis tests
Terraform mock, guards, regresión Python y actionlint. Código/lock/tests existen;
no se repitieron esas pruebas para confeccionar el índice.

**Falta:** captura/log saneado de las seis pruebas/validate y referencia S6 disponible
para trazabilidad, sin inventar acta ni mensaje. Las capturas del portal Azure con
suscripciones/costos NO acreditan VM, Portal U2 o excepción; no se incorporan como
prueba de despliegue. No se solicitan capturas de un despliegue eximido.
Referencia: CE1–CE4/CE8 según alcance docente; familias E01/E02/E03/E08 con excepción.

## E10 — GitHub/CI, commit dc0f4a0 y PR #3

**Estado: Git LOCAL comprobado + captura REAL de GitHub.**

Commit: [dc0f4a0](https://github.com/JoacoZun/nexoandes-iac-u1/commit/dc0f4a0a0f8435db2d164aa325b175ad86134437).
PR: [#3](https://github.com/JoacoZun/nexoandes-iac-u1/pull/3).
C22 muestra U2 offline Terraform controls #4 verde para dc0f4a0 y #5 verde para
PR #3; muestra además control U1 #17 verde. No se ejecutó ni modificó U1 aquí.
La captura respalda existencia de checks, no merge, aprobación humana o contenido
individual de cada job. El índice actual se crea después de dc0f4a0: ese commit
no incluye este archivo todavía.

**Falta:** URL/ID inequívoco de cada ejecución, detalle matrix Azure y pruebas,
head SHA del PR y estado/revisión/merge si corresponde. No se consultó GitHub en vivo
ni se inventan URLs de runs. El usuario decidirá integración/publicación posterior.
Referencia: CE8 transversal.

## Inventario de capturas reales inspeccionadas

Los originales externos no se distribuyen. Los enlaces C01–C22 apuntan a copias
saneadas en assets/. La columna SHA-256 de esta tabla identifica los originales
externos, NO los assets enlazados: consultar ASSETS_PROVENANCE.json para hashes
de ambas versiones y fechas. A01 permanece externo como borrador excluido.
Los hashes no certifican autoría ni veracidad independiente del servicio.

| ID | Conjunto | Archivo existente | Contenido visible y límite | SHA-256 |
|---|---|---|---|---|
| C01 | E03 | [Captura de pantalla 2026-11-17 135201.png](assets/C01.png) | Plan inicial AWS: 20 altas, 0 cambios, 0 bajas; no prueba apply completo. | `0a848c6954fcc998f623591320aaa298c8e247c10130236e06a1cd262a1ec332` |
| C02 | E03 | [Captura de pantalla 2026-11-17 135945.png](assets/C02.png) | Listado de 20 direcciones Terraform del root AWS U2; no publicar state. | `faceae591d008ff008274bf5cad42c12e2364315ef92c117be8a5d9352b2f0b3` |
| C03 | E05 | [Captura de pantalla 2026-11-17 140231.png](assets/C03.png) | Timeout del navegador al ALB; conservar como fallo inicial, no como éxito. | `54204b96070bc92e792b5e20fc8bc8388af8ca4cd425f88d8166766157726444` |
| C04 | E05 | [Captura de pantalla 2026-11-17 140318.png](assets/C04.png) | JSON de salud de proceso v1; no equivale a comprobación funcional completa. | `67602ce24ddcc9a654ae2f837bf86206f38544d7f3efed3621356ad966b05901` |
| C05 | E02/E05 | [Captura de pantalla 2026-11-17 140436.png](assets/C05.png) | Portal v1: X=8/a008/c50, build e identidad de un backend; sesión temprana. | `14a3823abaa7bafc3440f6e47205b59e4bad531a0fb3a5adfbd51a9298c1a2c1` |
| C06 | E05 | [Captura de pantalla 2026-11-17 140450.png](assets/C06.png) | Comprobación funcional básica y UTC de respuesta/metadata; sesión temprana. | `8e0ff1fae44e6ababdff77836613815fb40f5f26faa0728839d6c3db6e8fb264` |
| C07 | E04 | [Captura de pantalla 2026-11-17 140718.png](assets/C07.png) | ASG: deseado/min 2, máximo 3, dos InService/Healthy; IDs de sesión temprana. | `f77ea8fa36d574f0a2c4938b3ed0b119be0b1aea51082a1bf0545687b1d8d332` |
| C08 | E04 | [Captura de pantalla 2026-11-17 141133.png](assets/C08.png) | ALB activo, listener HTTP:80 y subredes/AZ. | `61768ea7f4cb615e69c5ffb25604bb5cdbaa9502717987e3acd462f6e65cfb05` |
| C09 | E04 | [Captura de pantalla 2026-11-17 141152.png](assets/C09.png) | Target Group: dos destinos Healthy; IDs de sesión temprana. | `78c70249473348ae786f36c1590609fdca82357dda4bdffc3b2e02aa05d9a502` |
| C10 | E04 | [Captura de pantalla 2026-11-17 201512.png](assets/C10.png) | Consulta ASG: dos Healthy/InService en us-east-1a y us-east-1b. | `924947d61ca0df4c9530b3e1f4d988780e610275eb6e3c81354ce01a06361b4c` |
| C11 | E06 | [Captura de pantalla 2026-11-17 202900.png](assets/C11.png) | BASELINE READY a 2026-11-17T23:27:52.208+00:00; no prueba actualización. | `3d0b562a31f5fbd0bbfeaebcb63b3aa2b2e5e57867edc518044b147ae2dd0485` |
| C12 | E06 | [Captura de pantalla 2026-11-17 203628.png](assets/C12.png) | Segundo gate baseline a 2026-11-17T23:36:09.160+00:00 y parámetros del experimento. | `358fc44d5676c4048e6a0f12fccd7bd4c2b36f6d3bb0fd5d19e268f4eb335067` |
| C13 | E06 | [Captura de pantalla 2026-11-17 203707.png](assets/C13.png) | Plan v2: 0 altas, 2 cambios, 0 bajas; plan guardado, no reemplazo realizado. | `ab471fa7560a2a9dafb8626d09badd03c1a7945c4941d5a9ea7ef607cc8666e7` |
| C14 | E06 | [Captura de pantalla 2026-11-17 203924.png](assets/C14.png) | Inspección del plan: LT/ASG y preferencias refresh; no prueba ejecución exitosa. | `181aba7e1c82ba9b531f3881f81340e33bc2e6dd50272ede7b3cf3518afea414` |
| C15 | E06 | [Captura de pantalla 2026-11-17 204619.png](assets/C15.png) | INC-U2-001: LT modificada y StartInstanceRefresh HTTP 403, explicit deny SCP. | `13a853258ccc47eaf2cb09179e26730a9471d3f3581e9be6de3d713c779f4ae7` |
| C16 | E07 | [Captura de pantalla 2026-11-17 211915.png](assets/C16.png) | Plan de recuperación de configuración v1/refresh=false: 0 altas, 2 cambios, 0 bajas. | `d37bc07e6cc494cb3199c153667c4118d6c5a8a2d3e2cc5c1bf7d9560f701ad2` |
| C17 | E07 | [Captura de pantalla 2026-11-17 214951.png](assets/C17.png) | ASG apunta a LT v3; deseado 2 y dos instancias LT v1 Healthy/InService. No prueba reemplazo. | `af7ece6467648ac1fc12662a3febd0d441ce86f4038917195c9b0a3c6d495b8d` |
| C18 | E05/E07 | [Captura de pantalla 2026-11-17 222935.png](assets/C18.png) | GET /api/check: HTTP 200, v1, passed=true, a008/c50, hash/build; UTC HTTP 2026-11-18T01:29:27Z. | `b4462c79b19f9ab8a6dcaf4c8e51cd6770286c2dde596c21bb7372a22cdeb861` |
| C19 | E08 | [Captura de pantalla 2026-11-17 223147.png](assets/C19.png) | Plan de limpieza: 0 altas, 0 cambios y 20 bajas; intención, no limpieza por sí sola. | `53986b3eaf4f92191c29404a740f1ae91a893013ddde6ab5d7540e71664511a7` |
| C20 | E08 | [Captura de pantalla 2026-11-17 223629.png](assets/C20.png) | Salida Destroy complete! Resources: 20 destroyed.; resultado Terraform fotografiado. | `ae129dba849f6cc7043617503fa822303b8533eeb3ecb36193f38350642e6785` |
| C21 | E08 | [Captura de pantalla 2026-11-17 223734.png](assets/C21.png) | Consultas posteriores: ASG U2=0, ALB U2=[], VPC U2=0; cobertura limitada a esas consultas. | `1b6f5a9fae6e0f680ffac3dc45d89b3e786307e2d0de7af360bc23dea3c9fd7a` |
| C22 | E10 | [Captura de pantalla 2026-11-17 224826.png](assets/C22.png) | GitHub Actions: U2 controls #4 para dc0f4a0 y #5 para PR #3 verdes; también control U1 #17. No prueba merge. | `167c28e0c57f6be2a84bbb15cd638ad5bac4f3ec0e3913d0251d3b989bcf352f` |

## Material docente, separado de evidencia de ejecución

| ID | Ruta existente | Uso permitido en el índice |
|---|---|---|
| D01 | NexoAndes_U2_01_Arquitectura_Direccionamiento.png (fuente externa no distribuida) | Referencia docente de arquitectura, no diagrama propio ni despliegue real |
| D02 | NexoAndes_U2_02_Resultados_Verificacion.png (fuente externa no distribuida) | Protocolo y ejemplos docentes, no resultados del alumno |
| D03 | Evaluacion Sumativa U2.pdf (fuente externa no distribuida) | Requisitos originales; contrastar con excepción S6 documentada |
| D04 | Rubrica Evaluacion U2.pdf (fuente externa no distribuida) | CE1–CE8, sin puntajes nuevos ni cumplimiento inventado |

No se incluyen capturas laborales/personales ajenas encontradas en carpetas generales.
El inventario no es un examen exhaustivo de todas las imágenes del equipo: se revisaron
capturas candidatas de la sesión 2026-11-17 y materiales NexoAndes identificados.

## Registros locales existentes del experimento

Directorio privado ignorado: `../observation/runs/u2-v1-v2-20261117-01/`.
No publicar logs crudos sin saneamiento. El plan binario nunca va en ZIP/repositorio.

| Archivo | Bytes | SHA-256 actual |
|---|---:|---|
| `config.initial.json` | 1211 | `d58f17ae3700bc4c2b07bcb50111ab2628b1a128cd032d431adda6fb97ca2ce6` |
| `controller.csv` | 183464 | `ffe3527d034f0c2022e766f2ed60f3a403d2ae0ded55e6c23dc2ad0b32ef53c0` |
| `controller.jsonl` | 243875 | `d6866e266fb0968ce12375e99aeff5a621c578fab88ff261ed47a077ea12e411` |
| `http.csv` | 890442 | `27d121fe0b082b36d42a0675d7ef695586f66a55416e750a400a244fecf1367b` |
| `http.jsonl` | 2190581 | `f1a49e1f984df5ebf6cde1ed38a6c04e1429a79c779b8965873b8bc7a3335082` |
| `preparation.json` | 3795 | `52c7e89a3d2def73c927673ed2f2b6a90c21a23a21bc71f77a86d0422d2f4229` |
| `v2-plan.sha256` | 117 | `8fe8ebff730c9dfafb07b083fd5ef142ddbe8f7e5a6202d884fa56173287d9e6` |
| `v2.tfplan` | 80419 | `d09e77e0833461f0cc9c7022d9c401960b686fa23d01714dc97f6238986800f7` |

Ausentes en ese directorio: events.jsonl, config.final.json, analysis.json,
v2-plan.txt y registro completo del apply. No se crean retrospectivamente eventos
ni informes aceptados. Los errores del controlador y fin por límite de duración
se conservan, aunque el HTTP registrado haya sido v1 correcto.

## Faltantes prioritarios para cerrar la entrega

1. Incorporar A02 (Mermaid/SVG/PNG) al paquete y conservar A01 como borrador; diagrama y hashes ya generados. Mantener el mapa de familias docentes.
2. Selección y saneamiento COMPLETADOS: empaquetar las copias assets/ según PDF_MANIFEST.json, sin incluir originales crudos.
3. Si hay logs ya existentes de apply inicial, recuperación y planes posteriores,
   anexarlos saneados; su ausencia no bloquea el PDF y se declara sin recrear resultados.
4. Completar trazabilidad de backend/identidad, IDs entre sesiones y cierre por categorías.
5. Incorporar evidencia de validaciones Azure y referencia S6 disponible.
6. Anotar URLs/IDs de CI/PR y revisión; mantener explícito INC-U2-001 y el alcance
   limitado de recuperación. No declarar reemplazo v2 o rollback funcional exitosos.
7. Preparar ficha PDF y ZIP limpio: sin state, .terraform, credenciales ni planes
   binarios. Declarar uso de IA (Codex: inventario, revisión y redacción del índice).

La consolidación añade únicamente archivos de evidencia y manifiestos; no se
consultó/modificó cloud, infraestructura o U1, ni se realizaron commit/push.
