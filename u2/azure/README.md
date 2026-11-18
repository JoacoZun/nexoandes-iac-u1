# Azure U2: entrega de código, sin despliegue

**Excepción docente S6:** el usuario informa que el docente permitió entregar
Azure como código sin despliegue. Se adopta ese alcance para esta entrega;
ver [EVALUATION.md](EVALUATION.md). **Azure NO fue desplegado**: no hay evidencia
Azure real de recursos, endpoint, HTTP, metadata, plan remoto o limpieza.
Los resultados locales y mocks se identifican como tales, sin sustituirlos por
ejecuciones ficticias. No es necesario obtener una cuenta Azure para esta entrega.

Root independiente `u2/azure/`, con módulo local `modules/infrastructure` y provider
`hashicorp/azurerm` exactamente 4.65.0; Terraform >=1.16.6. No modificar/ejecutar el
root U1 ni AWS para validar este root. Todos los archivos de esta etapa quedan aquí.

## Composición e identidad

Reutiliza `../` exclusivamente como composición de contratos puros. Azure recibe
siempre `app_version="v1"`; no hay input que permita seleccionar v2 en este root.
El módulo también rechaza contratos v2 mediante precondición de la VM.
Identidad indicada por el usuario: X=8 ratificado, student=a008 derivado y
course=c50 (equivalencia asumida con sección 50). El archivo local ignorado
`../identity.tfvars` contiene esos valores; requiere carga explícita mediante
`-var-file=../identity.tfvars` en una futura operación autorizada. No se carga
automáticamente. Los defaults siguen conservadores (`x_ratified=false`).
El test mock del root comprueba X=8/a008/c50 y su key Azure independiente;
las pruebas del módulo mantienen c99 como fixture sintética deliberada.
`course` y `build_ref` son obligatorios y validados por el contrato compartido.
Prefijo na-u2-cNN-aNNN-az y tags proyecto/fase/alumno/curso/proveedor propagados
explícitamente donde Azure lo admite; no se presume herencia desde el RG.

`deployment` exige tenant/suscripción UUID, ubicación, tamaño VM, imagen Marketplace
con publisher/offer/sku/versión exacta (no latest), usuario Linux y clave pública RSA,
CIDR HTTP autorizados, tamaño/tipo de disco. Sin credenciales, contraseñas ni valores
reales predeterminados. La clave pública es configuración de aprovisionamiento;
no se abre SSH ni se exige ingreso SSH. Nunca proporcionar clave privada.

## Recursos y tráfico

- Resource Group propio, VNet 172.20.X.0/24 y subnet 172.20.X.0/26.
- NSG asociado a NIC: permite TCP/80 desde CIDR explícitos; deny de resto de entrada
  antes de reglas predeterminadas (incluye SSH y tráfico lateral no autorizado).
- IP pública IPv4 Standard estática asociada a NIC. IP privada Dynamic, asignada
  por Azure; no escribir IP ficticia en Portal/configuración.
- Subnet con default_outbound_access_enabled=false; salida explícita por la IP
  pública asociada a NIC. No se depende de salida predeterminada de Azure.
- Se conservan reglas outbound predeterminadas NSG para bootstrap, DNS y servicios
  de plataforma/agente; no afirmar que el egreso esté limitado a HTTP/HTTPS.
- VM Linux con imagen cloud-init autorizada, contraseña deshabilitada, disco
  administrado y tags. Espera asociación NSG y reglas antes de crear la VM.

No hay ALB, ASG, peering, failover, roles RBAC, credenciales ni actualizaciones v2.

## Plantilla y función

Integra el artefacto compartido `../templates/user_data_u2.sh.tpl` sin alteraciones:
SHA-256 `4445eadace792b80ac3e07886d99b80bfd1f250b892731dfc9abda77b9c9e2e3`.
`templatefile()` recibe provider=azure, X/alumno/curso/build y portal_version=v1;
el contrato aplica base64 una vez y la VM recibe ese valor en custom_data.
Se comprueba el límite de 64 KiB decodificados. No se ejecuta el bootstrap localmente.

Imagen pendiente de autorización/validación: requiere cloud-init, Bash, systemd,
Python >=3.8 (o repositorios accesibles), useradd, puerto 80 libre e IMDS Azure.
Validar compatibilidad de arquitectura, tamaño VM, mínimo de disco y condiciones
Marketplace antes de una operación cloud futura. El agente y cloud-init pueden
seguir ejecutándose después de crear la VM: provisioning success no demuestra Portal.

`endpoint`: IPv4/URL del recurso Public IP. `ids`: ARM IDs de RG/red/NIC/VM,
UUID de la VM para contrastar IMDS, IP privada y nombre del disco. `portal`: identidad,
build, hash y versión deseada, no una respuesta web observada. Verificar GET `/`,
`/api/info` y `/api/check` con HTTP 200 y datos reales; `/health` solo acredita proceso.

## State y acceso

Backend parcial azurerm con use_azuread_auth=true, distinto del S3 AWS/U1.
No hay storage account, container o key inventados. Deben preexistir y ser autorizados.
Key esperada expuesta por `context`: u2/<course>/<student>/azure/terraform.tfstate.
El output informa la key; no configura el backend. No migrar/copiar state U1/AWS.
El backend requerirá acceso de datos Blob y locking por lease, retención/versionado
y permisos mínimos; no guardar access keys/SAS ni secretos en archivos del proyecto.

Provider recibe tenant/suscripción explícitos. La autenticación futura debe ser externa
y autorizada; esta etapa no hace az login ni define secretos. Auto-registro de Resource
Providers desactivado: comprobar Microsoft.Compute/Microsoft.Network y permisos del
RG/destino por mecanismo autorizado. No se crean asignaciones RBAC automáticamente.

## Validación segura

1. `fmt -check -diff -recursive` únicamente en este root.
2. `init -backend=false -input=false`: descarga provider público y crea metadata/lock
   locales, no inicializa backend Azure ni requiere cuenta.
3. `validate`: esquema local.
4. Ejecutar `tests/check_offline.py` con Python/hcl2 disponible ANTES de `terraform test`.
5. Los seis runs usan mock_provider azurerm, override_during=plan y command=plan;
   no ejecutan apply ni un plan CLI real. Datos de cuenta, imagen, ubicación, IP y clave
   pública son fixtures sintéticas; no sirven para acceso ni acreditan ejecución.

Resultados reales de esta preparación se informan al finalizar; no confundirlos con
evidencia de despliegue. No ejecutar scripts/workflows de U1 como runner de Azure.

## Pendientes y costos

Para la entrega autorizada solo de código: conservar la referencia de clase S6
en la ficha y vincular código, validaciones offline y CI con el commit evaluado.
Tenant/suscripción/ubicación/imagen/tamaño, cuotas, clave pública, permisos,
backend y pipeline de despliegue quedan como requisitos de una eventual operación
futura, fuera de esta entrega; no se inventan valores para completarlos.
No se acredita operación Azure por mocks ni se asigna un puntaje de CE3/CE8:
la valoración de la excepción corresponde al docente. Azure permanece v1;
cambio/recuperación se evalúan en AWS y no quedan eximidos por esta excepción.

Una ejecución futura puede cobrar VM, disco administrado, Public IP Standard,
transferencia y almacenamiento del backend. No se asume crédito ni Free Tier.

Referencias del provider fijado:
- [VM Linux 4.65.0](https://github.com/hashicorp/terraform-provider-azurerm/blob/v4.65.0/website/docs/r/linux_virtual_machine.html.markdown)
- [Subnet y salida explícita](https://github.com/hashicorp/terraform-provider-azurerm/blob/v4.65.0/website/docs/r/subnet.html.markdown)
- [Provider/auth y registros](https://github.com/hashicorp/terraform-provider-azurerm/blob/v4.65.0/website/docs/index.html.markdown)

Implementación asistida por Codex para código y tests locales; sin operación cloud.

## Resultados históricos de implementación

- Terraform portátil 1.16.6: fmt/fmt-check PASS, init -backend=false -input=false
  PASS, validate PASS, terraform test: **6 passed, 0 failed**.
- Provider AzureRM 4.65.0 descargado del registro público con firma HashiCorp
  verificada; lock propio generado en este root. No se autenticó contra Azure.
- Guard offline aprobado antes de cada suite: seis runs, mock azurerm exclusivo,
  command=plan, módulos locales, sin data sources/provisioners; hash docente intacto.
- Cobertura: CIDR/red/egreso explícito, NSG/IP/NIC, cloud-init y ausencia de contraseña,
  X sin ratificar bloqueado, contrato v2 rechazado, identidad/endpoint/state y build.
- Primer intento: 5 passed/1 failed por comparación list/set de CIDR en el test.
  Se normalizó a conjuntos, sin cambiar las redes ni debilitar el control de egreso;
  la repetición completa pasó los seis casos.
- Solo archivos nuevos bajo u2/azure, incluidos metadata local .terraform ignorada
  y lock. Sin cambios en U1/AWS, plantilla, PATH global, commit ni push.

Estos resultados son validación de código/schemas con recursos simulados. No prueban
compatibilidad real de una imagen, cuota, permisos, metadata ni disponibilidad HTTP.

La revisión final local del 2026-11-17, identidad X=8/a008/c50 y excepción S6
se documentan en [EVALUATION.md](EVALUATION.md), con resultados actuales y límites.
