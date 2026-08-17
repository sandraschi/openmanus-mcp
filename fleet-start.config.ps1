# Per-repo fleet start config for openmanus-mcp
# Edit ports/backend target here - start.ps1 is fleet-standard.
@{
    Name         = 'openmanus-mcp'
    BackendPort  = 10768
    FrontendPort = 10769
    HealthPath   = '/api/v1/health'
    WebRoot      = 'D:\Dev\repos\openmanus-mcp\web_sota'
    Backend = @{
        Kind          = 'uvicorn'
        UvicornTarget = 'server:app'
        SyncExtras    = @('dev')
        Env           = @{ WEB_PORT = '10768' }
    }
    Frontend = @{
        Kind           = 'vite-npm'
        PackageManager = 'npm'
        PortEnvVar     = 'VITE_PORT'
        ApiTargetEnv   = 'VITE_API_TARGET'
    }
}
