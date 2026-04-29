@echo off
echo ═══════════════════════════════════════════════════════════════════════════
echo SJBIT ELECTIVE SYSTEM - FRESH START SCRIPT
echo ═══════════════════════════════════════════════════════════════════════════
echo.

echo Step 1: Deleting old database...
if exist db.sqlite3 (
    del db.sqlite3
    echo ✓ Database deleted
) else (
    echo ℹ No database file found
)
echo.

echo Step 2: Deleting old migrations...
if exist electives\migrations\0001_initial.py (
    del electives\migrations\0001_initial.py
    echo ✓ Old migrations deleted
) else (
    echo ℹ No old migrations found
)
echo.

echo Step 3: Creating new migrations...
python manage.py makemigrations
if %errorlevel% neq 0 (
    echo ✗ Failed to create migrations
    pause
    exit /b 1
)
echo ✓ Migrations created
echo.

echo Step 4: Applying migrations...
python manage.py migrate
if %errorlevel% neq 0 (
    echo ✗ Failed to apply migrations
    pause
    exit /b 1
)
echo ✓ Migrations applied
echo.

echo Step 5: Creating superuser...
echo.
echo Please enter superuser details:
echo Recommended - Username: admin, Password: admin123
echo.
python manage.py createsuperuser
if %errorlevel% neq 0 (
    echo ✗ Failed to create superuser
    pause
    exit /b 1
)
echo ✓ Superuser created
echo.

echo Step 6: Importing CSV data...
python manage.py import_csv
if %errorlevel% neq 0 (
    echo ✗ Failed to import CSV data
    echo ℹ Make sure CSV files are in the project root
    pause
    exit /b 1
)
echo ✓ CSV data imported
echo.

echo Step 7: Collecting static files...
python manage.py collectstatic --noinput
if %errorlevel% neq 0 (
    echo ✗ Failed to collect static files
    pause
    exit /b 1
)
echo ✓ Static files collected
echo.

echo ═══════════════════════════════════════════════════════════════════════════
echo SETUP COMPLETE!
echo ═══════════════════════════════════════════════════════════════════════════
echo.
echo Next steps:
echo 1. Run: python manage.py runserver
echo 2. Open browser: http://127.0.0.1:8000/
echo 3. Login as admin: admin / admin123
echo 4. Login as student: [student_id] / student123
echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo.
pause
