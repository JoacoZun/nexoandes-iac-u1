# Git y pull request — preparado, no ejecutado

Base auditada: main y feature/fase1-iac en `7869232`; rama activa feature/fase1-iac.
README/.gitignore versionados; 14 archivos Terraform vacíos sin seguimiento antes
de implementar. No se ejecutaron commit/push/merge ni creación de PR.

Revisar primero `git status --short --branch`, `git diff --check` y diffs de cada
grupo. Los archivos nuevos se revisan con `git add -N <ruta>` si se desea verlos con
git diff (modifica solo índice; aquí no se ejecutó). No usar `git add .` sin inspección.

Comandos propuestos para commits atómicos, ejecutar solo con autorización del usuario:

```powershell
git switch feature/fase1-iac
git add main.tf variables.tf outputs.tf versions.tf providers.tf modules .terraform.lock.hcl templates/README.md .gitignore .gitattributes
git commit -m "feat: implementa arquitectura modular AWS de fase 1"
git add tests .tflint.hcl .checkov.yml requirements-ci.txt scripts/check_repository.py scripts/Invoke-Checks.ps1
git commit -m "test: incorpora aserciones mock y controles de calidad IaC"
git add .github ci
git commit -m "ci: prepara controles sin AWS y candidato de despliegue protegido"
git add README.md docs scripts/Verify-Deployment.ps1 scripts/Verify-Cleanup.ps1 scripts/Build-Submission.ps1
git commit -m "docs: documenta operacion evidencias y entrega verificable"
git push -u origin feature/fase1-iac
gh pr create --base main --head feature/fase1-iac --title "feat: infraestructura modular NexoAndes fase 1" --body-file docs/PR_BODY.md
```

Si gh no está disponible, abrir compare y seleccionar main como base:
https://github.com/JoacoZun/nexoandes-iac-u1/compare/main...feature/fase1-iac
Copiar `docs/PR_BODY.md`, solicitar revisión humana real y registrar PR/comentarios/SHA.
No inventar revisor ni aprobación. No fusionar hasta completar guía y requisitos.

Si el entorno sandbox detecta dubious ownership, usar por comando
`git -c safe.directory=C:/Users/il_fl/Desktop/nexoandes-iac-u1 <subcomando>`.
No se cambió configuración global de Git. Los commits anteriores son una propuesta
de agrupación; revisar dependencias y resultados finales antes de ejecutarlos.
