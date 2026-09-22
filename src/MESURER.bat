@echo off
setlocal enabledelayedexpansion
rem ============================================================
rem  Lanceur hors ligne du banc rolling shutter.
rem
rem  GLISSEZ UN DOSSIER DE PHOTOS SUR CETTE ICONE, ou lancez ce
rem  fichier et indiquez le dossier quand il le demande.
rem
rem  Rien ici n'a besoin d'Internet : le calcul est entierement
rem  local. Seul l'interpreteur Python de QGIS est necessaire,
rem  parce qu'il embarque numpy et Pillow.
rem ============================================================

title Banc rolling shutter - mesure hors ligne
cd /d "%~dp0"

rem --- Trouver l'interpreteur Python de QGIS -------------------
rem On ne code pas un chemin en dur : le numero de version change
rem a chaque mise a jour, et le lanceur cesserait de fonctionner
rem sans que rien n'explique pourquoi.
set "PY="
for %%D in ("C:\Program Files" "C:\Program Files (x86)" "C:\OSGeo4W" "D:\Program Files") do (
  if exist "%%~D" (
    for /f "delims=" %%Q in ('dir /b /ad "%%~D\QGIS*" 2^>nul') do (
      if exist "%%~D\%%Q\bin\python-qgis.bat" set "PY=%%~D\%%Q\bin\python-qgis.bat"
    )
  )
)
if exist "C:\OSGeo4W\bin\python-qgis.bat" set "PY=C:\OSGeo4W\bin\python-qgis.bat"

if not defined PY (
  echo.
  echo   Python de QGIS introuvable.
  echo.
  echo   Ce lanceur a besoin de l'interpreteur installe avec QGIS,
  echo   qui embarque numpy et Pillow. Cherchez un fichier nomme
  echo   python-qgis.bat sous le dossier d'installation de QGIS,
  echo   et lancez a la main :
  echo.
  echo      "chemin\vers\python-qgis.bat" balayage.py "dossier de photos"
  echo.
  pause
  exit /b 1
)

rem --- Le dossier de photos -----------------------------------
set "DOSSIER=%~1"
if "%DOSSIER%"=="" (
  echo.
  echo   Glissez un dossier de photos sur cette icone, ou
  set /p "DOSSIER=  indiquez ici le chemin du dossier : "
)
if "%DOSSIER%"=="" exit /b 1

if not exist "%DOSSIER%\" (
  echo.
  echo   "%DOSSIER%" n'est pas un dossier.
  pause
  exit /b 1
)

echo.
echo   Interpreteur : %PY%
echo   Dossier      : %DOSSIER%
echo.
echo   Analyse en cours. Comptez une a deux minutes pour cent photos.
echo.

"%PY%" balayage.py "%DOSSIER%"

echo.
echo ============================================================
echo   Pour memoire : ce qui vaut preuve, c'est l'ACCORD entre
echo   cadences. Le temps de lecture est une propriete du capteur
echo   et ne peut pas dependre de la cadence de la LED. Une seule
echo   cadence exploitable ne prouve rien.
echo ============================================================
echo.
pause
