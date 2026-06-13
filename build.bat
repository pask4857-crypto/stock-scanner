@echo off

echo ==========================
echo Build Start
echo ==========================

call .venv\Scripts\activate.bat

python -m PyInstaller --clean --onefile --windowed --name TWStockScanner --add-data "stocks.csv;." gui.py

echo.
echo ==========================
echo Build Complete
echo ==========================

if exist dist (
    start dist
)

pause