@echo off
setlocal EnableExtensions
cd /d "%~dp0"
where git >nul 2>nul
if errorlevel 1 (
 echo ERRO: Git for Windows nao instalado. Instale https://git-scm.com/downloads/win
 pause
 exit /b 1
)
if not exist "angulo-ase-renderizador\.github\workflows\docker-publish.yml" (
 echo ERRO: Pasta do workflow ausente.
 pause
 exit /b 1
)
set "DEST=%TEMP%\angulo-ase-renderizador-publicar"
if exist "%DEST%" (
 echo ERRO: Pasta temporaria ja existe: %DEST%
 echo Renomeie ou remova manualmente apos conferir seu conteudo.
 pause
 exit /b 1
)
git clone https://github.com/john1santos111-web/angulo-ase-renderizador.git "%DEST%"
if errorlevel 1 goto fail
cd /d "%DEST%"
git checkout main
if errorlevel 1 goto fail
if exist "app.py" del /q "app.py"
if exist "docker-publish.yml" del /q "docker-publish.yml"
xcopy /E /I /Y "%~dp0angulo-ase-renderizador\*" "%DEST%\" >nul
if errorlevel 1 goto fail
copy /Y "%~dp0angulo-ase-renderizador\.dockerignore" "%DEST%\.dockerignore" >nul
if not exist "%DEST%\.github\workflows\docker-publish.yml" goto fail
if not exist "%DEST%\handler.py" goto fail
git add -A
git diff --cached --quiet
if not errorlevel 1 (
 echo Nenhuma alteracao pendente.
 goto done
)
git commit -m "Implantar estrutura completa RunPod Serverless"
if errorlevel 1 goto fail
git push origin main
if errorlevel 1 goto fail
:done
echo.
echo SUCESSO: Confira https://github.com/john1santos111-web/angulo-ase-renderizador/actions
pause
exit /b 0
:fail
echo.
echo ERRO: Publicacao nao concluida. Confira as mensagens acima.
pause
exit /b 1
