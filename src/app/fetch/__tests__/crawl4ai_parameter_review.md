# Crawl4AI Parameter Review: Frontend (page.js) vs. Python Docs (parameters.md)

This document tracks discrepancies and areas for review for `crawl4ai` parameters sent from the frontend (`src/app/fetch/page.js`) compared to the `crawl4ai` Python library documentation (`docs/crawl4ai/docs/md_v2/api/parameters.md`). The "Frontend HTTP Param" column shows the current parameter name being sent by `page.js`.

The goal is to ensure the frontend sends parameters that the backend API correctly interprets and maps to the `crawl4ai` Python library's settings.

| Python Parameter Name (from parameters.md) | Current Frontend HTTP Param (`crawl4ai_...`)      | Notes / Action Needed                                                                 | Status |
| :----------------------------------------- | :------------------------------------------------ | :------------------------------------------------------------------------------------ | :----- |
| `wait_until` (CrawlerRunConfig)            | `crawl4ai_page_load_wait_condition`               | Mapped: Frontend sends as `crawl4ai_page_load_wait_condition`, backend expects `page_load_wait_condition` and maps to `wait_until`. | ✅ |
| `wait_for` (CrawlerRunConfig)              | `crawl4ai_wait_for_condition`                   | Mapped: Frontend sends as `crawl4ai_wait_for_condition`, backend expects `wait_for_element_js_condition` and maps to `wait_for`. | ✅ |
| `java_script_enabled` (BrowserConfig)      | `crawl4ai_enable_js`                            | Mapped: Frontend sends as `crawl4ai_enable_js`, backend expects `enable_javascript` and maps to `java_script_enabled`. | ✅ |
| `excluded_selector` (CrawlerRunConfig)     | `crawl4ai_excluded_elements`                    | Mapped: Frontend sends as `crawl4ai_excluded_elements`, backend expects `excluded_selector`. | ✅ |
| `only_text` (CrawlerRunConfig)             | `crawl4ai_extract_only_text_content`            | Mapped: Frontend sends as `crawl4ai_extract_only_text_content`, backend expects `extract_only_text_content` and maps to `only_text`. | ✅ |
| `js_code` (CrawlerRunConfig)               | `crawl4ai_execute_js_on_load`                   | Mapped: Frontend sends as `crawl4ai_execute_js_on_load`, backend expects `execute_javascript_on_page_load` and maps to `js_code`. | ✅ |
| `simulate_user` (CrawlerRunConfig)         | `crawl4ai_simulate_user_behavior`               | Mapped: Frontend sends as `crawl4ai_simulate_user_behavior`, backend expects `simulate_user_behavior` and maps to `simulate_user`. | ✅ |
| `magic` (CrawlerRunConfig)                 | `crawl4ai_enable_magic`                         | Mapped: Frontend sends as `crawl4ai_enable_magic`, backend expects `enable_magic_handling` and maps to `magic`. | ✅ |
| `screenshot` (CrawlerRunConfig)            | `crawl4ai_capture_screenshot`                   | Mapped: Frontend sends as `crawl4ai_capture_screenshot`, backend expects `capture_screenshot_base64` and maps to `screenshot`. | ✅ |
| `pdf` (CrawlerRunConfig)                   | `crawl4ai_generate_pdf`                         | Mapped: Frontend sends as `crawl4ai_generate_pdf`, backend expects `generate_pdf_of_page` and maps to `pdf`. | ✅ |
| `image_description_min_word_threshold` (CrawlerRunConfig) | `crawl4ai_image_alt_text_min_word_count` | Mapped: Frontend sends as `crawl4ai_image_alt_text_min_word_count`, backend expects `image_alt_text_min_word_count` and maps to `image_description_min_word_threshold`. | ✅ |
| `image_score_threshold` (CrawlerRunConfig) | `crawl4ai_image_relevance_score_threshold`    | Mapped: Frontend sends as `crawl4ai_image_relevance_score_threshold`, backend expects `image_relevance_score_threshold` and maps to `image_score_threshold`. | ✅ |
| `exclude_domains` (CrawlerRunConfig)       | `crawl4ai_custom_excluded_domains`              | Mapped: Frontend sends as `crawl4ai_custom_excluded_domains`, backend expects `custom_excluded_domains` and maps to `exclude_domains`. | ✅ |
| `check_robots_txt` (CrawlerRunConfig)      | `crawl4ai_respect_robots_txt`                   | Mapped: Frontend sends as `crawl4ai_respect_robots_txt`, backend expects `respect_robots_txt` and maps to `check_robots_txt`. | ✅ |
| `verbose` (CrawlerRunConfig)               | `crawl4ai_verbose_logging`                      | Mapped: Frontend sends as `crawl4ai_verbose_logging`, backend expects `verbose_logging` and maps to `verbose`. | ✅ |
| `log_console` (CrawlerRunConfig)           | `crawl4ai_log_page_console_output`              | Mapped: Frontend sends as `crawl4ai_log_page_console_output`, backend expects `log_page_console_output` and maps to `log_console`. | ✅ |
| `session_id` (CrawlerRunConfig)            | `crawl4ai_crawl_session_id`                     | Mapped: Frontend sends as `crawl4ai_crawl_session_id`, backend expects `crawl_session_id` and maps to `session_id`. | ✅ |
| `css_selector` (CrawlerRunConfig)          | `crawl4ai_crawl_css_selector`                   | Mapped: Frontend sends as `crawl4ai_crawl_css_selector`, backend expects `crawl_css_selector` and maps to `css_selector`. | ✅ |
| `cookies` (BrowserConfig)                  | `crawl4ai_browser_cookies`                      | Mapped: Frontend sends as `crawl4ai_browser_cookies` (JSON string), backend expects `browser_cookies` and parses as JSON. | ✅ |
| `headers` (BrowserConfig)                  | `crawl4ai_browser_headers`                      | Mapped: Frontend sends as `crawl4ai_browser_headers` (JSON string), backend expects `browser_headers` and parses as JSON. | ✅ |

**General Notes:**

* **Booleans:** Frontend sends as "true"/"false" strings; backend uses `to_bool()` to parse.
* **Numbers:** Frontend sends as strings; backend uses `to_int()`/`to_float()` to parse.
* **Prefix Convention:** The backend expects parameters without the `crawl4ai_` prefix, but the FastAPI endpoint in `main.py` maps the prefixed query params to the expected backend names.
* **Backend API Contract:** The mapping is robust and systematic; all parameters in the table are handled as expected.

---

**Task 10 Status:**
- This review is now complete and tracked here. For any new parameters or changes, follow this systematic review process and update this file accordingly.
- Reference this file in the agent plan and in code reviews for future alignment. 