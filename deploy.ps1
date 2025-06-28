# Binance Trade Copier - Production Deployment Script
# This script updates the codebase from git and restarts the application

param(
    [string]$ProjectPath = "C:\binance_trade_copier",
    [switch]$SkipGitPull = $false,
    [switch]$SkipRestart = $false,
    [int]$HealthCheckRetries = 3
)

Write-Host "=== Binance Trade Copier Deployment Script ==="
Write-Host "Project Path: $ProjectPath"
Write-Host "Skip Git Pull: $SkipGitPull"
Write-Host "Skip Restart: $SkipRestart"
Write-Host ""

# Function to write colored output
function Write-Status {
    param([string]$Message, [string]$Status = "INFO")
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    switch ($Status) {
        "SUCCESS" { Write-Host "[$timestamp] ✅ $Message" -ForegroundColor Green }
        "ERROR" { Write-Host "[$timestamp] ❌ $Message" -ForegroundColor Red }
        "WARNING" { Write-Host "[$timestamp] ⚠️ $Message" -ForegroundColor Yellow }
        default { Write-Host "[$timestamp] ℹ️ $Message" -ForegroundColor Cyan }
    }
}

# Function to handle errors and exit
function Exit-WithError {
    param([string]$Message)
    Write-Status $Message "ERROR"
    exit 1
}

try {
    # Change to project directory
    Write-Status "Changing to project directory: $ProjectPath"
    if (-not (Test-Path $ProjectPath)) {
        Exit-WithError "Project directory does not exist: $ProjectPath"
    }
    
    Set-Location $ProjectPath
    Write-Status "Changed to directory: $(Get-Location)"
    
    # Verify this is a git repository
    if (-not (Test-Path ".git")) {
        Exit-WithError "Not a git repository. Missing .git directory."
    }
    
    # Git operations (unless skipped)
    if (-not $SkipGitPull) {
        Write-Status "Fetching latest changes from main branch..."
        try {
            $fetchResult = git fetch origin main 2>&1
            if ($LASTEXITCODE -ne 0) {
                Exit-WithError "Failed to fetch from origin: $fetchResult"
            }
            Write-Status "Fetch completed successfully"
        } catch {
            Exit-WithError "Exception during git fetch: $($_.Exception.Message)"
        }
        
        Write-Status "Resetting to latest main branch..."
        try {
            $resetResult = git reset --hard origin/main 2>&1
            if ($LASTEXITCODE -ne 0) {
                Exit-WithError "Failed to reset to origin/main: $resetResult"
            }
            Write-Status "Reset completed successfully"
        } catch {
            Exit-WithError "Exception during git reset: $($_.Exception.Message)"
        }
        
        # Show current commit
        try {
            $currentCommit = git rev-parse HEAD
            $shortCommit = git rev-parse --short HEAD
            Write-Status "Current commit: $shortCommit ($currentCommit)"
        } catch {
            Write-Status "Could not retrieve git commit information" "WARNING"
        }
    } else {
        Write-Status "Skipping git pull operations" "WARNING"
    }
    
    # Stop existing Python processes (unless skipped)
    if (-not $SkipRestart) {
        Write-Status "Stopping existing Python processes..."
        try {
            $pythonProcesses = Get-Process -Name python -ErrorAction SilentlyContinue
            if ($pythonProcesses) {
                $pythonProcesses | ForEach-Object {
                    Write-Status "Stopping Python process (PID: $($_.Id))"
                    Stop-Process -Id $_.Id -Force -ErrorAction SilentlyContinue
                }
                Write-Status "Stopped $($pythonProcesses.Count) Python process(es)"
            } else {
                Write-Status "No Python processes found to stop"
            }
        } catch {
            Write-Status "Error stopping Python processes: $($_.Exception.Message)" "WARNING"
        }
        
        # Wait for processes to terminate
        Write-Status "Waiting for processes to terminate..."
        Start-Sleep -Seconds 3
        
        # Verify all Python processes are stopped
        try {
            $remainingProcesses = Get-Process -Name python -ErrorAction SilentlyContinue
            if ($remainingProcesses) {
                Write-Status "Warning: $($remainingProcesses.Count) Python processes still running" "WARNING"
            }
        } catch {
            Write-Status "Could not verify process termination" "WARNING"
        }
        
        # Start the application
        Write-Status "Starting Binance Trade Copier..."
        try {
            $startInfo = New-Object System.Diagnostics.ProcessStartInfo
            $startInfo.FileName = "python"
            $startInfo.Arguments = "main.py"
            $startInfo.WorkingDirectory = $ProjectPath
            $startInfo.UseShellExecute = $false
            $startInfo.CreateNoWindow = $false
            $startInfo.WindowStyle = "Hidden"
            
            $process = [System.Diagnostics.Process]::Start($startInfo)
            Write-Status "Started application with process ID: $($process.Id)"
        } catch {
            Exit-WithError "Failed to start application: $($_.Exception.Message)"
        }
        
        # Wait for application to initialize
        Write-Status "Waiting for application to initialize..."
        Start-Sleep -Seconds 5
    } else {
        Write-Status "Skipping application restart" "WARNING"
    }
    
    # Verify deployment
    Write-Status "Verifying deployment..."
    
    # Check if Python processes are running
    $pythonProcesses = Get-Process -Name python -ErrorAction SilentlyContinue
    if ($pythonProcesses) {
        Write-Status "Python processes found: $($pythonProcesses.Count)"
        $pythonProcesses | ForEach-Object { 
            Write-Status "  Process ID: $($_.Id), Start Time: $($_.StartTime)"
        }
    } else {
        Exit-WithError "No Python processes running after deployment"
    }
    
    # Test health endpoint with retries
    $healthCheckPassed = $false
    for ($i = 1; $i -le $HealthCheckRetries; $i++) {
        Write-Status "Testing health endpoint (attempt $i/$HealthCheckRetries)..."
        try {
            $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing -TimeoutSec 10
            if ($response.StatusCode -eq 200) {
                Write-Status "Health endpoint is responding" "SUCCESS"
                $healthData = $response.Content | ConvertFrom-Json
                Write-Status "Service: $($healthData.service)"
                Write-Status "Status: $($healthData.status)"
                Write-Status "Copying Active: $($healthData.copying_active)"
                Write-Status "Active Connections: $($healthData.active_connections)"
                $healthCheckPassed = $true
                break
            } else {
                Write-Status "Health endpoint returned status code: $($response.StatusCode)" "WARNING"
            }
        } catch {
            Write-Status "Health endpoint check failed: $($_.Exception.Message)" "WARNING"
            if ($i -lt $HealthCheckRetries) {
                Write-Status "Retrying in 5 seconds..."
                Start-Sleep -Seconds 5
            }
        }
    }
    
    if (-not $healthCheckPassed) {
        # Check if port 8000 is in use
        try {
            $port8000 = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
            if ($port8000) {
                Write-Status "Port 8000 is in use but health endpoint not responding" "WARNING"
                $port8000 | ForEach-Object { 
                    Write-Status "  Process ID using port: $($_.OwningProcess)"
                }
            } else {
                Write-Status "Port 8000 is not in use - application may not have started" "ERROR"
            }
        } catch {
            Write-Status "Could not check port 8000 status: $($_.Exception.Message)" "WARNING"
        }
        Exit-WithError "Health check failed after $HealthCheckRetries attempts"
    }
    
    Write-Status "=== Deployment completed successfully ===" "SUCCESS"
    
} catch {
    Exit-WithError "Unexpected error during deployment: $($_.Exception.Message)"
}