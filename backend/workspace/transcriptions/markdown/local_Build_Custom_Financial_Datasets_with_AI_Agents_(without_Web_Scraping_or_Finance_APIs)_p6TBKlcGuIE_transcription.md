# Transcription for Video: [p6TBKlcGuIE](https://www.youtube.com/watch?v=p6TBKlcGuIE)

| Timestamp Link | Video ID | Seg ID | Start | End | Text |
|---|---|---|---|---|---|
| [00:00](https://www.youtube.com/watch?v=p6TBKlcGuIE&t=0s) | p6TBKlcGuIE | 0 | 00:00 | 00:03 | This tutorial will show you how to build an AI agent workflow |
| [00:03](https://www.youtube.com/watch?v=p6TBKlcGuIE&t=3s) | p6TBKlcGuIE | 1 | 00:03 | 00:06 | that creates custom financial data sets from scratch. |
| [00:06](https://www.youtube.com/watch?v=p6TBKlcGuIE&t=6s) | p6TBKlcGuIE | 2 | 00:06 | 00:10 | These data sets will be at the company level, meaning we'll input a stock ticker symbol |
| [00:10](https://www.youtube.com/watch?v=p6TBKlcGuIE&t=10s) | p6TBKlcGuIE | 3 | 00:10 | 00:15 | and get company data as outputs. We won't be relying on traditional web scraping, |
| [00:15](https://www.youtube.com/watch?v=p6TBKlcGuIE&t=15s) | p6TBKlcGuIE | 4 | 00:15 | 00:18 | and we're not connecting to any financial or stock data APIs. |
| [00:19](https://www.youtube.com/watch?v=p6TBKlcGuIE&t=19s) | p6TBKlcGuIE | 5 | 00:19 | 00:24 | Instead, we'll use AI agents to scour the internet for relevant data points, |
| [00:24](https://www.youtube.com/watch?v=p6TBKlcGuIE&t=24s) | p6TBKlcGuIE | 6 | 00:24 | 00:29 | including variables that aren't typically structured or found in any off-the-shelf data set. |
| [00:29](https://www.youtube.com/watch?v=p6TBKlcGuIE&t=29s) | p6TBKlcGuIE | 7 | 00:29 | 00:34 | In this tutorial, we'll assemble data on frequency of executive departures, |
| [00:34](https://www.youtube.com/watch?v=p6TBKlcGuIE&t=34s) | p6TBKlcGuIE | 8 | 00:34 | 00:39 | board compositions, employee sentiment, and the number of open job postings. |
| [00:39](https://www.youtube.com/watch?v=p6TBKlcGuIE&t=39s) | p6TBKlcGuIE | 9 | 00:39 | 00:43 | But these are just a few examples. What actually matters is up to you. |
| [00:43](https://www.youtube.com/watch?v=p6TBKlcGuIE&t=43s) | p6TBKlcGuIE | 10 | 00:43 | 00:47 | The signals you choose should reflect what you believe moves stock prices. |
| [00:47](https://www.youtube.com/watch?v=p6TBKlcGuIE&t=47s) | p6TBKlcGuIE | 11 | 00:47 | 00:51 | This workflow gives you the flexibility to collect the kinds of inputs that are |
| [00:51](https://www.youtube.com/watch?v=p6TBKlcGuIE&t=51s) | p6TBKlcGuIE | 12 | 00:51 | 00:54 | most relevant to your own investment thesis or prediction model. |
| [00:54](https://www.youtube.com/watch?v=p6TBKlcGuIE&t=54s) | p6TBKlcGuIE | 13 | 00:54 | 00:58 | You're no longer limited to the data found in SEC filings |
| [00:58](https://www.youtube.com/watch?v=p6TBKlcGuIE&t=58s) | p6TBKlcGuIE | 14 | 00:58 | 01:01 | or whatever extras your go-to financial API provides. |
| [01:01](https://www.youtube.com/watch?v=p6TBKlcGuIE&t=61s) | p6TBKlcGuIE | 15 | 01:01 | 01:03 | This is public information. |
| [01:03](https://www.youtube.com/watch?v=p6TBKlcGuIE&t=63s) | p6TBKlcGuIE | 16 | 01:03 | 01:06 | It just hasn't been systematized or widely distributed, |
| [01:06](https://www.youtube.com/watch?v=p6TBKlcGuIE&t=66s) | p6TBKlcGuIE | 17 | 01:06 | 01:09 | which is exactly why it has the potential to give you an edge. |
| [01:10](https://www.youtube.com/watch?v=p6TBKlcGuIE&t=70s) | p6TBKlcGuIE | 18 | 01:10 | 01:13 | The AI tech stack we'll be using for this agentic workflow |
| [01:13](https://www.youtube.com/watch?v=p6TBKlcGuIE&t=73s) | p6TBKlcGuIE | 19 | 01:13 | 01:15 | is incredibly simple to set up. |
| [01:15](https://www.youtube.com/watch?v=p6TBKlcGuIE&t=75s) | p6TBKlcGuIE | 20 | 01:15 | 01:18 | We'll be using OpenAI's Agents SDK library in Python, |
| [01:19](https://www.youtube.com/watch?v=p6TBKlcGuIE&t=79s) | p6TBKlcGuIE | 21 | 01:19 | 01:20 | which is an easy-to-implement framework |
| [01:20](https://www.youtube.com/watch?v=p6TBKlcGuIE&t=80s) | p6TBKlcGuIE | 22 | 01:20 | 01:23 | designed for building agentic AI applications. |
| [01:23](https://www.youtube.com/watch?v=p6TBKlcGuIE&t=83s) | p6TBKlcGuIE | 23 | 01:23 | 01:25 | If you're new to agentic orchestration |
| [01:25](https://www.youtube.com/watch?v=p6TBKlcGuIE&t=85s) | p6TBKlcGuIE | 24 | 01:25 | 01:28 | or you're just looking to create a custom dataset quickly, |
| [01:28](https://www.youtube.com/watch?v=p6TBKlcGuIE&t=88s) | p6TBKlcGuIE | 25 | 01:28 | 01:31 | this library is about as easy as it gets. |
| [01:31](https://www.youtube.com/watch?v=p6TBKlcGuIE&t=91s) | p6TBKlcGuIE | 26 | 01:31 | 01:36 | Next, we'll be using the Pydantic library to define and enforce structured outputs. |
| [01:36](https://www.youtube.com/watch?v=p6TBKlcGuIE&t=96s) | p6TBKlcGuIE | 27 | 01:36 | 01:39 | This makes it easy to create a dataset with clearly typed fields, |
| [01:39](https://www.youtube.com/watch?v=p6TBKlcGuIE&t=99s) | p6TBKlcGuIE | 28 | 01:39 | 01:45 | including integers, floats, and strings, so there's minimal post-processing required. |
| [01:45](https://www.youtube.com/watch?v=p6TBKlcGuIE&t=105s) | p6TBKlcGuIE | 29 | 01:45 | 01:48 | You can go straight into analysis whether that's using an LLM, |
| [01:48](https://www.youtube.com/watch?v=p6TBKlcGuIE&t=108s) | p6TBKlcGuIE | 30 | 01:48 | 01:54 | training a machine learning model, or just exploring the data in a notebook. |
| [01:54](https://www.youtube.com/watch?v=p6TBKlcGuIE&t=114s) | p6TBKlcGuIE | 31 | 01:54 | 01:56 | To create this ready-for-analysis dataset, |
| [01:56](https://www.youtube.com/watch?v=p6TBKlcGuIE&t=116s) | p6TBKlcGuIE | 32 | 01:56 | 02:02 | set, we'll also be using the Pandas library to export all of the data into a data frame. |
| [02:02](https://www.youtube.com/watch?v=p6TBKlcGuIE&t=122s) | p6TBKlcGuIE | 33 | 02:02 | 02:08 | In terms of AI models and web search capabilities, you can connect the OpenAI Agents SDK framework |
| [02:08](https://www.youtube.com/watch?v=p6TBKlcGuIE&t=128s) | p6TBKlcGuIE | 34 | 02:08 | 02:13 | to more than just chat GPT models, but I'll be implementing two options, first, using |
| [02:13](https://www.youtube.com/watch?v=p6TBKlcGuIE&t=133s) | p6TBKlcGuIE | 35 | 02:13 | 02:19 | GPT-40 Mini from OpenAI, and second, using Perplexity's Sonar Pro model. |
| [02:19](https://www.youtube.com/watch?v=p6TBKlcGuIE&t=139s) | p6TBKlcGuIE | 36 | 02:19 | 02:25 | As you'll see, the pricing for web connectivity for the OpenAI models is extremely expensive, |
| [02:25](https://www.youtube.com/watch?v=p6TBKlcGuIE&t=145s) | p6TBKlcGuIE | 37 | 02:25 | 02:28 | while Perplexity's Sonar models are much more affordable. |
| [02:28](https://www.youtube.com/watch?v=p6TBKlcGuIE&t=148s) | p6TBKlcGuIE | 38 | 02:28 | 02:34 | Per 1,000 web searches, OpenAI charges over 2.5 times as much for 4.0 Mini than Perplexity |
| [02:34](https://www.youtube.com/watch?v=p6TBKlcGuIE&t=154s) | p6TBKlcGuIE | 39 | 02:34 | 02:38 | charges for Sonar Pro, assuming a medium context size. |
| [02:38](https://www.youtube.com/watch?v=p6TBKlcGuIE&t=158s) | p6TBKlcGuIE | 40 | 02:38 | 02:42 | So it's much more cost-effective to use a Perplexity model. |
| [02:42](https://www.youtube.com/watch?v=p6TBKlcGuIE&t=162s) | p6TBKlcGuIE | 41 | 02:42 | 02:48 | This tutorial assumes you've already created an API key for either OpenAI or Perplexity, |
| [02:48](https://www.youtube.com/watch?v=p6TBKlcGuIE&t=168s) | p6TBKlcGuIE | 42 | 02:48 | 02:52 | but if you're new to working with either of these APIs, check the video description. |
| [02:52](https://www.youtube.com/watch?v=p6TBKlcGuIE&t=172s) | p6TBKlcGuIE | 43 | 02:52 | 02:56 | I've linked to earlier walkthroughs where I cover how to set that up. |
| [02:56](https://www.youtube.com/watch?v=p6TBKlcGuIE&t=176s) | p6TBKlcGuIE | 44 | 02:56 | 03:01 | Start by creating a new virtual or conda environment and installing the following libraries. |
| [03:01](https://www.youtube.com/watch?v=p6TBKlcGuIE&t=181s) | p6TBKlcGuIE | 45 | 03:01 | 03:05 | OpenAI Agents, Pydantic, and Pandas. |
| [03:05](https://www.youtube.com/watch?v=p6TBKlcGuIE&t=185s) | p6TBKlcGuIE | 46 | 03:05 | 03:09 | You can do this by copying the code on the screen into your terminal or command prompt. |
| [03:09](https://www.youtube.com/watch?v=p6TBKlcGuIE&t=189s) | p6TBKlcGuIE | 47 | 03:09 | 03:13 | Next, shift to a code editor and create a Jupyter notebook. |
| [03:13](https://www.youtube.com/watch?v=p6TBKlcGuIE&t=193s) | p6TBKlcGuIE | 48 | 03:13 | 03:18 | We'll first cover how to build the custom financial dataset using an OpenAI model. |
| [03:18](https://www.youtube.com/watch?v=p6TBKlcGuIE&t=198s) | p6TBKlcGuIE | 49 | 03:18 | 03:22 | You'll need to import the OS library and set your OpenAI API key. |
| [03:22](https://www.youtube.com/watch?v=p6TBKlcGuIE&t=202s) | p6TBKlcGuIE | 50 | 03:22 | 03:27 | Begin by importing the Agent, Runner, and Web Search tool modules from the Agents library. |
| [03:27](https://www.youtube.com/watch?v=p6TBKlcGuIE&t=207s) | p6TBKlcGuIE | 51 | 03:27 | 03:33 | the list module from typing, base model from Pydantic, and import pandas as pd. |
| [03:33](https://www.youtube.com/watch?v=p6TBKlcGuIE&t=213s) | p6TBKlcGuIE | 52 | 03:33 | 03:37 | We'll create a base model using Pydantic to define the structure and data types we want |
| [03:37](https://www.youtube.com/watch?v=p6TBKlcGuIE&t=217s) | p6TBKlcGuIE | 53 | 03:37 | 03:39 | the agent to return. |
| [03:39](https://www.youtube.com/watch?v=p6TBKlcGuIE&t=219s) | p6TBKlcGuIE | 54 | 03:39 | 03:45 | This ensures the output is clean, validated, and ready to use without extra formatting. |
| [03:45](https://www.youtube.com/watch?v=p6TBKlcGuIE&t=225s) | p6TBKlcGuIE | 55 | 03:45 | 03:49 | We'll give each field a short variable name and specify its data type. |
| [03:49](https://www.youtube.com/watch?v=p6TBKlcGuIE&t=229s) | p6TBKlcGuIE | 56 | 03:49 | 03:53 | These fields represent the specific pieces of information we'll ask the AI agent to find |
| [03:53](https://www.youtube.com/watch?v=p6TBKlcGuIE&t=233s) | p6TBKlcGuIE | 57 | 03:53 | 03:55 | in the prompt. |
| [03:55](https://www.youtube.com/watch?v=p6TBKlcGuIE&t=235s) | p6TBKlcGuIE | 58 | 03:55 | 03:58 | Next, we'll quickly instantiate the web search tool. |
| [03:58](https://www.youtube.com/watch?v=p6TBKlcGuIE&t=238s) | p6TBKlcGuIE | 59 | 03:58 | 04:03 | This will be passed into the agent under the tools argument so it can query the internet |
| [04:03](https://www.youtube.com/watch?v=p6TBKlcGuIE&t=243s) | p6TBKlcGuIE | 60 | 04:03 | 04:05 | for each data point we're asking for. |
| [04:05](https://www.youtube.com/watch?v=p6TBKlcGuIE&t=245s) | p6TBKlcGuIE | 61 | 04:05 | 04:08 | Then we define the agent itself. |
| [04:08](https://www.youtube.com/watch?v=p6TBKlcGuIE&t=248s) | p6TBKlcGuIE | 62 | 04:08 | 04:12 | We give it a name, a set of clear instructions outlining exactly what information it should |
| [04:12](https://www.youtube.com/watch?v=p6TBKlcGuIE&t=252s) | p6TBKlcGuIE | 63 | 04:12 | 04:18 | collect for a given company ticker, and we specify the output format using the company |
| [04:18](https://www.youtube.com/watch?v=p6TBKlcGuIE&t=258s) | p6TBKlcGuIE | 64 | 04:18 | 04:21 | info model we created earlier. |
| [04:21](https://www.youtube.com/watch?v=p6TBKlcGuIE&t=261s) | p6TBKlcGuIE | 65 | 04:21 | 04:27 | The tool we pass in enables real-time web access, and we set the model to GPT-40-mini, |
| [04:27](https://www.youtube.com/watch?v=p6TBKlcGuIE&t=267s) | p6TBKlcGuIE | 66 | 04:27 | 04:30 | which handles both the reasoning and the extraction. |
| [04:30](https://www.youtube.com/watch?v=p6TBKlcGuIE&t=270s) | p6TBKlcGuIE | 67 | 04:30 | 04:34 | At this point, we're basically ready to run the AI agent. |
| [04:34](https://www.youtube.com/watch?v=p6TBKlcGuIE&t=274s) | p6TBKlcGuIE | 68 | 04:34 | 04:39 | We'll loop over a list of tickers, pass each one to the agent, and collect the structured |
| [04:39](https://www.youtube.com/watch?v=p6TBKlcGuIE&t=279s) | p6TBKlcGuIE | 69 | 04:39 | 04:40 | results. |
| [04:40](https://www.youtube.com/watch?v=p6TBKlcGuIE&t=280s) | p6TBKlcGuIE | 70 | 04:40 | 04:45 | Each response gets added to a list, and once the loop is complete, we convert that list |
| [04:45](https://www.youtube.com/watch?v=p6TBKlcGuIE&t=285s) | p6TBKlcGuIE | 71 | 04:45 | 04:47 | into a Pandas dataframe. |
| [04:47](https://www.youtube.com/watch?v=p6TBKlcGuIE&t=287s) | p6TBKlcGuIE | 72 | 04:47 | 04:52 | We'll use the runner.run function, which takes in the agent we created, and the ticker as |
| [04:52](https://www.youtube.com/watch?v=p6TBKlcGuIE&t=292s) | p6TBKlcGuIE | 73 | 04:52 | 04:53 | arguments. |
| [04:53](https://www.youtube.com/watch?v=p6TBKlcGuIE&t=293s) | p6TBKlcGuIE | 74 | 04:53 | 04:57 | Since we're running this in a Jupyter notebook, we'll use await, because the run function |
| [04:57](https://www.youtube.com/watch?v=p6TBKlcGuIE&t=297s) | p6TBKlcGuIE | 75 | 04:57 | 04:59 | is asynchronous. |
| [04:59](https://www.youtube.com/watch?v=p6TBKlcGuIE&t=299s) | p6TBKlcGuIE | 76 | 04:59 | 05:03 | It needs to complete its task before moving on to the next ticker. |
| [05:03](https://www.youtube.com/watch?v=p6TBKlcGuIE&t=303s) | p6TBKlcGuIE | 77 | 05:03 | 05:07 | You can then check out your filled-in dataset and scan for accuracy, which I'll go into |
| [05:07](https://www.youtube.com/watch?v=p6TBKlcGuIE&t=307s) | p6TBKlcGuIE | 78 | 05:07 | 05:12 | more when we compare it side-by-side with the Perplexity results. |
| [05:12](https://www.youtube.com/watch?v=p6TBKlcGuIE&t=312s) | p6TBKlcGuIE | 79 | 05:12 | 05:16 | Now we'll walk through how to run this same financial data collection workflow using Perplexity |
| [05:16](https://www.youtube.com/watch?v=p6TBKlcGuIE&t=316s) | p6TBKlcGuIE | 80 | 05:16 | 05:18 | Sonar. |
| [05:18](https://www.youtube.com/watch?v=p6TBKlcGuIE&t=318s) | p6TBKlcGuIE | 81 | 05:18 | 05:22 | Start by setting your Perplexity Sonar API key. |
| [05:22](https://www.youtube.com/watch?v=p6TBKlcGuIE&t=322s) | p6TBKlcGuIE | 82 | 05:22 | 05:27 | From the OpenAI agent's SDK, we'll use the same general structure, but we'll import the |
| [05:27](https://www.youtube.com/watch?v=p6TBKlcGuIE&t=327s) | p6TBKlcGuIE | 83 | 05:27 | 05:34 | async-openai and openai-chat-completions model modules this time, since we're connecting to an |
| [05:34](https://www.youtube.com/watch?v=p6TBKlcGuIE&t=334s) | p6TBKlcGuIE | 84 | 05:34 | 05:40 | external model provider. The rest of the libraries, Pydantic, Pandas, and the agent tooling stay the |
| [05:40](https://www.youtube.com/watch?v=p6TBKlcGuIE&t=340s) | p6TBKlcGuIE | 85 | 05:40 | 05:47 | same. The key difference is how we define the model inside the agent. First, we create a |
| [05:47](https://www.youtube.com/watch?v=p6TBKlcGuIE&t=347s) | p6TBKlcGuIE | 86 | 05:47 | 05:56 | perplexity client using async-openai with the base URL set to api.perplexity.ai. Then, when we pass |
| [05:56](https://www.youtube.com/watch?v=p6TBKlcGuIE&t=356s) | p6TBKlcGuIE | 87 | 05:56 | 06:02 | that client into the agent, we set the model to SonarPro. This connects the agent directly |
| [06:02](https://www.youtube.com/watch?v=p6TBKlcGuIE&t=362s) | p6TBKlcGuIE | 88 | 06:02 | 06:08 | to Perplexity's language model, while keeping the workflow and schema exactly the same. |
| [06:08](https://www.youtube.com/watch?v=p6TBKlcGuIE&t=368s) | p6TBKlcGuIE | 89 | 06:08 | 06:13 | We then run the tickers through the runner.run function as we did when working with the OpenAI |
| [06:13](https://www.youtube.com/watch?v=p6TBKlcGuIE&t=373s) | p6TBKlcGuIE | 90 | 06:13 | 06:20 | model. Okay, so how accurate are each of these models at doing web data collection? |
| [06:20](https://www.youtube.com/watch?v=p6TBKlcGuIE&t=380s) | p6TBKlcGuIE | 91 | 06:20 | 06:25 | So the Perplexity dataset is on the top, and the OpenAI dataset is now on the bottom. Both |
| [06:25](https://www.youtube.com/watch?v=p6TBKlcGuIE&t=385s) | p6TBKlcGuIE | 92 | 06:25 | 06:30 | Both did a good job at collecting some of the more obvious and easy to find variables, |
| [06:30](https://www.youtube.com/watch?v=p6TBKlcGuIE&t=390s) | p6TBKlcGuIE | 93 | 06:30 | 06:36 | such as sector, founding year, number of employees, and current CEO tenure in years, with slight |
| [06:36](https://www.youtube.com/watch?v=p6TBKlcGuIE&t=396s) | p6TBKlcGuIE | 94 | 06:36 | 06:38 | variations. |
| [06:38](https://www.youtube.com/watch?v=p6TBKlcGuIE&t=398s) | p6TBKlcGuIE | 95 | 06:38 | 06:43 | Compared to Perplexity, the GPT-40 mini model totally bombed on the number of CEOs each |
| [06:43](https://www.youtube.com/watch?v=p6TBKlcGuIE&t=403s) | p6TBKlcGuIE | 96 | 06:43 | 06:49 | company has had since 2010 and the job positions currently available, although Perplexity also |
| [06:49](https://www.youtube.com/watch?v=p6TBKlcGuIE&t=409s) | p6TBKlcGuIE | 97 | 06:49 | 06:53 | undercounted some as well for this variable too. |
| [06:53](https://www.youtube.com/watch?v=p6TBKlcGuIE&t=413s) | p6TBKlcGuIE | 98 | 06:53 | 06:58 | Look, this is by no means an exhaustive check of accuracy, since I only spot-checked a few |
| [06:58](https://www.youtube.com/watch?v=p6TBKlcGuIE&t=418s) | p6TBKlcGuIE | 99 | 06:58 | 07:03 | random values, but it seems like Perplexity Sonar did a much better job while costing |
| [07:03](https://www.youtube.com/watch?v=p6TBKlcGuIE&t=423s) | p6TBKlcGuIE | 100 | 07:03 | 07:06 | substantially less than OpenAI. |
| [07:06](https://www.youtube.com/watch?v=p6TBKlcGuIE&t=426s) | p6TBKlcGuIE | 101 | 07:06 | 07:11 | You can improve accuracy by stating the current date and giving the LLM a specific time reference |
| [07:11](https://www.youtube.com/watch?v=p6TBKlcGuIE&t=431s) | p6TBKlcGuIE | 102 | 07:11 | 07:13 | period in the prompt. |
| [07:13](https://www.youtube.com/watch?v=p6TBKlcGuIE&t=433s) | p6TBKlcGuIE | 103 | 07:13 | 07:18 | You'll also need a way to externally validate some of these values to build enough confidence |
| [07:18](https://www.youtube.com/watch?v=p6TBKlcGuIE&t=438s) | p6TBKlcGuIE | 104 | 07:18 | 07:21 | to use a dataset like this in production. |
| [07:21](https://www.youtube.com/watch?v=p6TBKlcGuIE&t=441s) | p6TBKlcGuIE | 105 | 07:21 | 07:26 | The reality is, we're in a moment where this kind of data gathering approach is transitioning |
| [07:26](https://www.youtube.com/watch?v=p6TBKlcGuIE&t=446s) | p6TBKlcGuIE | 106 | 07:26 | 07:30 | from being spotty and unreliable to highly accurate. |
| [07:30](https://www.youtube.com/watch?v=p6TBKlcGuIE&t=450s) | p6TBKlcGuIE | 107 | 07:30 | 07:35 | That makes now the most valuable time to experiment, whether it's through better prompting or |
| [07:35](https://www.youtube.com/watch?v=p6TBKlcGuIE&t=455s) | p6TBKlcGuIE | 108 | 07:35 | 07:39 | by guiding the AI toward more relevant sources. |
| [07:39](https://www.youtube.com/watch?v=p6TBKlcGuIE&t=459s) | p6TBKlcGuIE | 109 | 07:39 | 07:43 | The biggest gains will come before this method becomes fully optimized and priced into the |
| [07:43](https://www.youtube.com/watch?v=p6TBKlcGuIE&t=463s) | p6TBKlcGuIE | 110 | 07:43 | 07:45 | market. |
| [07:45](https://www.youtube.com/watch?v=p6TBKlcGuIE&t=465s) | p6TBKlcGuIE | 111 | 07:45 | 07:49 | The code can be accessed from the video description below, and if you found this useful, make |
| [07:49](https://www.youtube.com/watch?v=p6TBKlcGuIE&t=469s) | p6TBKlcGuIE | 112 | 07:49 | 07:54 | Make sure to like, comment, and subscribe to the DeepCharts channel for more tutorials |
| [07:54](https://www.youtube.com/watch?v=p6TBKlcGuIE&t=474s) | p6TBKlcGuIE | 113 | 07:54 | 07:59 | on how to leverage the latest AI methods and models for quant finance and other domains. |
