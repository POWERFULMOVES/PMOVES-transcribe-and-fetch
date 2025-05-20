param(
    [Parameter(Mandatory=$true)]
    [string]$TestFile,
    [string]$OutputFile
)

if (-not $TestFile) {
    Write-Host "Usage: .\run_individual_test.ps1 <test_file.py> [output.md]"
    exit 1
}

if (-not $OutputFile) {
    "`n## $TestFile`n"
    pytest -q --tb=short --maxfail=5 $TestFile
} else {
    "`n## $TestFile`n" | Tee-Object -FilePath $OutputFile -Append
    '```' | Add-Content $OutputFile
    pytest -q --tb=short --maxfail=5 $TestFile | Tee-Object -FilePath $OutputFile -Append
    '```' | Add-Content $OutputFile
    Write-Host "Finished $TestFile (output appended to $OutputFile)"
} 