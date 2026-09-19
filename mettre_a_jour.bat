@echo off
REM Met à jour la présentation de vitrine : lit les annonces sur laforet.com/montauban,
REM régénère public\data.json + images, puis publie si le dossier est un dépôt git.
REM À planifier chaque jour (Planificateur de tâches Windows) — voir LISEZ-MOI.md
chcp 65001 >nul
cd /d "%~dp0"
python generer.py
if errorlevel 1 (
  echo Echec de la generation - la version precedente reste en ligne.
  exit /b 1
)
if exist ".git" (
  git add -A public instagram
  git diff --cached --quiet || (git commit -m "Mise a jour vitrine %date% %time%" && git push)
)
