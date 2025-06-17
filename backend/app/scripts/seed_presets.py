# backend/app/scripts/seed_presets.py

"""
Script to define default crawl presets for the PMOVES Agent Platform.

This script generates a list of preset configurations that can be used to
populate the 'crawl_presets' table in the database. Each preset is defined
as a dictionary conforming to the structure expected by the preset management API
(closely related to the CrawlPresetCreate Pydantic model).

The `strategy_definition` field within each preset is a JSON-like dictionary
that will be parsed by `crawl4ai_docker_fetcher.py` to configure the crawl4ai library.
"""

from typing import List, Dict, Any, Optional
from uuid import uuid4 # For created_by if needed, though likely system/admin

# Placeholder for actual user ID if presets are user-specific by default
# For system-wide presets, this might be a specific admin user ID or None
DEFAULT_CREATED_BY_USER_ID = str(uuid4()) # Example: Generate a consistent UUID for all system presets

def get_default_presets() -> List[Dict[str, Any]]:
    """
    Returns a list of default crawl preset definitions.
    """
    presets: List[Dict[str, Any]] = []

    # 1. Quick Product Scrape
    presets.append({
        "preset_name": "quick_product_scrape",
        "description": "Fast, rule-based extraction for structured e-commerce pages using CSS selectors. Optimized for speed by using text-only mode.",
        "version": 1,
        "crawl_tool": "crawl4ai",
        "strategy_definition": {
            "params": {
                "extraction_strategy": {
                    "type": "JsonCssExtractionStrategy",
                    "params": {
                        "schema_name": "product_details_css",
                        "schema": {
                            "name": "LaptopScraper",
                            "baseSelector": "div.product-card",
                            "fields": [
                                {"name": "name", "selector": "h3.product-name", "type": "text"},
                                {"name": "price", "selector": ".price", "type": "text"},
                                {"name": "url", "selector": "a.product-link", "type": "attribute", "attribute": "href"}
                            ]
                        }
                    }
                }
            },
            "browser_config": {
                "text_mode": True
            },
            "run_config": {
                "only_text": True
            }
        },
        "target_capability": "data_extraction",
        "tags": ["ecommerce", "scraping", "css", "fast"],
        "created_by": DEFAULT_CREATED_BY_USER_ID
    })

    # 2. Deep Dive News Articles
    presets.append({
        "preset_name": "deep_dive_news_articles",
        "description": "Performs an in-depth crawl of a news website, prioritizing relevant and recent-looking articles using keyword scoring and URL patterns. Start the crawl on the primary domain of the news site. Relies on include_external=false to stay on domain.",
        "version": 1,
        "crawl_tool": "crawl4ai",
        "strategy_definition": {
            "strategy": "BestFirstCrawlingStrategy",
            "params": {
                "max_depth": 3,
                "max_pages": 100,
                "include_external": False,
                "url_scorer": {
                    "type": "KeywordRelevanceScorer",
                    "params": {
                        "keywords": ["news", "article", "breaking", "story", "report", "latest", "update"],
                        "weight": 0.8
                    }
                },
                "filter_chain": {
                    "filters": [
                        {
                            "type": "URLPatternFilter",
                            "params": {
                                "patterns": [
                                    "*/article[s]?/*", "*/story/*", "*/post/*",
                                    "*/news/*", "*/blog/*", "*/*[0-9]{4}/*[0-9]{1,2}/*[0-9]{1,2}/*"
                                ],
                                "case_sensitive": False
                            }
                        },
                        {
                            "type": "ContentTypeFilter",
                            "params": {
                                "allowed_types": ["text/html", "application/xhtml+xml"]
                            }
                        }
                    ]
                }
            },
            "browser_config": {
                "headless": True,
                "user_agent": "NewsAnalysisBot/1.0"
            },
            "run_config": {
                "page_timeout": 90000
            }
        },
        "target_capability": "web_research",
        "tags": ["news", "deep_crawl", "content_discovery", "best_first"],
        "created_by": DEFAULT_CREATED_BY_USER_ID
    })

    # 3. Tech News Summary (LLM Extraction)
    presets.append({
        "preset_name": "tech_news_summary",
        "description": "Extracts a structured summary (title, summary, key topics) from a single tech article page using an LLM. Requires LLM configuration.",
        "version": 1,
        "crawl_tool": "crawl4ai",
        "strategy_definition": {
            "params": {
                "extraction_strategy": {
                    "type": "LLMExtractionStrategy",
                    "params": {
                        "schema_name": "tech_article_summary",
                        "schema": {
                            "type": "object",
                            "properties": {
                                "title": {"type": "string", "description": "The main title of the tech article."},
                                "summary": {"type": "string", "description": "A concise summary of the article's content."},
                                "key_topics": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "A list of key topics or technologies discussed."
                                }
                            },
                            "required": ["title", "summary", "key_topics"]
                        },
                        "instruction": "Extract the title, a concise summary (2-3 sentences), and a list of key topics from the provided tech article content. Focus on the core information and technological aspects."
                    }
                }
            },
            "llm_config": {
                "provider": "ollama", # Or your preferred default
                "model": "llama3:latest", # Or your preferred default
                "api_base": "http://localhost:11434", # Adjust if different
                "temperature": 0.5,
                "max_tokens": 1000
            },
            "browser_config": {
                "headless": True,
                "user_agent": "TechSummaryBot/1.0"
            },
            "run_config": {
                "page_timeout": 60000
            }
        },
        "target_capability": "summarization",
        "tags": ["llm", "extraction", "summary", "tech"],
        "created_by": DEFAULT_CREATED_BY_USER_ID
    })

    # 4. Documentation Site BFS Crawl
    presets.append({
        "preset_name": "documentation_site_bfs_crawl",
        "description": "Crawls a documentation website using BFS, focusing on relevant sections like 'docs', 'help', 'guide', etc., and filtering for HTML content. Stays on the initial domain.",
        "version": 1,
        "crawl_tool": "crawl4ai",
        "strategy_definition": {
            "strategy": "BFSDeepCrawlStrategy",
            "params": {
                "max_depth": 2,
                "max_pages": 50,
                "include_external": False,
                "filter_chain": {
                    "filters": [
                        {
                            "type": "URLPatternFilter",
                            "params": {
                                "patterns": ["*docs*", "*help*", "*documentation*", "*support*", "*/faq/*", "*/guide/*"],
                                "case_sensitive": False
                            }
                        },
                        {
                            "type": "ContentTypeFilter",
                            "params": {
                                "allowed_types": ["text/html", "application/xhtml+xml"]
                            }
                        }
                    ]
                }
            },
            "browser_config": {
                "headless": True
            },
            "run_config": {
                "page_timeout": 75000
            }
        },
        "target_capability": "web_research",
        "tags": ["documentation", "bfs", "deep_crawl", "info_retrieval"],
        "created_by": DEFAULT_CREATED_BY_USER_ID
    })

    # 5. Targeted Blog Crawl (BestFirst)
    presets.append({
        "preset_name": "targeted_blog_crawl",
        "description": "Crawls a specific blog using BestFirst strategy, prioritizing relevant posts using keywords and URL patterns. Start the crawl on the blog's main domain. Stays on the initial domain.",
        "version": 1,
        "crawl_tool": "crawl4ai",
        "strategy_definition": {
            "strategy": "BestFirstCrawlingStrategy",
            "params": {
                "max_depth": 3,
                "max_pages": 100,
                "include_external": False,
                "url_scorer": {
                    "type": "KeywordRelevanceScorer",
                    "params": {
                        "keywords": ["ai", "llm", "development", "tech", "software", "engineering", "programming", "tutorial", "guide"],
                        "weight": 0.75
                    }
                },
                "filter_chain": {
                    "filters": [
                        {
                            "type": "URLPatternFilter",
                            "params": {
                                "patterns": ["*/blog/*", "*/post/*", "*/article[s]?/*", "*/*[0-9]{4}/*[0-9]{1,2}/*"],
                                "case_sensitive": False
                            }
                        },
                        {
                            "type": "ContentTypeFilter",
                            "params": {
                                "allowed_types": ["text/html", "application/xhtml+xml"]
                            }
                        }
                    ]
                }
            },
            "browser_config": {"headless": True, "user_agent": "BlogCrawler/1.0"},
            "run_config": {"page_timeout": 75000}
        },
        "target_capability": "web_research",
        "tags": ["blog", "best_first", "deep_crawl", "keywords"],
        "created_by": DEFAULT_CREATED_BY_USER_ID
    })

    # 6. Generic LLM Extraction
    presets.append({
        "preset_name": "llm_generic_extraction",
        "description": "A generic preset for extracting structured data from a single page using an LLM. Provides a basic schema and instruction; most effective when schema/instruction are refined or provided at runtime by an agent.",
        "version": 1,
        "crawl_tool": "crawl4ai",
        "strategy_definition": {
            "params": {
                "extraction_strategy": {
                    "type": "LLMExtractionStrategy",
                    "params": {
                        "schema_name": "generic_llm_extract",
                        "schema": {
                            "type": "object",
                            "properties": {
                                "title": {"type": "string", "description": "The main title of the page."},
                                "summary": {"type": "string", "description": "A brief summary of the page content."},
                                "extracted_data": {"type": "object", "additionalProperties": True, "description": "Key data points extracted based on instruction."}
                            },
                            "required": ["title", "summary"]
                        },
                        "instruction": "Extract the title, a concise summary, and any other key information from the provided page content based on the user's specific goal for this crawl."
                    }
                }
            },
            "llm_config": {
                "provider": "ollama",
                "model": "llama3:latest",
                "api_base": "http://localhost:11434",
                "temperature": 0.5,
                "max_tokens": 1500
            },
            "browser_config": {
                "user_agent": "GenericLLMExtractorBot/1.0",
                "text_mode": False
            },
            "run_config": {
                "page_timeout": 60000,
                "only_text": False
            }
        },
        "target_capability": "data_extraction",
        "tags": ["llm", "extraction", "generic"],
        "created_by": DEFAULT_CREATED_BY_USER_ID
    })

    # Presets will be defined here in subsequent steps.
    # Example structure for a preset:
    # {
    #     "preset_name": "example_preset",
    #     "description": "A brief description of what this preset does.",
    #     "version": 1,
    #     "crawl_tool": "crawl4ai",
    #     "strategy_definition": {
    #         # Detailed JSON configuration for crawl4ai
    #     },
    #     "target_capability": "web_research", # Optional
    #     "tags": ["example", "research"], # Optional
    #     "created_by": DEFAULT_CREATED_BY_USER_ID # Or specific user ID
    # }

    return presets

if __name__ == "__main__":
    default_presets = get_default_presets()
    if default_presets:
        print(f"Successfully generated {len(default_presets)} default presets.")
        # In a real scenario, you might pretty-print this,
        # save to a JSON file, or use it to call an API to insert presets.
        import json
        print(json.dumps(default_presets, indent=2, default=str))
    # --- How to use these presets ---
    # The `default_presets` list generated by `get_default_presets()` contains
    # preset configurations ready to be inserted into the database.
    #
    # Option 1: Manual Seeding via API
    #   1. Run this script: `python backend/app/scripts/seed_presets.py > presets_to_seed.json`
    #   2. Manually (or programmatically) take each object from the `presets_to_seed.json`
    #      array and POST it to the `/api/presets` endpoint of your running application.
    #      Ensure you have the necessary authentication if required by the API.
    #      The `created_by` field uses a default UUID; you might want to adjust this
    #      to a specific admin user ID from your `auth.users` table.
    #
    # Option 2: Extend this script for Automated Seeding
    #   - You could modify this script to import the Supabase client (or use httpx to call
    #     the FastAPI `/api/presets` endpoint).
    #   - Loop through `default_presets` and insert each one.
    #   - This would require careful handling of environment variables for Supabase/API
    #     credentials and the API base URL.
    #
    # Option 3: Integrate into a broader seeding mechanism
    #   - If your project has a dedicated seeding process (e.g., using Alembic for
    #     database migrations and seeding), this script's `get_default_presets()`
    #     function can be imported and used by that process.
    #
    # Remember to ensure the `crawl_presets` table schema (from `backend/app/db/schema.sql`)
    # has been applied to your database before attempting to insert these presets.
    else:
        print("No default presets generated yet.")
