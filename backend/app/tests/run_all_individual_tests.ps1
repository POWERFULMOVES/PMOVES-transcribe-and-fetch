# Output markdown file
$outputFile = "test_results.md"

# List of test files
$testFiles = @(
    "test_crawl4ai_fetcher_deep_strategies.py"
    "test_crawl4ai_fetcher_extraction_strategies.py"
    "test_crawl4ai_fetcher_general_options.py"
    "test_crawl4ai_fetcher_llmconfig.py"
    "test_crawl4ai_fetcher_markdown_config.py"
    "test_fetch_history_saving.py"
    "test_search_config.py"
)

# Remove previous output file if exists
if (Test-Path $outputFile) { Remove-Item $outputFile }

"# Test Results" | Out-File -FilePath $outputFile -Encoding utf8

foreach ($testFile in $testFiles) {
    "`n## $testFile`n" | Tee-Object -FilePath $outputFile -Append
    '```' | Add-Content $outputFile
    pytest -q --tb=short --maxfail=5 $testFile | Tee-Object -FilePath $outputFile -Append
    '```' | Add-Content $outputFile
    Write-Host "Finished $testFile"
}

"`nAll tests complete. Results saved to $outputFile." | Add-Content $outputFile 