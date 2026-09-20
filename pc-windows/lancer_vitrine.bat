@echo off
REM Lance la vitrine Laforet Montauban en plein ecran (mode kiosque) et la relance
REM automatiquement si le navigateur se ferme ou plante. A placer dans le dossier
REM Demarrage de Windows (voir LISEZ-MOI.md, section 3).
REM
REM Si l'ecran affiche la page couchee, ajouter ?rot=90 (ou ?rot=-90) a la fin de
REM l'adresse ci-dessous.

set "URL=https://laurentallsi.github.io/vitrine-laforet-montauban/"
set "BROWSER="

if exist "%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe" set "BROWSER=%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe"
if not defined BROWSER if exist "%ProgramFiles%\Microsoft\Edge\Application\msedge.exe" set "BROWSER=%ProgramFiles%\Microsoft\Edge\Application\msedge.exe"
if not defined BROWSER if exist "%ProgramFiles%\Google\Chrome\Application\chrome.exe" set "BROWSER=%ProgramFiles%\Google\Chrome\Application\chrome.exe"
if not defined BROWSER if exist "%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe" set "BROWSER=%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"

if not defined BROWSER (
  echo Aucun navigateur recent trouve - installez Edge ou Chrome, voir LISEZ-MOI.md.
  pause
  exit /b 1
)

REM Profil dedie : evite que le navigateur "se raccroche" a une instance deja active
REM en arriere-plan (sinon start /wait rend la main tout de suite et la boucle
REM ouvrirait une nouvelle fenetre toutes les 3 secondes).
set "PROFIL=%LOCALAPPDATA%\VitrineKiosk"

:boucle
start /wait "" "%BROWSER%" --kiosk "%URL%" --user-data-dir="%PROFIL%" --edge-kiosk-type=fullscreen --no-first-run --noerrdialogs --disable-session-crashed-bubble --overscroll-history-navigation=0
timeout /t 3 /nobreak >nul
goto boucle
