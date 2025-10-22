@echo off
echo ==========================================
echo  Testing Dashboard Layout
echo ==========================================
echo.

echo [1/3] Checking if app is running...
docker ps --filter "name=iotnarad_app" --format "table {{.Names}}\t{{.Status}}"
echo.

echo [2/3] Opening dashboard in browser...
start http://localhost:8050
echo.

echo [3/3] Dashboard layout should now be:
echo   ✅ Professional sidebar with dark blue gradient
echo   ✅ Main content area with proper spacing
echo   ✅ White header bar with shadows
echo   ✅ Beautiful stat cards with hover effects
echo   ✅ Proper navigation with active states
echo   ✅ Responsive design
echo.

echo ==========================================
echo  Expected Dashboard Features
echo ==========================================
echo.
echo ✅ Dark blue sidebar (280px width)
echo ✅ IOTNarad logo with blue microchip icon
echo ✅ Navigation menu (Home, Analytics, Devices, Help)
echo ✅ White header bar with page title
echo ✅ Light grey main content area
echo ✅ Four stat cards with icons and numbers
echo ✅ Getting Started section
echo ✅ System Status section
echo ✅ Professional shadows and hover effects
echo.
echo If layout is still not perfect:
echo 1. Hard refresh browser (Ctrl+F5)
echo 2. Clear browser cache
echo 3. Try incognito mode
echo.
pause
