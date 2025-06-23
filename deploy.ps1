# Binance Trade Copier Deployment Script for Windows
# This script sets up and starts the Binance Trade Copier application

param(
    [string]$AppDir = "C:\binance_copier"
)

Write-Host "=== Binance Trade Copier Deployment Script ===" -ForegroundColor Green

# Stop existing processes
Write-Host "Stopping existing application processes..." -ForegroundColor Yellow
Get-Process -Name python -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like "*main.py*" } | ForEach-Object {
    Write-Host "Stopping process PID: $($_.Id)"
    Stop-Process -Id $_.Id -Force -ErrorAction SilentlyContinue
}
Start-Sleep -Seconds 3

# Verify Python installation
Write-Host "Checking Python installation..." -ForegroundColor Yellow
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Error "Python is not installed or not in PATH. Please install Python first."
    exit 1
}

$pythonVersion = python --version
Write-Host "Found: $pythonVersion" -ForegroundColor Green

# Change to application directory
if (-not (Test-Path $AppDir)) {
    Write-Host "Creating application directory: $AppDir" -ForegroundColor Yellow
    New-Item -ItemType Directory -Path $AppDir -Force
}

Set-Location $AppDir
Write-Host "Working directory: $(Get-Location)" -ForegroundColor Green

# Create required directories
@("data", "templates") | ForEach-Object {
    if (-not (Test-Path $_)) {
        New-Item -ItemType Directory -Path $_ -Force
        Write-Host "Created directory: $_" -ForegroundColor Green
    }
}

# Install dependencies
if (Test-Path "requirements.txt") {
    Write-Host "Installing Python dependencies..." -ForegroundColor Yellow
    python -m pip install --upgrade pip
    python -m pip install -r requirements.txt
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Dependencies installed successfully" -ForegroundColor Green
    } else {
        Write-Error "Failed to install dependencies"
        exit 1
    }
} else {
    Write-Warning "requirements.txt not found, skipping dependency installation"
}

# Start the application
Write-Host "Starting Binance Trade Copier..." -ForegroundColor Yellow
if (Test-Path "main.py") {
    try {
        $process = Start-Process -FilePath "python" -ArgumentList "main.py" -WorkingDirectory $AppDir -WindowStyle Hidden -PassThru
        
        if ($process) {
            Write-Host "Application started successfully!" -ForegroundColor Green
            Write-Host "Process ID: $($process.Id)" -ForegroundColor Green
            
            # Wait and verify the process is still running
            Start-Sleep -Seconds 5
            if (Get-Process -Id $process.Id -ErrorAction SilentlyContinue) {
                Write-Host "Process verification successful - application is running" -ForegroundColor Green
                
                # Try to test the health endpoint
                Start-Sleep -Seconds 5
                try {
                    $response = Invoke-RestMethod -Uri "http://localhost:8000/health" -TimeoutSec 10 -ErrorAction Stop
                    Write-Host "Health check passed!" -ForegroundColor Green
                    Write-Host ($response | ConvertTo-Json -Depth 2) -ForegroundColor Cyan
                } catch {
                    Write-Warning "Health endpoint not accessible yet, but application process is running"
                    Write-Host "The application may still be starting up or using a different port" -ForegroundColor Yellow
                }
                
                Write-Host "=== Deployment Completed Successfully! ===" -ForegroundColor Green
            } else {
                Write-Error "Process died after startup"
                exit 1
            }
        } else {
            Write-Error "Failed to start application"
            exit 1
        }
    } catch {
        Write-Error "Error starting application: $($_.Exception.Message)"
        exit 1
    }
} else {
    Write-Error "main.py not found in $AppDir"
    exit 1
}

Write-Host ""
Write-Host "To check application status later, run:" -ForegroundColor Cyan
Write-Host "Get-Process -Name python | Where-Object { `$_.CommandLine -like '*main.py*' }" -ForegroundColor White
Write-Host ""
Write-Host "To stop the application, run:" -ForegroundColor Cyan  
Write-Host "Get-Process -Name python | Where-Object { `$_.CommandLine -like '*main.py*' } | Stop-Process -Force" -ForegroundColor White
