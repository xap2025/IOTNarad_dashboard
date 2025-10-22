@echo off
echo ==========================================
echo  Testing Login Page Layout
echo ==========================================
echo.

echo [1/3] Checking if app is running...
docker ps --filter "name=iotnarad_app" --format "table {{.Names}}\t{{.Status}}"
echo.

echo [2/3] Opening login page in browser...
start http://localhost:8050
echo.

echo [3/3] Layout should now be:
echo   ✅ Centered horizontally and vertically
echo   ✅ Beautiful purple gradient background
echo   ✅ White card with proper spacing
echo   ✅ Smooth animations
echo   ✅ Professional styling
echo.

echo ==========================================
echo  Expected Layout Features
echo ==========================================
echo.
echo ✅ Login card centered on screen
echo ✅ Purple gradient background
echo ✅ White card with rounded corners
echo ✅ IOTNarad logo and branding
echo ✅ Username and password fields
echo ✅ Login button with gradient
echo ✅ Floating decorative elements
echo ✅ Smooth slide-in animation
echo.
echo If layout is still not centered:
echo 1. Hard refresh browser (Ctrl+F5)
echo 2. Clear browser cache
echo 3. Try incognito mode
echo.
pause
