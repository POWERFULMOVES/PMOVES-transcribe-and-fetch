Reader API
===============
  

[_![Image 69](https://jina.ai/Jina%20-%20Dark.svg)_](https://jina.ai/)

_search_[_notifications_ News](https://jina.ai/news)_box_Products_arrow\_drop\_down__![Image 70](https://jina.ai/J.svg)_Company_arrow\_drop\_down_

Reader
======

Convert a URL to LLM-friendly input, by simply adding `r.jina.ai` in front.

_code_API

* * *

_play\_arrow_Demo

* * *

_attach\_money_Pricing

[Reader API](https://jina.ai/reader/#apiform)
---------------------------------------------

Convert a URL to LLM-friendly input, by simply adding `r.jina.ai` in front.

_zoom\_out\_map_

_key_

API Key & Billing

_code_

Usage

_more\_horiz_

More

_chevron\_left__chevron\_right_

* * *

[_home_](https://jina.ai/reader)

Auto preview

[_forum_ Raise issue](https://github.com/jina-ai/reader/issues)

[_help\_outline_FAQ](https://jina.ai/reader#faq)

_api__arrow\_drop\_down_

[Status](https://status.jina.ai/)

_chevron\_left__chevron\_right_

* * *

_double\_arrow_

Use `r.jina.ai` to read a URL

This will return the main content of the page in clean, LLM-friendly text.

_keyboard\_arrow\_down_

Enter your URL

_arrow\_forward_

https://r.jina.ai/

Reader URL

_content\_copy__open\_in\_new_

_search_

Use `s.jina.ai` to search a query

This will search the web and returns URLs and contents, each in clean, LLM-friendly text.

_keyboard\_arrow\_down_

Enter your query

_arrow\_forward_

_key_

https://s.jina.ai/

Reader URL

_content\_copy__open\_in\_new_

_fact\_check_

Use `g.jina.ai` for grounding

This will call our grounding engine do fact-checking.

_science_

Experimental

_keyboard\_arrow\_down_

Enter your query

_arrow\_forward_

_key_

https://g.jina.ai/

Reader URL

[Read release note_arrow\_forward_](https://jina.ai/news/fact-checking-with-new-grounding-api-in-jina-reader)

* * *

_filter\_alt_

Common, Specific

Parameters

_arrow\_drop\_down_

Search Parameters/Headers

Add API Key for Higher Rate Limit

Enter your Jina API key to access a higher rate limit. For latest rate limit information, please refer to the table below.

[_open\_in\_new_Learn more](https://jina.ai/reader#rate-limit)

Use POST Method

Use POST instead of GET method with a URL passed in the body. Useful for building SPAs with hash-based routing.

[_open\_in\_new_Learn more](https://github.com/jina-ai/reader?tab=readme-ov-file#spas-with-hash-based-routing)

Content Format

You can control the level of detail in the response to prevent over-filtering. The default pipeline is optimized for most websites and LLM input.

Default

_arrow\_drop\_down_

Timeout

Maximum time to wait for the webpage to load. Note that this is NOT the total time for the whole end-to-end request.

Target Selector

Provide a list of CSS selector to focus on more specific parts of the page. Useful when your desired content doesn't show under the default settings.

body

.class

#id

Wait For Selector

Provide a list of CSS selector to wait for specific elements to appear before returning. Useful when your desired content doesn't show under the default settings.

body

.class

#id

Excluded Selector

Provide a list of CSS selector to remove the specified elements of the page. Useful when you want to exclude specific parts of the page like headers, footers, etc.

header

.class

#id

Remove All Images

Remove all images from the response.

Gather All Links At the End

A "Buttons & Links" section will be created at the end. This helps the downstream LLMs or web agents navigating the page or take further actions.

Gather All Images At the End

An "Images" section will be created at the end. This gives the downstream LLMs an overview of all visuals on the page, which may improve reasoning.

JSON Response

The response will be in JSON format, containing the URL, title, content, and timestamp (if available). In Search mode, it returns a list of five entries, each following the described JSON structure.

Forward Cookie

Our API server can forward your custom cookie settings when accessing the URL, which is useful for pages requiring extra authentication. Note that requests with cookies will not be cached.

[_open\_in\_new_Learn more](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Set-Cookie)

<cookie-name\>\=<cookie-value\>

<cookie-name-1\>\=<cookie-value\>; domain=<cookie-1-domain\>

Image Caption

Captions all images at the specified URL, adding 'Image \[idx\]: \[caption\]' as an alt tag for those without one. This allows downstream LLMs to interact with the images in activities such as reasoning and summarizing.

Use a Proxy Server

Our API server can utilize your proxy to access URLs, which is helpful for pages accessible only through specific proxies.

[_open\_in\_new_Learn more](https://en.wikipedia.org/wiki/Proxy_server)

Bypass the Cache

Our API server caches both Read and Search mode contents for a certain amount of time. To bypass this cache, set this header to true.

Github Flavored Markdown

Opt in/out features from GFM (Github Flavored Markdown).

Enabled

_arrow\_drop\_down_

Stream Mode

Stream mode is beneficial for large target pages, allowing more time for the page to fully render. If standard mode results in incomplete content, consider using Stream mode.

[_open\_in\_new_Learn more](https://github.com/jina-ai/reader?tab=readme-ov-file#streaming-mode)

Browser Locale

Control the browser locale to render the page. Lots of websites serve different content based on the locale.

[_open\_in\_new_Learn more](https://developer.mozilla.org/en-US/docs/Web/API/Navigator/language)

Enable iframe Extraction

Extracts and processes content from all embedded iframes within the DOM tree

Enable Shadow DOM Extraction

Traverses and extracts content from all Shadow DOM roots in the document

Local PDF/HTML file

POST

Use Reader on your local PDF and HTML file by uploading them. Only support pdf and html files. For HTML, please also specify a reference URL for better parsing related CSS/JS scripts.

_upload_

Pre-Execute Custom JavaScript

POST

Executes pre-processing JavaScript code, accepting either inline code string or remote script URL endpoint

[_open\_in\_new_Learn more](https://developer.mozilla.org/en-US/docs/Web/JavaScript)

* * *

_upload_

Request

Bash

Language

_arrow\_drop\_down_

```
curl https://r.jina.ai/https://example.com
```

_content\_copy_

* * *

_upload_

Request (javascript)

```
fetch('https://r.jina.ai/https://example.com', {
  method: 'GET',
})
```

_content\_copy_

* * *

_send_GET RESPONSE

* * *

_key_

API key

_visibility\_off__content\_copy_

* * *

Available tokens

0 _sync_

This is your unique key. Store it securely!

[What is Reader?](https://jina.ai/reader/#what_reader)
------------------------------------------------------

![Image 71](https://jina.ai/assets/explain-EQrFe5k3.svg)

Feeding web information into LLMs is an important step of grounding, yet it can be challenging. The simplest method is to scrape the webpage and feed the raw HTML. However, scraping can be complex and often blocked, and raw HTML is cluttered with extraneous elements like markups and scripts. The Reader API addresses these issues by extracting the core content from a URL and converting it into clean, LLM-friendly text, ensuring high-quality input for your agent and RAG systems.

_casino_

Enter your URL

_open\_in\_new_

Click below to fetch the source code of the page directly

* * *

Reader URL

_content\_copy__open\_in\_new_

Click below to obtain the content through our Reader API

* * *

_download_Fetch Content

* * *

Raw HTML

* * *

Reader Output

* * *

Pose a Question

_send_

Input a question and combine it with the fetched content for LLM to generate an answer

Reader for web search
---------------------

![Image 72](https://jina.ai/assets/explain3-CqNg2V0h.svg)

Reader allows you to feed your LLM with the latest information from the web. Simply prepend https://s.jina.ai/ to your query, and Reader will search the web and return the top five results with their URLs and contents, each in clean, LLM-friendly text. This way, you can always keep your LLM up-to-date, improve its factuality, and reduce hallucinations.

_casino_

Enter your query

Type a question that requires latest information or world knowledge.

* * *

Reader URL

_content\_copy__open\_in\_new_

If you use this URL in code, dont forget to encode the URL.

* * *

_contact\_support_Ask LLM w/o & w/ Search Grounding

* * *

_info_ Please note that unlike the demo shown above, in practice you do not search the original question on the web for grounding. What people often do is rewrite the original question or use multi-hop questions. They read the retrieved results and then generate additional queries to gather more information as needed before arriving at a final answer.

Reader for fact-checking
------------------------

![Image 73](https://jina.ai/assets/explain5-CKbWV5a5.svg)

The new grounding endpoint offers an end-to-end, near real-time fact-checking experience. It takes a given statement, grounds it using real-time web search results, and returns a factuality score and the exact references used. You can easily ground statements to reduce LLM hallucinations or improve the integrity of human-written content.

_bolt_

Your fact-checking statement

_send_

Reader also reads images!
-------------------------

![Image 74](https://jina.ai/assets/explain2-BYDhf_rF.svg)

Images on the webpage are automatically captioned using a vision language model in the reader and formatted as image alt tags in the output. This gives your downstream LLM just enough hints to incorporate those images into its reasoning and summarizing processes. This means you can ask questions about the images, select specific ones, or even forward their URLs to a more powerful VLM for deeper analysis!

Reader also reads PDFs!
-----------------------

![Image 75](https://jina.ai/assets/explain4-CPLfQrjf.png)

Yes, Reader natively supports PDF reading. It's compatible with most PDFs, including those with many images, and it's lightning fast! Combined with an LLM, you can easily build a ChatPDF or document analysis AI in no time.

[_open\_in\_new_Original PDF](https://www.nasa.gov/wp-content/uploads/2023/01/55583main_vision_space_exploration2.pdf)

* * *

[_open\_in\_new_Reader Result](https://r.jina.ai/https://www.nasa.gov/wp-content/uploads/2023/01/55583main_vision_space_exploration2.pdf)

The best part? It's free!
-------------------------

Reader API is available for free and offers flexible rate limit and pricing. Built on a scalable infrastructure, it offers high accessibility, concurrency, and reliability. We strive to be your preferred grounding solution for your LLMs.

Rate Limit

Rate limits are tracked in two ways: **RPM** (requests per minute) and **TPM** (tokens per minute). Limits are enforced per IP and can be reached based on whichever threshold—RPM or TPM—is hit first.

Columns

_arrow\_drop\_down_

|  | Product | API Endpoint | Description_arrow\_upward_ | w/o API Key | w/ API Key | w/ Premium API Key | Average Latency | Token Usage Counting | Allowed Request |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 
![Image 76](https://jina.ai/assets/reader-D06QTWF1.svg)



 | Reader API | `https://r.jina.ai` | Convert URL to LLM-friendly text | 20 RPM | 200 RPM | 1000 RPM | 4.6s | Count the number of tokens in the output response. | GET/POST |
| 

![Image 77](https://jina.ai/assets/reader-D06QTWF1.svg)



 | Reader API | `https://s.jina.ai` | Search the web and convert results to LLM-friendly text | _block_ | 40 RPM | 100 RPM | 8.7s | Count the number of tokens in the output response. | GET/POST |
| 

![Image 78](https://jina.ai/assets/reader-D06QTWF1.svg)



 | Reader API | `https://g.jina.ai` | Grounding a statement with web knowledge | _block_ | 10 RPM | 30 RPM | 22.7s | Count the total number of tokens in the whole process. | GET/POST |
| 

![Image 79](https://jina.ai/assets/embedding-DzEuY8_E.svg)



 | Embedding API | `https://api.jina.ai/v1/embeddings` | Convert text/images to fixed-length vectors | _block_ | 500 RPM & 1,000,000 TPM | 2,000 RPM & 5,000,000 TPM | 

_bolt_

depends on the input size

_help_



 | Count the number of tokens in the input request. | POST |
| 

![Image 80](https://jina.ai/assets/reranker-DudpN0Ck.svg)



 | Reranker API | `https://api.jina.ai/v1/rerank` | Tokenize and segment long text | _block_ | 500 RPM & 1,000,000 TPM | 2,000 RPM & 5,000,000 TPM | 

_bolt_

depends on the input size

_help_



 | Count the number of tokens in the input request. | POST |
| 

![Image 81](blob:https://jina.ai/47430e9cbced04c539a17eb39573e3a9)



 | Classifier API (Zero-shot) | `https://api.jina.ai/v1/classify` | Classify inputs using zero-shot classification | _block_ | 200 RPM & 500,000 TPM | 1,000 RPM & 3,000,000 TPM | 

_bolt_

depends on the input size





 | Tokens counted as: input\_tokens + label\_tokens | POST |
| 

![Image 82](blob:https://jina.ai/47430e9cbced04c539a17eb39573e3a9)



 | Classifier API (Few-shot) | `https://api.jina.ai/v1/classify` | Classify inputs using a trained few-shot classifier | _block_ | 20 RPM & 200,000 TPM | 60 RPM & 1,000,000 TPM | 

_bolt_

depends on the input size





 | Tokens counted as: input\_tokens | POST |
| 

![Image 83](blob:https://jina.ai/47430e9cbced04c539a17eb39573e3a9)



 | Classifier API | `https://api.jina.ai/v1/train` | Train a classifier using labeled examples | _block_ | 20 RPM & 200,000 TPM | 60 RPM & 1,000,000 TPM | 

_bolt_

depends on the input size





 | Tokens counted as: input\_tokens × num\_iters | POST |
| 

![Image 84](blob:https://jina.ai/d9cb1deb4878909b05c9cd0f15af4aac)



 | Segmenter API | `https://segment.jina.ai` | Tokenize and segment long text | 20 RPM | 200 RPM | 1,000 RPM | 0.3s | Token is not counted as usage. | GET/POST |

Don't panic! Every new API key contains one million free tokens!

_key_Get your API key

* * *

_attach\_money_Check the price table

[API Pricing](https://jina.ai/reader/#pricing)
----------------------------------------------

API pricing is based on token usage - input tokens for standard APIs and output tokens for Reader API. One API key gives you access to all search foundation products.

_![Image 85](https://jina.ai/J-active.svg)_

With Jina Search Foundation API

The easiest way to access all of our products. Top-up tokens as you go.

_key_

_content\_copy_

Enter the API key you wish to recharge

_error_

_visibility\_off_

_currency\_exchange_

Auto-recharge when tokens are low

Recommended for uninterrupted service in production. When your token balance is below the threshold you set, we will automatically recharge your credit card for the same amount as your last top-up. If you purchased multiple packs in the last top-up, we will recharge only one pack.

_check_

≤ 1M Tokens

Recharge threshold

_arrow\_drop\_down_

_speed_

Understand the rate limit

Rate limits are the maximum number of requests that can be made to an API within a minute per IP address (RPM). Find out more about the rate limits for each product and tier below.

_keyboard\_arrow\_down_

Rate Limit

Rate limits are tracked in two ways: **RPM** (requests per minute) and **TPM** (tokens per minute). Limits are enforced per IP and can be reached based on whichever threshold—RPM or TPM—is hit first.

Columns

_arrow\_drop\_down_

|  | Product | API Endpoint | Description_arrow\_upward_ | w/o API Key | w/ API Key | w/ Premium API Key | Average Latency | Token Usage Counting | Allowed Request |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 
![Image 86](https://jina.ai/assets/reader-D06QTWF1.svg)



 | Reader API | `https://r.jina.ai` | Convert URL to LLM-friendly text | 20 RPM | 200 RPM | 1000 RPM | 4.6s | Count the number of tokens in the output response. | GET/POST |
| 

![Image 87](https://jina.ai/assets/reader-D06QTWF1.svg)



 | Reader API | `https://s.jina.ai` | Search the web and convert results to LLM-friendly text | _block_ | 40 RPM | 100 RPM | 8.7s | Count the number of tokens in the output response. | GET/POST |
| 

![Image 88](https://jina.ai/assets/reader-D06QTWF1.svg)



 | Reader API | `https://g.jina.ai` | Grounding a statement with web knowledge | _block_ | 10 RPM | 30 RPM | 22.7s | Count the total number of tokens in the whole process. | GET/POST |
| 

![Image 89](https://jina.ai/assets/embedding-DzEuY8_E.svg)



 | Embedding API | `https://api.jina.ai/v1/embeddings` | Convert text/images to fixed-length vectors | _block_ | 500 RPM & 1,000,000 TPM | 2,000 RPM & 5,000,000 TPM | 

_bolt_

depends on the input size

_help_



 | Count the number of tokens in the input request. | POST |
| 

![Image 90](https://jina.ai/assets/reranker-DudpN0Ck.svg)



 | Reranker API | `https://api.jina.ai/v1/rerank` | Tokenize and segment long text | _block_ | 500 RPM & 1,000,000 TPM | 2,000 RPM & 5,000,000 TPM | 

_bolt_

depends on the input size

_help_



 | Count the number of tokens in the input request. | POST |
| 

![Image 91](blob:https://jina.ai/47430e9cbced04c539a17eb39573e3a9)



 | Classifier API (Zero-shot) | `https://api.jina.ai/v1/classify` | Classify inputs using zero-shot classification | _block_ | 200 RPM & 500,000 TPM | 1,000 RPM & 3,000,000 TPM | 

_bolt_

depends on the input size





 | Tokens counted as: input\_tokens + label\_tokens | POST |
| 

![Image 92](blob:https://jina.ai/47430e9cbced04c539a17eb39573e3a9)



 | Classifier API (Few-shot) | `https://api.jina.ai/v1/classify` | Classify inputs using a trained few-shot classifier | _block_ | 20 RPM & 200,000 TPM | 60 RPM & 1,000,000 TPM | 

_bolt_

depends on the input size





 | Tokens counted as: input\_tokens | POST |
| 

![Image 93](blob:https://jina.ai/47430e9cbced04c539a17eb39573e3a9)



 | Classifier API | `https://api.jina.ai/v1/train` | Train a classifier using labeled examples | _block_ | 20 RPM & 200,000 TPM | 60 RPM & 1,000,000 TPM | 

_bolt_

depends on the input size





 | Tokens counted as: input\_tokens × num\_iters | POST |
| 

![Image 94](blob:https://jina.ai/d9cb1deb4878909b05c9cd0f15af4aac)



 | Segmenter API | `https://segment.jina.ai` | Tokenize and segment long text | 20 RPM | 200 RPM | 1,000 RPM | 0.3s | Token is not counted as usage. | GET/POST |

_verified\_user_

Top up this API key with more tokens

Depending on your location, you may be charged in USD, EUR, or other currencies. Taxes may apply.

Toy Experiment

1 Million

Tokens valid for:

_![Image 95](https://jina.ai/assets/embedding-DzEuY8_E.svg)__![Image 96](https://jina.ai/assets/reranker-DudpN0Ck.svg)__![Image 97](https://jina.ai/assets/reader-D06QTWF1.svg)__![Image 98](blob:https://jina.ai/47430e9cbced04c539a17eb39573e3a9)__![Image 99](blob:https://jina.ai/d9cb1deb4878909b05c9cd0f15af4aac)_

Non-commercial use only (CC-BY-NC)

Free

Enjoy your new API key with free tokens, no credit card required.

Prototype Development

1 Billion

Tokens valid for:

_![Image 100](https://jina.ai/assets/embedding-DzEuY8_E.svg)__![Image 101](https://jina.ai/assets/reranker-DudpN0Ck.svg)__![Image 102](https://jina.ai/assets/reader-D06QTWF1.svg)__![Image 103](blob:https://jina.ai/47430e9cbced04c539a17eb39573e3a9)__![Image 104](blob:https://jina.ai/d9cb1deb4878909b05c9cd0f15af4aac)_

_task\_alt_ Unrestricted commercial use

$20

0.020 / 1M tokens

_add\_shopping\_cart_

Production Deployment

11 Billion

Tokens valid for:

_![Image 105](https://jina.ai/assets/embedding-DzEuY8_E.svg)__![Image 106](https://jina.ai/assets/reranker-DudpN0Ck.svg)__![Image 107](https://jina.ai/assets/reader-D06QTWF1.svg)__![Image 108](blob:https://jina.ai/47430e9cbced04c539a17eb39573e3a9)__![Image 109](blob:https://jina.ai/d9cb1deb4878909b05c9cd0f15af4aac)_

_task\_alt_ Unrestricted commercial use

_task\_alt_ Much higher rate limit

_task\_alt_ Priority customer support

_task\_alt_ Free 1-hour consultation

$200

0.018 / 1M tokens

_add\_shopping\_cart_

Please input the right API key to top up

FAQ
---

### [How to get my API key?](https://jina.ai/reader/#get-api-key)

 video\_not\_supported

### [What's the rate limit?](https://jina.ai/reader/#rate-limit)

Rate Limit

Rate limits are tracked in two ways: **RPM** (requests per minute) and **TPM** (tokens per minute). Limits are enforced per IP and can be reached based on whichever threshold—RPM or TPM—is hit first.

Columns

_arrow\_drop\_down_

|  | Product | API Endpoint | Description_arrow\_upward_ | w/o API Key | w/ API Key | w/ Premium API Key | Average Latency | Token Usage Counting | Allowed Request |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 
![Image 110](https://jina.ai/assets/reader-D06QTWF1.svg)



 | Reader API | `https://r.jina.ai` | Convert URL to LLM-friendly text | 20 RPM | 200 RPM | 1000 RPM | 4.6s | Count the number of tokens in the output response. | GET/POST |
| 

![Image 111](https://jina.ai/assets/reader-D06QTWF1.svg)



 | Reader API | `https://s.jina.ai` | Search the web and convert results to LLM-friendly text | _block_ | 40 RPM | 100 RPM | 8.7s | Count the number of tokens in the output response. | GET/POST |
| 

![Image 112](https://jina.ai/assets/reader-D06QTWF1.svg)



 | Reader API | `https://g.jina.ai` | Grounding a statement with web knowledge | _block_ | 10 RPM | 30 RPM | 22.7s | Count the total number of tokens in the whole process. | GET/POST |
| 

![Image 113](https://jina.ai/assets/embedding-DzEuY8_E.svg)



 | Embedding API | `https://api.jina.ai/v1/embeddings` | Convert text/images to fixed-length vectors | _block_ | 500 RPM & 1,000,000 TPM | 2,000 RPM & 5,000,000 TPM | 

_bolt_

depends on the input size

_help_



 | Count the number of tokens in the input request. | POST |
| 

![Image 114](https://jina.ai/assets/reranker-DudpN0Ck.svg)



 | Reranker API | `https://api.jina.ai/v1/rerank` | Tokenize and segment long text | _block_ | 500 RPM & 1,000,000 TPM | 2,000 RPM & 5,000,000 TPM | 

_bolt_

depends on the input size

_help_



 | Count the number of tokens in the input request. | POST |
| 

![Image 115](blob:https://jina.ai/47430e9cbced04c539a17eb39573e3a9)



 | Classifier API (Zero-shot) | `https://api.jina.ai/v1/classify` | Classify inputs using zero-shot classification | _block_ | 200 RPM & 500,000 TPM | 1,000 RPM & 3,000,000 TPM | 

_bolt_

depends on the input size





 | Tokens counted as: input\_tokens + label\_tokens | POST |
| 

![Image 116](blob:https://jina.ai/47430e9cbced04c539a17eb39573e3a9)



 | Classifier API (Few-shot) | `https://api.jina.ai/v1/classify` | Classify inputs using a trained few-shot classifier | _block_ | 20 RPM & 200,000 TPM | 60 RPM & 1,000,000 TPM | 

_bolt_

depends on the input size





 | Tokens counted as: input\_tokens | POST |
| 

![Image 117](blob:https://jina.ai/47430e9cbced04c539a17eb39573e3a9)



 | Classifier API | `https://api.jina.ai/v1/train` | Train a classifier using labeled examples | _block_ | 20 RPM & 200,000 TPM | 60 RPM & 1,000,000 TPM | 

_bolt_

depends on the input size





 | Tokens counted as: input\_tokens × num\_iters | POST |
| 

![Image 118](blob:https://jina.ai/d9cb1deb4878909b05c9cd0f15af4aac)



 | Segmenter API | `https://segment.jina.ai` | Tokenize and segment long text | 20 RPM | 200 RPM | 1,000 RPM | 0.3s | Token is not counted as usage. | GET/POST |

### [Do I need a commercial license?](https://jina.ai/reader/#cc-self-check)

CC BY-NC License Self-Check

* * *

_play\_arrow_

Are you using our official API or official images on Azure or AWS?

_play\_arrow_

_done_

Yes

_play\_arrow_

Are you using a paid API key or free trial key?

_play\_arrow_

_done_

Paid API key

No restrictions. Use as per your current agreement.

_play\_arrow_

_info_

Free API key

Free trial key can be only used for non-commercial purposes. Please purchase a paid package for commercial use.

_play\_arrow_

Are you using our official model images on AWS and Azure?

No restrictions. Use as per your current agreement.

_play\_arrow_

_close_

No

_play\_arrow_

Are you using these models?

jina-clip-v2

jina-embeddings-v3

jina-reranker-v2-base-multilingual

jina-colbert-v2

reader-lm-1.5b

reader-lm-0.5b

_play\_arrow_

_close_

No

No restrictions apply.

_play\_arrow_

_done_

Yes

_play\_arrow_

Is your use commercial?

_play\_arrow_

_question\_mark_

Not sure

_play\_arrow_

Are you:

_play\_arrow_

Using it for personal or hobby projects?

This is non-commercial. You can use the models freely.

_play\_arrow_

A for-profit company using it internally?

This is commercial. Contact our sales team.

[Contact sales](https://jina.ai/contact-sales)

_play\_arrow_

An educational institution using it for teaching?

This is typically non-commercial. You can use the models freely.

_play\_arrow_

A non-profit or NGO using it for your mission?

This is typically non-commercial, but check with us if unsure.

[Contact sales](https://jina.ai/contact-sales)

_play\_arrow_

Using it in a product or service you sell?

This is commercial. Contact our sales team.

[Contact sales](https://jina.ai/contact-sales)

_play\_arrow_

A government entity using it for public services?

This may be commercial. Please contact us for clarification.

[Contact sales](https://jina.ai/contact-sales)

_play\_arrow_

_close_

No

You can use the models freely.

_play\_arrow_

_done_

Yes

Contact our sales team for licensing.

[Contact sales](https://jina.ai/contact-sales)

### [Other questions](https://jina.ai/reader/#faq)

Reader-related common questions

_![Image 119](https://jina.ai/assets/reader-D06QTWF1.svg)_

What are the costs associated with using the Reader API?

_keyboard\_arrow\_down_

The Reader API is free of charge and does not require an API key. Simply prepend 'https://r.jina.ai/' to your URL.

_![Image 120](https://jina.ai/assets/reader-D06QTWF1.svg)_

How does the Reader API function?

_keyboard\_arrow\_down_

The Reader API uses a proxy to fetch any URL, rendering its content in a browser to extract high-quality main content.

_![Image 121](https://jina.ai/assets/reader-D06QTWF1.svg)_

Is the Reader API open source?

_keyboard\_arrow\_down_

Yes, the Reader API is open source and available on the Jina AI GitHub repository.

_![Image 122](https://jina.ai/assets/reader-D06QTWF1.svg)_

What is the typical latency for the Reader API?

_keyboard\_arrow\_down_

The Reader API generally processes URLs and returns content within 2 seconds, although complex or dynamic pages might require more time.

_![Image 123](https://jina.ai/assets/reader-D06QTWF1.svg)_

Why should I use the Reader API instead of scraping the page myself?

_keyboard\_arrow\_down_

Scraping can be complicated and unreliable, particularly with complex or dynamic pages. The Reader API provides a streamlined, reliable output of clean, LLM-ready text.

_![Image 124](https://jina.ai/assets/reader-D06QTWF1.svg)_

Does the Reader API support multiple languages?

_keyboard\_arrow\_down_

The Reader API returns content in the original language of the URL. It does not provide translation services.

_![Image 125](https://jina.ai/assets/reader-D06QTWF1.svg)_

What should I do if a website blocks the Reader API?

_keyboard\_arrow\_down_

If you experience blocking issues, please contact our support team for assistance and resolution.

_![Image 126](https://jina.ai/assets/reader-D06QTWF1.svg)_

Can the Reader API extract content from PDF files?

_keyboard\_arrow\_down_

Yes, the Reader API can natively extract content from PDF files.

_![Image 127](https://jina.ai/assets/reader-D06QTWF1.svg)_

Can the Reader API process media content from web pages?

_keyboard\_arrow\_down_

Currently, the Reader API does not process media content, but future enhancements will include image captioning and video summarization.

_![Image 128](https://jina.ai/assets/reader-D06QTWF1.svg)_

Is it possible to use the Reader API on local HTML files?

_keyboard\_arrow\_down_

No, the Reader API can only process content from publicly accessible URLs.

_![Image 129](https://jina.ai/assets/reader-D06QTWF1.svg)_

Does Reader API cache the content?

_keyboard\_arrow\_down_

If you request the same URL within 5 minutes, the Reader API will return the cached content.

_![Image 130](https://jina.ai/assets/reader-D06QTWF1.svg)_

Can I use the Reader API to access content behind a login?

_keyboard\_arrow\_down_

Unfortunately not.

_![Image 131](https://jina.ai/assets/reader-D06QTWF1.svg)_

Can I use the Reader API to access PDF on arXiv?

_keyboard\_arrow\_down_

Yes, you can either use the native PDF support from the Reader (https://r.jina.ai/https://arxiv.org/pdf/2310.19923v4) or use the HTML version from the arXiv (https://r.jina.ai/https://arxiv.org/html/2310.19923v4)

_![Image 132](https://jina.ai/assets/reader-D06QTWF1.svg)_

How does image caption work in Reader?

_keyboard\_arrow\_down_

Reader captions all images at the specified URL and adds \`Image \[idx\]: \[caption\]\` as an alt tag (if they initially lack one). This enables downstream LLMs to interact with the images in reasoning, summarizing etc.

_![Image 133](https://jina.ai/assets/reader-D06QTWF1.svg)_

What is the scalability of the Reader? Can I use it in production?

_keyboard\_arrow\_down_

The Reader API is designed to be highly scalable. It is auto-scaled based on the real-time traffic and the maximum concurrency requests is now around 4000. We are maintaining it actively as one of the core products of Jina AI. So feel free to use it in production.

_![Image 134](https://jina.ai/assets/reader-D06QTWF1.svg)_

What is the rate limit of the Reader API?

_keyboard\_arrow\_down_

Please find the latest rate limit information in the table below. Note that we are actively working on improving the rate limit and performance of the Reader API, the table will be updated accordingly.

[_speed_Rate limit](https://jina.ai/reader/#rate-limit)

API-related common questions

_code_

Can I use the same API key for embedding, reranking, reader, fine-tuning APIs?

_keyboard\_arrow\_down_

Yes, the same API key is valid for all search foundation products from Jina AI. This includes the embedding, reranking, reader and fine-tuning APIs, with tokens shared between the all services.

_code_

Can I monitor the token usage of my API key?

_keyboard\_arrow\_down_

Yes, token usage can be monitored in the 'Buy tokens' tab by entering your API key, allowing you to view the usage history and remaining tokens.

_code_

What should I do if I forget my API key?

_keyboard\_arrow\_down_

If you have misplaced a topped-up key and wish to retrieve it, please contact support AT jina.ai with your registered email for assistance.

[Contact](https://jina.ai/contact-sales)

_code_

Do API keys expire?

_keyboard\_arrow\_down_

No, our API keys do not have an expiration date. However, if you suspect your key has been compromised and wish to retire it or transfer its tokens to a new key, please contact our support team for assistance.

[Contact](https://jina.ai/contact-sales)

_code_

Why is the first request for some models slow?

_keyboard\_arrow\_down_

This is because our serverless architecture offloads certain models during periods of low usage. The initial request activates or 'warms up' the model, which may take a few seconds. After this initial activation, subsequent requests process much more quickly.

_code_

Is user input data used for training your models?

_keyboard\_arrow\_down_

We adhere to a strict privacy policy and do not use user input data for training our models.

Billing-related common questions

_attach\_money_

Is billing based on the number of sentences or requests?

_keyboard\_arrow\_down_

Our pricing model is based on the total number of tokens processed, allowing users the flexibility to allocate these tokens across any number of sentences, offering a cost-effective solution for diverse text analysis requirements.

_attach\_money_

Is there a free trial available for new users?

_keyboard\_arrow\_down_

We offer a welcoming free trial to new users, which includes one million tokens for use with any of our models, facilitated by an auto-generated API key. Once the free token limit is reached, users can easily purchase additional tokens for their API keys via the 'Buy tokens' tab.

_attach\_money_

Are tokens charged for failed requests?

_keyboard\_arrow\_down_

No, tokens are not deducted for failed requests.

_attach\_money_

What payment methods are accepted?

_keyboard\_arrow\_down_

Payments are processed through Stripe, supporting a variety of payment methods including credit cards, Google Pay, and PayPal for your convenience.

_attach\_money_

Is invoicing available for token purchases?

_keyboard\_arrow\_down_

Yes, an invoice will be issued to the email address associated with your Stripe account upon the purchase of tokens.

Offices

_location\_on_

Berlin, Germany (HQ)

Prinzessinnenstraße 19-20, 10969 Berlin, Germany

_location\_on_

Beijing, China

Level 5, Building 6, No.48 Haidian West St. Beijing Haidian, China

_location\_on_

Shenzhen, China

402, Floor 4, Fu'an Technology Building, Shenzhen Nanshan, China

Search Foundation

[Embeddings](https://jina.ai/embeddings)[Reranker](https://jina.ai/reranker)[Reader](https://jina.ai/reader)[Classifier](https://jina.ai/classifier)[Segmenter](https://jina.ai/segmenter)

Get Jina AI API key

[Rate Limit](https://jina.ai/contact-sales#rate-limit)[API Status](https://status.jina.ai/)

Company

[About us](https://jina.ai/about-us)[Contact sales](https://jina.ai/contact-sales)[Newsroom](https://jina.ai/news)[Intern program](https://jina.ai/internship)[Join us _open\_in\_new_](https://career.jina.ai/)[Download logo _open\_in\_new_](https://jina.ai/logo-Jina-1024.zip)

Terms

[Commercial License](https://jina.ai/COMMERCIAL-LICENSE-TERMS.pdf)[Security](https://jina.ai/legal/#security)[Terms & Conditions](https://jina.ai/legal/#terms-and-conditions)[Privacy](https://jina.ai/legal/#privacy-policy)[Manage Cookies](javascript:UC_UI.showSecondLayer();)[![Image 135](https://jina.ai/21972-312_SOC_NonCPA_Blk.svg)](https://app.eu.vanta.com/jinaai/trust/vz7f4mohp0847aho84lmva)

[](https://x.com/jinaAI_)[](https://www.linkedin.com/company/jinaai/)[](https://github.com/jina-ai)[_![Image 136](https://jina.ai/huggingface_logo.svg)_](https://huggingface.co/jinaai) [](https://discord.jina.ai/)[_email_](mailto:support@jina.ai)

_language_

English

_arrow\_drop\_down_

Jina AI GmbH © 2020-2024.