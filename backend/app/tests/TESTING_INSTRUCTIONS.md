# Testing Instructions

This folder contains scripts to help you run your test files individually or all at once, and save the results to a markdown file for easy review.

---

## 0. Activate your Python environment

Before running any tests, activate your virtual environment:

```powershell
.venv\Scripts\activate
```

---

## 1. Run All Tests and Save Results (PowerShell)

```powershell
# In this folder, run:
pwsh ./run_all_individual_tests.ps1
```
- This will run each test file one by one and save the output to `test_results.md` in markdown format.

---

## 2. Run a Single Test (PowerShell)

```powershell
# Just print the result:
pwsh ./run_individual_test.ps1 test_crawl4ai_fetcher_deep_strategies.py

# Save the result to a markdown file:
pwsh ./run_individual_test.ps1 test_crawl4ai_fetcher_deep_strategies.py my_results.md
```

---

## 3. Run Each Test File Individually and Save to Markdown (PowerShell)

Activate your environment first, then run each command below to append results to `test_results.md`:

```powershell
.venv\Scripts\activate

pwsh ./run_individual_test.ps1 test_crawl4ai_fetcher_extraction_strategies.py test_results.md
pwsh ./run_individual_test.ps1 test_crawl4ai_fetcher_general_options.py test_results.md
pwsh ./run_individual_test.ps1 test_crawl4ai_fetcher_llmconfig.py test_results.md
pwsh ./run_individual_test.ps1 test_crawl4ai_fetcher_markdown_config.py test_results.md
pwsh ./run_individual_test.ps1 test_fetch_history_saving.py test_results.md
pwsh ./run_individual_test.ps1 test_search_config.py test_results.md
```

---

## 4. Run Each Test File Individually and Print to Terminal (PowerShell)

Activate your environment first, then run each command below to print results to the terminal only:

```powershell
.venv\Scripts\activate
pwsh ./run_individual_test.ps1 test_crawl4ai_fetcher_deep_strategies.py
pwsh ./run_individual_test.ps1 test_crawl4ai_fetcher_extraction_strategies.py
pwsh ./run_individual_test.ps1 test_crawl4ai_fetcher_general_options.py
pwsh ./run_individual_test.ps1 test_crawl4ai_fetcher_llmconfig.py
pwsh ./run_individual_test.ps1 test_crawl4ai_fetcher_markdown_config.py
pwsh ./run_individual_test.ps1 test_fetch_history_saving.py
pwsh ./run_individual_test.ps1 test_search_config.py
```

---

## 5. Bash Scripts (for WSL, Git Bash, or Linux/macOS)

- `run_all_individual_tests.sh` and `run_individual_test.sh` provide the same functionality for bash users.

```bash
# Run all tests and save to markdown
bash run_all_individual_tests.sh

# Run a single test and print
bash run_individual_test.sh test_crawl4ai_fetcher_deep_strategies.py

# Run a single test and save to markdown
bash run_individual_test.sh test_crawl4ai_fetcher_deep_strategies.py my_results.md
```

---

## 6. Notes
- The output markdown files will contain each test's results under a separate heading for easy review.
- You can open the markdown file in any editor or viewer that supports markdown.
- If you add new test files, update the scripts' test file lists accordingly.

---

## 7. Pytest Output Filtering (Important for Agents)

By default, all test runs use the following pytest options for concise, agent-friendly output:

- `-q` (quiet): Minimal output, only test results.
- `--tb=short`: Short tracebacks for failures.
- `--maxfail=5`: Stops after 5 failures (adjustable).

This ensures that output files (like `test_results.md`) are easy to parse and do not overwhelm context windows for agents or LLMs.

**To change this behavior:**
- Edit the `addopts` line in `pyproject.toml` under `[tool.pytest.ini_options]`.
- Or, modify the pytest command in the PowerShell or Bash scripts.

**Tip:** If you need more or less output, adjust these options as needed for your workflow or agent context limits.

--- 