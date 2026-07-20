# Find .env file
$envFile = Join-Path $PSScriptRoot "..\.env"
if (-not (Test-Path $envFile)) {
    $envFile = Join-Path $PSScriptRoot ".env"
}
if (-not (Test-Path $envFile)) {
    $envFile = ".env"
}

if (Test-Path $envFile) {
    Write-Host "Loading environment from $envFile..." -ForegroundColor Cyan
    Get-Content $envFile | ForEach-Object {
        $line = $_.Trim()
        # Parse key=value pairs, ignoring comments and empty lines
        if ($line -and -not $line.StartsWith("#") -and $line -match "^([^=]+)=(.*)$") {
            $key = $Matches[1].Trim()
            $value = $Matches[2].Trim()
            # Strip quotes if present
            if ($value.StartsWith('"') -and $value.EndsWith('"')) {
                $value = $value.Substring(1, $value.Length - 2)
            }
            elseif ($value.StartsWith("'") -and $value.EndsWith("'")) {
                $value = $value.Substring(1, $value.Length - 2)
            }
            
            [System.Environment]::SetEnvironmentVariable($key, $value)
            Set-Item "env:$key" $value
        }
    }
} else {
    Write-Warning ".env file not found. Attempting to connect with defaults."
}

# Resolve DB settings
$dbUrl = [System.Environment]::GetEnvironmentVariable("DATABASE_URL")
if ($dbUrl) {
    # Convert sqlalchemy / python format database URL to standard postgres URI
    $dbUrl = $dbUrl -replace '^postgresql\+psycopg2://', 'postgresql://'
    Write-Host "Connecting using DATABASE_URL..." -ForegroundColor Green
    psql $dbUrl @args
} else {
    $dbHost = [System.Environment]::GetEnvironmentVariable("DB_HOST")
    if (-not $dbHost) { $dbHost = "localhost" }
    
    $dbPort = [System.Environment]::GetEnvironmentVariable("DB_PORT")
    if (-not $dbPort) { $dbPort = "5432" }
    
    $dbName = [System.Environment]::GetEnvironmentVariable("DB_NAME")
    
    $dbUser = [System.Environment]::GetEnvironmentVariable("DB_USER")
    if (-not $dbUser) { $dbUser = "postgres" }
    
    $dbPass = [System.Environment]::GetEnvironmentVariable("DB_PASSWORD")

    if ($dbPass) {
        $env:PGPASSWORD = $dbPass
    }

    Write-Host "Connecting to $dbName on ${dbHost}:${dbPort} as $dbUser..." -ForegroundColor Green
    if ($dbName) {
        psql -h $dbHost -p $dbPort -U $dbUser -d $dbName @args
    } else {
        psql -h $dbHost -p $dbPort -U $dbUser @args
    }
}
