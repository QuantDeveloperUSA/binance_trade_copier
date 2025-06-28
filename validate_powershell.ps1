# PowerShell Syntax Validation Script
# This script checks if our deploy.ps1 script has valid PowerShell syntax

param(
    [string]$ScriptPath = "deploy.ps1"
)

Write-Host "=== PowerShell Script Validation ==="
Write-Host "Validating script: $ScriptPath"
Write-Host ""

if (-not (Test-Path $ScriptPath)) {
    Write-Host "❌ Script file not found: $ScriptPath" -ForegroundColor Red
    exit 1
}

try {
    # Parse the PowerShell script to check for syntax errors
    $errors = $null
    $tokens = $null
    $ast = [System.Management.Automation.Language.Parser]::ParseFile($ScriptPath, [ref]$tokens, [ref]$errors)
    
    if ($errors.Count -eq 0) {
        Write-Host "✅ PowerShell syntax validation passed" -ForegroundColor Green
        Write-Host "   - No syntax errors found" -ForegroundColor Green
        Write-Host "   - Script can be parsed successfully" -ForegroundColor Green
        
        # Check for common PowerShell best practices
        $content = Get-Content $ScriptPath -Raw
        $warnings = @()
        
        # Check for parameter validation
        if ($content -match 'param\s*\(') {
            Write-Host "   - ✅ Uses parameters" -ForegroundColor Green
        } else {
            $warnings += "Consider using parameters for flexibility"
        }
        
        # Check for error handling
        if ($content -match 'try\s*\{.*?catch\s*\{') {
            Write-Host "   - ✅ Uses try-catch error handling" -ForegroundColor Green
        } elseif ($content -match 'try\s*\{' -and $content -match 'catch\s*\{') {
            Write-Host "   - ✅ Uses try-catch error handling" -ForegroundColor Green
        } else {
            $warnings += "Consider adding try-catch blocks for better error handling"
        }
        
        # Check for Write-Host output
        if ($content -match 'Write-Host') {
            Write-Host "   - ✅ Uses Write-Host for output" -ForegroundColor Green
        }
        
        # Check for exit codes
        if ($content -match 'exit\s+\d+') {
            Write-Host "   - ✅ Uses exit codes" -ForegroundColor Green
        }
        
        if ($warnings.Count -gt 0) {
            Write-Host "   - Recommendations:" -ForegroundColor Yellow
            foreach ($warning in $warnings) {
                Write-Host "     * $warning" -ForegroundColor Yellow
            }
        }
        
    } else {
        Write-Host "❌ PowerShell syntax validation failed" -ForegroundColor Red
        Write-Host "Errors found:" -ForegroundColor Red
        foreach ($error in $errors) {
            Write-Host "  Line $($error.Extent.StartLineNumber): $($error.Message)" -ForegroundColor Red
        }
        exit 1
    }
    
} catch {
    Write-Host "❌ Failed to validate PowerShell script" -ForegroundColor Red
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "=== Validation Complete ===" -ForegroundColor Cyan