# Capturas saneadas para la ficha U2

22 copias C01–C22 de capturas existentes; originales externos conservados.
No se crearon imágenes de resultados, consolas, despliegues o autorizaciones.

Usar `../PDF_MANIFEST.json` para construir la ficha: selecciona 17 capturas
principales y cinco de reserva, sin duplicar imágenes entre conjuntos.
E01 usa el SVG técnico definitivo, no la imagen anterior A01.
E09 usa documentación real de validaciones offline y referencia cruzada a CI:
no existe captura de despliegue Azure ni se fabricó una consola de tests.

`../ASSETS_PROVENANCE.json` registra para cada copia: nombre original, alias de
procedencia, fechas disponibles, dimensiones, SHA-256 original/saneado, criterio,
selección y coordenadas de las redacciones. Las rutas privadas no se publican; los originales externos quedan fuera del
repositorio. El índice público enlaza únicamente copias saneadas.

## Saneamiento

Redacciones deterministas mediante rectángulos negros opacos sobre píxeles RGB.
Se ocultaron usuarios/autores personales, cuentas, ARN, identificadores de recursos,
direcciones públicas/privadas y hostname donde aparecían. No se leyeron archivos
de credenciales ni se consultaron servicios externos. No se añade texto sustituto
que aparente ser parte del resultado original.

Se conservan identidad académica a008/c50/X=8, nombres lógicos del proyecto,
versiones/build/hash, estados de salud, contadores, mensajes de error y fechas
visibles. Algunos prefijos/campos junto a identificadores quedan bajo las máscaras;
los originales permiten la auditoría privada, sin publicar esos valores.

No se cambia resolución ni encuadre. Se elimina metadata al guardar PNG, sin
capas, alpha ni una imagen original oculta. Se verificó que fuera de las zonas
de redacción todos los píxeles permanecen idénticos a los originales.
Las 22 copias fueron revisadas visualmente; se corrigieron omisiones del OCR local.
Los hashes acreditan integridad de archivos, no autenticidad independiente del cloud.

## Límites que deben acompañar las imágenes

- AWS fue desplegado históricamente y posteriormente eliminado.
- SCP bloqueó StartInstanceRefresh: no hubo reemplazo v2 exitoso acreditado.
- Recuperación de configuración v1 no es rollback funcional v2→v1.
- Azure se entrega solo como código por autorización S6 informada por el usuario.
- 20 recursos destruidos y consultas vacías ASG/ALB/VPC no prueban limpieza global.
- CI verde y PR #3 no prueban merge/aprobación humana.
- La fecha del nombre del archivo no certifica UTC; distinguirla del contenido.
- El timeout inicial C03 se conserva en reserva y se menciona en el relato.

Los logs históricos no localizados se declaran como limitaciones, no como bloqueo
para construir el PDF ni motivo para recrear una ejecución. No publicar planes
binarios, state, registros crudos o capturas originales sin revisar/sanear.
