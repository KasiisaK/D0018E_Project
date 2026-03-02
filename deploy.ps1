# Script by ChatGPT to make it easier to deploy the app to Elastic Beanstalk.
# deploy.ps1 - Clean build, copy dist + product images, and zip for Elastic Beanstalk

Write-Host "=== Starting clean deployment build ===" -ForegroundColor Cyan

# ────────────────────────────────────────────────
# Configuration
# ────────────────────────────────────────────────
$frontendDir    = "frontend"
$backendDir     = "backend"
$zipFile        = "bigmug-app.zip"
$distPath       = "$frontendDir\dist"
$staticPath     = "$backendDir\static"
$productImages  = "$frontendDir\src\assets\images"

# ────────────────────────────────────────────────
# Step 1: Clean previous build artifacts
# ────────────────────────────────────────────────
Write-Host "Cleaning old dist, static, and zip..." -ForegroundColor Yellow

# Remove old dist folder
if (Test-Path $distPath) {
    Remove-Item -Path $distPath -Recurse -Force -ErrorAction SilentlyContinue
    Write-Host "  → Removed old dist folder" -ForegroundColor Green
}

# Clear backend/static contents (keep the folder itself)
if (Test-Path $staticPath) {
    Remove-Item -Path "$staticPath\*" -Recurse -Force -ErrorAction SilentlyContinue
    Write-Host "  → Cleared backend/static contents" -ForegroundColor Green
} else {
    New-Item -ItemType Directory -Path $staticPath -Force | Out-Null
    Write-Host "  → Created empty backend/static folder" -ForegroundColor Green
}

# Delete old zip
if (Test-Path $zipFile) {
    Remove-Item -Path $zipFile -Force -ErrorAction SilentlyContinue
    Write-Host "  → Removed old $zipFile" -ForegroundColor Green
}

# ────────────────────────────────────────────────
# Step 2: Build frontend
# ────────────────────────────────────────────────
Write-Host "`nBuilding Vue frontend..." -ForegroundColor Yellow
Set-Location $frontendDir
npm run build
Set-Location $PSScriptRoot

# Check if build succeeded
if (-Not (Test-Path $distPath)) {
    Write-Host "ERROR: Build failed - dist folder was not created!" -ForegroundColor Red
    exit 1
}
Write-Host "Frontend build completed successfully." -ForegroundColor Green

# ────────────────────────────────────────────────
# Step 3: Copy dist → backend/static
# ────────────────────────────────────────────────
Write-Host "`nCopying dist → backend/static..." -ForegroundColor Yellow
Copy-Item -Path "$distPath\*" -Destination $staticPath -Recurse -Force
Write-Host "  → Copied built assets successfully" -ForegroundColor Green

# ────────────────────────────────────────────────
# Step 4: Copy product images from frontend/src/assets/images
# ────────────────────────────────────────────────
Write-Host "`nCopying product images from src/assets/images..." -ForegroundColor Yellow

if (Test-Path $productImages) {
    Copy-Item -Path "$productImages\*" -Destination $staticPath -Recurse -Force
    Write-Host "  → Copied all product images successfully" -ForegroundColor Green
} else {
    Write-Host "  WARNING: Product images folder not found: $productImages" -ForegroundColor Yellow
    Write-Host "  → Continuing without extra images..." -ForegroundColor Yellow
}

# ────────────────────────────────────────────────
# Step 5: Create new zip (only backend contents)
# ────────────────────────────────────────────────
Write-Host "`nCreating new zip archive: $zipFile" -ForegroundColor Yellow
Compress-Archive -Path "$backendDir\*" -DestinationPath $zipFile -Force
Write-Host "Zip created successfully." -ForegroundColor Green

# ────────────────────────────────────────────────
# Final summary
# ────────────────────────────────────────────────
Write-Host "`n=== Deployment package ready ===" -ForegroundColor Cyan
Get-Item $zipFile | Format-List Name, Length, LastWriteTime

Write-Host "`nNext step:" -ForegroundColor Cyan
Write-Host "  → Upload $zipFile to Elastic Beanstalk and deploy" -ForegroundColor White
Write-Host ""