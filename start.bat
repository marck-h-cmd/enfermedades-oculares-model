@echo off
echo =======================================================
echo     Iniciando Suite Clinica OcularDiagnose
echo =======================================================
echo.

echo [1/3] Iniciando Servidor Backend (FastAPI)...
start "Backend OcularDiagnose" cmd /k ".\venv\Scripts\activate.bat && uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload"

echo [2/3] Iniciando Servidor Frontend (Next.js)...
start "Frontend OcularDiagnose" cmd /k "cd frontend && npm run dev"

echo [3/3] Iniciando Interfaz Streamlit (Dashboard Antiguo)...
start "Streamlit OcularDiagnose" cmd /k ".\venv\Scripts\activate.bat && streamlit run app.py"

echo.
echo =======================================================
echo.
echo ¡Los tres servidores se han lanzado en ventanas separadas!
echo - Frontend (Next.js) estara en:   http://localhost:3000
echo - Backend (FastAPI) estara en:    http://127.0.0.1:8000
echo - Dashboard (Streamlit) estara en: http://localhost:8501
echo.
echo Puedes minimizar esas tres ventanas negras pero NO las cierres.
echo =======================================================
pause
