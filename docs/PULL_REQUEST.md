# Git y Draft Pull Request existente

Auditoría de solo lectura del 24-10-2026: `feature/fase1-iac` en
`e7f6025bc8fd7e221942c19d3fd0eb579809410b`, coincide con la cabeza remota de
[Draft PR #1](https://github.com/JoacoZun/nexoandes-iac-u1/pull/1), abierta hacia
`main` (`78692328cfa0536fd80334168a27c5fed9790eef`). Creada a las 12:26:12,
America/Santiago (UTC−03:00). API de reviews: **0 revisiones registradas**.
La sesión comenzó con working tree limpio; los cambios de preparación de lista 8
son locales y todavía no forman parte de la PR ni de sus checks aprobados.

No crear una segunda PR, no cambiar a Ready, aprobar, cerrar ni fusionar desde
esta preparación. `docs/PR_BODY.md` es únicamente una descripción propuesta local;
no se modificó la descripción remota. La revisión automática no es aprobación humana.

## Historial real y comparación

| Commit | Cambio |
|---|---|
| `86dc894e8c257649a07868f733d606c0f5f642cf` | feat(iac): infraestructura modular |
| `b5494aa250a884059bfc5472f396e7837b729086` | test(iac): pruebas y controles |
| `3f274f0f54456dc4390cf2dd3c9de916eb504be8` | ci: validación y despliegue desactivado |
| `1c0966c31ab19b31f6f4a1b71516eaae7da9039f` | docs: arquitectura y evidencias |
| `e7f6025bc8fd7e221942c19d3fd0eb579809410b` | fix(ci): checksum Linux AWS Provider |

La comparación `git diff main...HEAD --stat` mostró 46 archivos, 1902 inserciones
y 25 eliminaciones en la implementación publicada. La API de archivos PR corroboró
46 archivos. Es una comparación de commits; no incluye los nuevos cambios locales.
Consultar [comparación actual](https://github.com/JoacoZun/nexoandes-iac-u1/pull/1/files).

Comandos de consulta que no alteran GitHub:

```powershell
git status --short --branch
git log main..HEAD --oneline
git diff main...HEAD --stat
git diff --stat
git diff --check
```

## Revisión técnica antes de autorizar integración

1. Cotejar el SHA de la PR y el de todos los checks; repetir CI cuando se publiquen
   los cambios locales de lista 8. Un check de e7f6025 no acredita un diff posterior.
2. Revisar root default 8, subnet 172.16.8.0/24 y parametrización de network con
   otro X; nombres y tags deben compartir student_id y ListNumber.
3. Cotejar VPC/ruta/asociación, única entrada TCP/80, ausencia de SSH/key pair,
   egreso HTTP/HTTPS, IMDSv2, cifrado y eliminación del volumen raíz.
4. Verificar contrato, origen y hash de la plantilla docente; no aprobar una fixture
   de mocks como portal. Confirmar AMI/SO/tipo/región con la guía.
5. Revisar lock sin hashes manuales ficticios: SHA256 oficiales Linux/Windows y
   `init -lockfile=readonly`. Revisar pruebas negativas y parsers en jobs separados.
6. Confirmar CI sin credenciales/plan/apply, candidato aún disabled y adaptadores
   bloqueados hasta guía. Revisar plan protegido, gate real, backend/locking y roles.
7. Registrar comentarios humanos, correcciones, fecha y resolución. Hoy no hay
   aprobación humana; mantener Draft mientras falten materiales y revisión.

Si el entorno sandbox detecta dubious ownership, usar por comando
`git -c safe.directory=C:/Users/il_fl/Desktop/nexoandes-iac-u1 <subcomando>`.
No se cambió configuración global de Git. La primera auditoría encontró 14 .tf
vacíos y ambas ramas en 7869232; ese estado es histórico, ya superado por los cinco
commits anteriores. En esta sesión no se ejecutó commit/push/merge ni escritura GitHub.
