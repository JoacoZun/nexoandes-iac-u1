# Azure U2: alcance de entrega autorizado en clase S6

Registro local: 2026-11-17, America/Santiago.
Fuente de la autorización: declaración explícita del usuario en esta conversación:
el docente permitió en clase S6 entregar Azure como código sin despliegue.
Se documenta esa autorización informada; no se adjunta ni se inventa acta, mensaje
del docente, fecha de clase o modificación escrita de la rúbrica.

**Azure NO fue desplegado.** No se utilizaron cuentas Azure para esta preparación.
No hay IDs, IP, respuesta HTTP, metadata, limpieza ni plan posterior reales Azure
acreditados por estos archivos. No deben usarse outputs mock como capturas cloud.
La excepción se limita a Azure; no acredita reemplazo ni recuperación AWS.

## Identidad y composición entregadas

- X=8 ratificado por el usuario; student=a008 derivado; course=c50 por sección 50
  (equivalencia asumida, sin atribuirla al documento docente).
- La identidad local está en ../identity.tfvars, ignorado y no auto-cargado.
  El test root versionado fija explícitamente esos tres valores y ratificación.
- Root u2/azure -> composición pura u2/ -> módulo portal_azure -> infraestructura.
- Redes resultantes: VNet 172.20.8.0/24 y subnet 172.20.8.0/26.
- RG, NSG, IP pública Standard estática, NIC con IP privada dinámica, VM Linux
  y disco administrado. Tags propagados a recursos compatibles.
- HTTP solo desde CIDR declarados, denegación del resto de entrada, sin SSH
  abierto ni contraseña. La clave administrativa requerida es pública, no privada.
- Egreso explícito mediante IP pública/NIC; outbound NSG predeterminado, sin
  afirmar filtrado exclusivo HTTP/HTTPS ni conectividad realmente comprobada.
- Portal siempre v1: plantilla docente intacta, templatefile y base64 una vez
  en custom_data. Límite decodificado 64 KiB; precondición rechaza contrato v2.

## Providers, entradas y state

Terraform >=1.16.6,<2; CI fija 1.16.6. AzureRM =4.65.0 y lock independiente
con hashes existentes conservados. resource_provider_registrations=none evita
registro automático; cualquier despliegue futuro necesita providers registrados.
No hay data sources, provisioners ni bootstrap ejecutado por los tests.

deployment exige tenant/suscripción, ubicación, tamaño VM, usuario, clave pública
RSA, CIDR, tamaño/tipo de disco e imagen publisher/offer/sku/versión fija.
build_ref es obligatorio, no una identidad inventada de ejecución Azure.
Sin esos parámetros reales no hay configuración de despliegue completa: esto
no bloquea validate ni tests mock de la entrega de código autorizada.

Backend azurerm parcial con autenticación Entra, sin credenciales ni destino
inventado; key esperada u2/c50/a008/azure/terraform.tfstate, distinta de AWS/U1.
El output no configura la key. No hubo init remoto ni migración/copias de state.
endpoint/ids solo producirán valores reales después de un despliegue futuro.
portal/context describen identidad, versión deseada y contexto, no verificación HTTP.

## Evidencia evaluable y límites

| Familia/criterio | Entrega local | Límite declarado |
|---|---|---|
| E01 / CE1-CE2 | Arquitectura de código y equivalencias RG/VNet/VM/NSG frente a AWS | No representar recursos Azure como existentes |
| E02 / CE3-CE8 | Módulos, contratos, versiones/lock, outputs y separación de state/accesos | No acreditar autenticación ni backend operativo |
| E03 / CE3 | Código, validate y seis runs mock, conforme a excepción S6 informada | No despliegue, API, HTTP o plan posterior Azure; valoración por docente |
| E04 / CE4 | Bootstrap versionado y Portal v1 reproducible en código | Imagen y compatibilidad cloud no verificadas |
| E05-E07 / CE5-CE7 | Sin sustitución por los mocks Azure | Siguen siendo requisitos AWS y su contingencia propia |
| E08 / CE8 | Trazabilidad y declaración de no despliegue | No afirmar limpieza Azure ejecutada; no hubo recursos creados por esta preparación |

La evaluación original exige ambas nubes; la entrega se acoge a la excepción
informada de S6, no a una lectura que convierta simulación en despliegue.
No se presupone puntaje ni exención de requisitos AWS.

## CI y reproducción offline

.github/workflows/u2-ci.yml mantiene celda u2/azure, permisos contents:read,
sin credenciales/deploy y acciones fijadas por SHA. Guarda dependencias antes
del aislamiento de red Linux; validate/tests posteriores se ejecutan en namespace
sin salida externa y fallan si el aislamiento no puede establecerse.
Las pruebas deben pasar primero check_ci_safety.py y tests/check_offline.py:
solo mock_provider azurerm, command=plan dentro de terraform test y sin remapeos
a providers reales. Esto no autoriza un plan CLI contra Azure.

La validación local Windows no reproduce el aislamiento Linux. La ejecución de
CI en GitHub y su URL/resultado deben incorporarse cuando exista una ejecución
real; no se afirma que haya ocurrido en esta revisión.

Pendientes de entrega: referencia S6 disponible para trazabilidad (si existe),
diagrama/ficha PDF actualizados al alcance, commit evaluado y resultado CI real.
No se requieren credenciales, despliegue o limpieza ficticia para completar esto.

Uso de IA: Codex asistió revisión de código, documentación y pruebas offline.

## Resultado local del 2026-11-17

- Terraform portátil 1.16.6: fmt y fmt-check recursivos de u2/azure, PASS.
- Guards común CI y específico Azure antes de test: PASS; seis runs con mock
  AzureRM y command=plan, sin data sources/provisioners ni providers reales en tests.
- terraform validate: PASS. terraform test: 6 passed, 0 failed; teardown mock
  no representa creación ni eliminación de recursos Azure.
- Root: identidad X=8 ratificada, a008/c50, key Azure, redes y tags del contrato.
- Módulo: red, HTTP por CIDR, deny del resto, asociación NSG/NIC, IP explícita,
  cloud-init, ausencia de contraseña, bloqueo de X sin ratificar y rechazo de v2.
- actionlint sobre u2-ci.yml: PASS (sin shellcheck externo). No se cambió el workflow.
- Regresión Python U2: 45 tests, PASS, incluidos guards de los tres roots.
- Plantilla docente intacta; locks conservados. No se ejecutó init ni plan CLI,
  no se consultaron AWS/Azure y no se usaron credenciales.
- Windows no acredita namespace Linux ni una ejecución CI remota. El entorno
  .venv antiguo no pudo arrancar por su intérprete ausente; se utilizó Python
  portátil y dependencias existentes en .tools/u2-ci-deps, sin instalar paquetes.
