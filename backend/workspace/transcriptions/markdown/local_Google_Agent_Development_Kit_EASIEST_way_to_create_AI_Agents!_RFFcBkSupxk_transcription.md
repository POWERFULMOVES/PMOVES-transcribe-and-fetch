# Transcription for Video: [RFFcBkSupxk](https://www.youtube.com/watch?v=RFFcBkSupxk)

| Timestamp Link | Video ID | Seg ID | Start | End | Text |
|---|---|---|---|---|---|
| [00:00](https://www.youtube.com/watch?v=RFFcBkSupxk&t=0s) | RFFcBkSupxk | 0 | 00:00 | 00:04 | Agent Development Kit from Google. It's one of the easiest way to create AI agents, |
| [00:05](https://www.youtube.com/watch?v=RFFcBkSupxk&t=5s) | RFFcBkSupxk | 1 | 00:05 | 00:09 | evaluate those agents and deploy those agents. It has a built-in user interface, |
| [00:09](https://www.youtube.com/watch?v=RFFcBkSupxk&t=9s) | RFFcBkSupxk | 2 | 00:09 | 00:13 | API server. Even if you're an absolute beginner, you should be able to get started with |
| [00:13](https://www.youtube.com/watch?v=RFFcBkSupxk&t=13s) | RFFcBkSupxk | 3 | 00:13 | 00:19 | creating AI agents. This is what I built and it's running locally on my computer. I'm just asking, |
| [00:19](https://www.youtube.com/watch?v=RFFcBkSupxk&t=19s) | RFFcBkSupxk | 4 | 00:19 | 00:23 | what is the stock price of Apple? Now, based on that, it's going to run those tools, |
| [00:24](https://www.youtube.com/watch?v=RFFcBkSupxk&t=24s) | RFFcBkSupxk | 5 | 00:24 | 00:29 | get relevant information. You can see clearly the call between those agents and the tools, |
| [00:29](https://www.youtube.com/watch?v=RFFcBkSupxk&t=29s) | RFFcBkSupxk | 6 | 00:29 | 00:36 | all the messages included and finally you get the answer here. The stock price of Apple is 206. |
| [00:36](https://www.youtube.com/watch?v=RFFcBkSupxk&t=36s) | RFFcBkSupxk | 7 | 00:36 | 00:42 | It also has built-in state, artifacts, sessions and eval. I'm going to take you through step by |
| [00:42](https://www.youtube.com/watch?v=RFFcBkSupxk&t=42s) | RFFcBkSupxk | 8 | 00:42 | 00:46 | step how you can build this completely locally on your computer. That's exactly what we're going to |
| [00:46](https://www.youtube.com/watch?v=RFFcBkSupxk&t=46s) | RFFcBkSupxk | 9 | 00:46 | 00:54 | see today. Let's get started. It's a multi-agent system without the complexity. Build AI agents |
| [00:54](https://www.youtube.com/watch?v=RFFcBkSupxk&t=54s) | RFFcBkSupxk | 10 | 00:54 | 01:00 | that think like humans, create systems that work while you sleep and deploy anywhere with just one |
| [01:00](https://www.youtube.com/watch?v=RFFcBkSupxk&t=60s) | RFFcBkSupxk | 11 | 01:00 | 01:06 | command this is even simpler than other frameworks such as auto gen lang grof and crew ai you are |
| [01:06](https://www.youtube.com/watch?v=RFFcBkSupxk&t=66s) | RFFcBkSupxk | 12 | 01:06 | 01:12 | able to build in minutes with just few lines of code you can use multiple models also you got |
| [01:12](https://www.youtube.com/watch?v=RFFcBkSupxk&t=72s) | RFFcBkSupxk | 13 | 01:12 | 01:18 | full transparency with visual debugging and evaluation three simple steps install adk define |
| [01:18](https://www.youtube.com/watch?v=RFFcBkSupxk&t=78s) | RFFcBkSupxk | 14 | 01:18 | 01:23 | your agent and deploy anywhere i'm going to take you through step by step how you can create a |
| [01:23](https://www.youtube.com/watch?v=RFFcBkSupxk&t=83s) | RFFcBkSupxk | 15 | 01:23 | 01:29 | basic agent basic agent with tool agent with state multi-tool agent structured output agent and call |
| [01:29](https://www.youtube.com/watch?v=RFFcBkSupxk&t=89s) | RFFcBkSupxk | 16 | 01:29 | 01:33 | back agent i'll provide all the code in the description below for you to copy and run it |
| [01:33](https://www.youtube.com/watch?v=RFFcBkSupxk&t=93s) | RFFcBkSupxk | 17 | 01:33 | 01:38 | yourself but before that i regularly create videos in regards to artificial intelligence on my |
| [01:38](https://www.youtube.com/watch?v=RFFcBkSupxk&t=98s) | RFFcBkSupxk | 18 | 01:38 | 01:41 | youtube channel so do subscribe and click the bell icon to stay tuned make sure you click the like |
| [01:41](https://www.youtube.com/watch?v=RFFcBkSupxk&t=101s) | RFFcBkSupxk | 19 | 01:41 | 01:47 | button so this video can be helpful for many others like you so first step pip install google |
| [01:47](https://www.youtube.com/watch?v=RFFcBkSupxk&t=107s) | RFFcBkSupxk | 20 | 01:47 | 01:53 | adk and y finance so we are going to create a custom tool called yahoo finance and add that |
| [01:53](https://www.youtube.com/watch?v=RFFcBkSupxk&t=113s) | RFFcBkSupxk | 21 | 01:53 | 02:00 | tool to AI agent then offer that click enter now adk create I'm going to create |
| [02:00](https://www.youtube.com/watch?v=RFFcBkSupxk&t=120s) | RFFcBkSupxk | 22 | 02:00 | 02:03 | an app and then click enter this will automatically create the required files |
| [02:03](https://www.youtube.com/watch?v=RFFcBkSupxk&t=123s) | RFFcBkSupxk | 23 | 02:03 | 02:08 | so I'm going to use Gemini 2.0 flash choosing number one I'm going to use |
| [02:08](https://www.youtube.com/watch?v=RFFcBkSupxk&t=128s) | RFFcBkSupxk | 24 | 02:08 | 02:13 | Google AI that's the easiest option so choosing one now I can add my API key |
| [02:13](https://www.youtube.com/watch?v=RFFcBkSupxk&t=133s) | RFFcBkSupxk | 25 | 02:13 | 02:17 | which you can generate from AI studio.google.com slash API key so once |
| [02:17](https://www.youtube.com/watch?v=RFFcBkSupxk&t=137s) | RFFcBkSupxk | 26 | 02:17 | 02:22 | after you generate that enter that here now if you see you got three different |
| [02:22](https://www.youtube.com/watch?v=RFFcBkSupxk&t=142s) | RFFcBkSupxk | 27 | 02:22 | 02:28 | files created one is agent init and dot env env contains your environment variables you can see |
| [02:28](https://www.youtube.com/watch?v=RFFcBkSupxk&t=148s) | RFFcBkSupxk | 28 | 02:28 | 02:35 | that here agent.py will have this basic agent setup and the init file will contain this code |
| [02:35](https://www.youtube.com/watch?v=RFFcBkSupxk&t=155s) | RFFcBkSupxk | 29 | 02:35 | 02:42 | so for now we are going to go into agent.py file and improve it from here so first we are going to |
| [02:42](https://www.youtube.com/watch?v=RFFcBkSupxk&t=162s) | RFFcBkSupxk | 30 | 02:42 | 02:49 | create basic agent so same as before from google adk agents import agent then after that i'm going |
| [02:49](https://www.youtube.com/watch?v=RFFcBkSupxk&t=169s) | RFFcBkSupxk | 31 | 02:49 | 02:54 | create a basic agent with agent class and all this information it's just the |
| [02:54](https://www.youtube.com/watch?v=RFFcBkSupxk&t=174s) | RFFcBkSupxk | 32 | 02:54 | 02:59 | basic agent which is same as the agent which is automatically generated so it's |
| [02:59](https://www.youtube.com/watch?v=RFFcBkSupxk&t=179s) | RFFcBkSupxk | 33 | 02:59 | 03:03 | a simple agent that answers question so you can see name you can change the |
| [03:03](https://www.youtube.com/watch?v=RFFcBkSupxk&t=183s) | RFFcBkSupxk | 34 | 03:03 | 03:06 | model if you want and then instruction so now after this if you want to run |
| [03:06](https://www.youtube.com/watch?v=RFFcBkSupxk&t=186s) | RFFcBkSupxk | 35 | 03:06 | 03:11 | this I'm going to create a variable the root agent and assign the basic agent to |
| [03:11](https://www.youtube.com/watch?v=RFFcBkSupxk&t=191s) | RFFcBkSupxk | 36 | 03:11 | 03:16 | root agent so by default you need to set this up you need to have a root agent so |
| [03:16](https://www.youtube.com/watch?v=RFFcBkSupxk&t=196s) | RFFcBkSupxk | 37 | 03:16 | 03:19 | this is going to be run first and this is the overall code and we have |
| [03:19](https://www.youtube.com/watch?v=RFFcBkSupxk&t=199s) | RFFcBkSupxk | 38 | 03:19 | 03:24 | successfully created an AI agent now I'm going to run this code in your terminal |
| [03:24](https://www.youtube.com/watch?v=RFFcBkSupxk&t=204s) | RFFcBkSupxk | 39 | 03:24 | 03:30 | adk run app.py this will automatically create the required logs and here's a |
| [03:30](https://www.youtube.com/watch?v=RFFcBkSupxk&t=210s) | RFFcBkSupxk | 40 | 03:30 | 03:35 | user now I can ask any question tell me about Google and it's going to answer me |
| [03:35](https://www.youtube.com/watch?v=RFFcBkSupxk&t=215s) | RFFcBkSupxk | 41 | 03:35 | 03:41 | the response from the basic agent so this is for us to test the app adk run |
| [03:41](https://www.youtube.com/watch?v=RFFcBkSupxk&t=221s) | RFFcBkSupxk | 42 | 03:41 | 03:46 | app and I'm going to exit this we also have multiple options if you go to adk |
| [03:46](https://www.youtube.com/watch?v=RFFcBkSupxk&t=226s) | RFFcBkSupxk | 43 | 03:46 | 03:53 | help you have API server to create the new app which I've just shown we just |
| [03:53](https://www.youtube.com/watch?v=RFFcBkSupxk&t=233s) | RFFcBkSupxk | 44 | 03:53 | 03:58 | did adk run we also have other options such as web for testing this AI agent in |
| [03:58](https://www.youtube.com/watch?v=RFFcBkSupxk&t=238s) | RFFcBkSupxk | 45 | 03:58 | 04:04 | a web interface so I'm going to show you adk web and then click enter now you can |
| [04:04](https://www.youtube.com/watch?v=RFFcBkSupxk&t=244s) | RFFcBkSupxk | 46 | 04:04 | 04:08 | clearly see it's running the web application in this URL so I'm going to |
| [04:08](https://www.youtube.com/watch?v=RFFcBkSupxk&t=248s) | RFFcBkSupxk | 47 | 04:08 | 04:14 | open this URL and here's the URL where you can choose your agent and now I can |
| [04:14](https://www.youtube.com/watch?v=RFFcBkSupxk&t=254s) | RFFcBkSupxk | 48 | 04:14 | 04:18 | ask the same question tell me about app and after that it's going to respond |
| [04:18](https://www.youtube.com/watch?v=RFFcBkSupxk&t=258s) | RFFcBkSupxk | 49 | 04:18 | 04:22 | here you can also see the conversation here and the responses from the basic |
| [04:22](https://www.youtube.com/watch?v=RFFcBkSupxk&t=262s) | RFFcBkSupxk | 50 | 04:22 | 04:28 | agent I can even ask further question what was my previous question just to |
| [04:28](https://www.youtube.com/watch?v=RFFcBkSupxk&t=268s) | RFFcBkSupxk | 51 | 04:28 | 04:34 | see if it knows the context and I can clearly see it's all integrated well so |
| [04:34](https://www.youtube.com/watch?v=RFFcBkSupxk&t=274s) | RFFcBkSupxk | 52 | 04:34 | 04:37 | So you can see request response at the top here. |
| [04:37](https://www.youtube.com/watch?v=RFFcBkSupxk&t=277s) | RFFcBkSupxk | 53 | 04:37 | 04:39 | This is just for our debugging purpose. |
| [04:39](https://www.youtube.com/watch?v=RFFcBkSupxk&t=279s) | RFFcBkSupxk | 54 | 04:39 | 04:41 | You can also see a session ID. |
| [04:41](https://www.youtube.com/watch?v=RFFcBkSupxk&t=281s) | RFFcBkSupxk | 55 | 04:41 | 04:52 | Each session ID consists of our user messages, such as our question, answer from the agent, list of tool calls, and also it saves the state for this session. |
| [04:53](https://www.youtube.com/watch?v=RFFcBkSupxk&t=293s) | RFFcBkSupxk | 56 | 04:53 | 04:55 | So you can see the state here, also artifacts. |
| [04:55](https://www.youtube.com/watch?v=RFFcBkSupxk&t=295s) | RFFcBkSupxk | 57 | 04:55 | 04:58 | You can also create evaluation set. |
| [04:58](https://www.youtube.com/watch?v=RFFcBkSupxk&t=298s) | RFFcBkSupxk | 58 | 04:58 | 05:03 | For now, we are going to focus on the events where you got the first question and also the second question. |
| [05:03](https://www.youtube.com/watch?v=RFFcBkSupxk&t=303s) | RFFcBkSupxk | 59 | 05:03 | 05:06 | So now we have completed the first step of creating the basic agent. |
| [05:07](https://www.youtube.com/watch?v=RFFcBkSupxk&t=307s) | RFFcBkSupxk | 60 | 05:07 | 05:08 | Now let's create a tool. |
| [05:08](https://www.youtube.com/watch?v=RFFcBkSupxk&t=308s) | RFFcBkSupxk | 61 | 05:08 | 05:09 | So this is the whole setup. |
| [05:09](https://www.youtube.com/watch?v=RFFcBkSupxk&t=309s) | RFFcBkSupxk | 62 | 05:09 | 05:13 | We have a stock agent which has access to the stock info tool. |
| [05:13](https://www.youtube.com/watch?v=RFFcBkSupxk&t=313s) | RFFcBkSupxk | 63 | 05:13 | 05:16 | And the agent is going to use that tool and give us the response. |
| [05:17](https://www.youtube.com/watch?v=RFFcBkSupxk&t=317s) | RFFcBkSupxk | 64 | 05:17 | 05:19 | So I'm going to keep this basic agent just for our reference. |
| [05:19](https://www.youtube.com/watch?v=RFFcBkSupxk&t=319s) | RFFcBkSupxk | 65 | 05:19 | 05:22 | Then coming to basic agent with tool. |
| [05:22](https://www.youtube.com/watch?v=RFFcBkSupxk&t=322s) | RFFcBkSupxk | 66 | 05:22 | 05:26 | So just importing the agent, importing Yahoo Finance as YF. |
| [05:27](https://www.youtube.com/watch?v=RFFcBkSupxk&t=327s) | RFFcBkSupxk | 67 | 05:27 | 05:29 | Then creating a function called get stock price, |
| [05:29](https://www.youtube.com/watch?v=RFFcBkSupxk&t=329s) | RFFcBkSupxk | 68 | 05:29 | 05:33 | which will automatically return the stock price based on the ticker symbol. |
| [05:33](https://www.youtube.com/watch?v=RFFcBkSupxk&t=333s) | RFFcBkSupxk | 69 | 05:33 | 05:39 | If it's Apple, it's AAPL and that will be passed here and you get the stock price. |
| [05:39](https://www.youtube.com/watch?v=RFFcBkSupxk&t=339s) | RFFcBkSupxk | 70 | 05:39 | 05:43 | So it's just a simple function and that will be used as a tool for the agent. |
| [05:43](https://www.youtube.com/watch?v=RFFcBkSupxk&t=343s) | RFFcBkSupxk | 71 | 05:43 | 05:48 | So tool agent, creating the agent and naming it as tool agent with the description, |
| [05:49](https://www.youtube.com/watch?v=RFFcBkSupxk&t=349s) | RFFcBkSupxk | 72 | 05:49 | 05:52 | a simple agent that gets stock price and it's a stock price assistant. |
| [05:52](https://www.youtube.com/watch?v=RFFcBkSupxk&t=352s) | RFFcBkSupxk | 73 | 05:52 | 05:58 | It will use the ticker symbol and use the tool get stock price tool to get relevant answer. |
| [05:58](https://www.youtube.com/watch?v=RFFcBkSupxk&t=358s) | RFFcBkSupxk | 74 | 05:58 | 06:01 | So I'm going to assign this tool as the root agent. |
| [06:02](https://www.youtube.com/watch?v=RFFcBkSupxk&t=362s) | RFFcBkSupxk | 75 | 06:02 | 06:03 | So that's where it starts. |
| [06:03](https://www.youtube.com/watch?v=RFFcBkSupxk&t=363s) | RFFcBkSupxk | 76 | 06:03 | 06:08 | Literally this much amount of code to create tools and assign that to agents. |
| [06:08](https://www.youtube.com/watch?v=RFFcBkSupxk&t=368s) | RFFcBkSupxk | 77 | 06:08 | 06:10 | So this function is assigned here as tools. |
| [06:11](https://www.youtube.com/watch?v=RFFcBkSupxk&t=371s) | RFFcBkSupxk | 78 | 06:11 | 06:15 | So this tool agent can use this tool to give relevant answer. |
| [06:15](https://www.youtube.com/watch?v=RFFcBkSupxk&t=375s) | RFFcBkSupxk | 79 | 06:15 | 06:16 | So now it's ready. |
| [06:16](https://www.youtube.com/watch?v=RFFcBkSupxk&t=376s) | RFFcBkSupxk | 80 | 06:16 | 06:17 | Now I'm going to run this. |
| [06:17](https://www.youtube.com/watch?v=RFFcBkSupxk&t=377s) | RFFcBkSupxk | 81 | 06:17 | 06:20 | So previously I was running the basic agent. |
| [06:20](https://www.youtube.com/watch?v=RFFcBkSupxk&t=380s) | RFFcBkSupxk | 82 | 06:20 | 06:23 | So I pressed control C to cancel the previous setup. |
| [06:23](https://www.youtube.com/watch?v=RFFcBkSupxk&t=383s) | RFFcBkSupxk | 83 | 06:23 | 06:24 | I'm going to clear it. |
| [06:25](https://www.youtube.com/watch?v=RFFcBkSupxk&t=385s) | RFFcBkSupxk | 84 | 06:25 | 06:26 | I'm going to run that again. |
| [06:26](https://www.youtube.com/watch?v=RFFcBkSupxk&t=386s) | RFFcBkSupxk | 85 | 06:26 | 06:27 | ADK web. |
| [06:27](https://www.youtube.com/watch?v=RFFcBkSupxk&t=387s) | RFFcBkSupxk | 86 | 06:27 | 06:28 | Now again, it's restarted. |
| [06:28](https://www.youtube.com/watch?v=RFFcBkSupxk&t=388s) | RFFcBkSupxk | 87 | 06:28 | 06:33 | coming back to my previous URL and refreshing it and now let's try this |
| [06:33](https://www.youtube.com/watch?v=RFFcBkSupxk&t=393s) | RFFcBkSupxk | 88 | 06:33 | 06:39 | what is the stock price of Apple now you can see it uses the get stock price tool |
| [06:39](https://www.youtube.com/watch?v=RFFcBkSupxk&t=399s) | RFFcBkSupxk | 89 | 06:39 | 06:43 | that is the function then got the answer back based on that is giving me this |
| [06:43](https://www.youtube.com/watch?v=RFFcBkSupxk&t=403s) | RFFcBkSupxk | 90 | 06:43 | 06:49 | response this is a real-time answer stock price of Apple is 206 by default |
| [06:49](https://www.youtube.com/watch?v=RFFcBkSupxk&t=409s) | RFFcBkSupxk | 91 | 06:49 | 06:54 | these agent doesn't have real-time data by adding tools you're providing the |
| [06:54](https://www.youtube.com/watch?v=RFFcBkSupxk&t=414s) | RFFcBkSupxk | 92 | 06:54 | 06:59 | real-time response also you can see the interaction here so tool agent requesting |
| [06:59](https://www.youtube.com/watch?v=RFFcBkSupxk&t=419s) | RFFcBkSupxk | 93 | 06:59 | 07:04 | from get stock price function then it returns the response back to the tool |
| [07:04](https://www.youtube.com/watch?v=RFFcBkSupxk&t=424s) | RFFcBkSupxk | 94 | 07:04 | 07:09 | agent and finally the agent responds with the final answer the stock price of |
| [07:09](https://www.youtube.com/watch?v=RFFcBkSupxk&t=429s) | RFFcBkSupxk | 95 | 07:09 | 07:13 | Apple so it's very clear in this user interface now step number three or the |
| [07:13](https://www.youtube.com/watch?v=RFFcBkSupxk&t=433s) | RFFcBkSupxk | 96 | 07:13 | 07:18 | feature number three is agent with state so same like that we are importing agent |
| [07:18](https://www.youtube.com/watch?v=RFFcBkSupxk&t=438s) | RFFcBkSupxk | 97 | 07:18 | 07:23 | and also tool context importing Yahoo Finance having the same function get |
| [07:23](https://www.youtube.com/watch?v=RFFcBkSupxk&t=443s) | RFFcBkSupxk | 98 | 07:23 | 07:28 | stock price and stateful agent and here we are using the same get stock price |
| [07:28](https://www.youtube.com/watch?v=RFFcBkSupxk&t=448s) | RFFcBkSupxk | 99 | 07:28 | 07:34 | function but the thing what changed here is the get stock price function so we |
| [07:34](https://www.youtube.com/watch?v=RFFcBkSupxk&t=454s) | RFFcBkSupxk | 100 | 07:34 | 07:40 | are initializing a state so the state name is recent searches so it will keep |
| [07:40](https://www.youtube.com/watch?v=RFFcBkSupxk&t=460s) | RFFcBkSupxk | 101 | 07:40 | 07:45 | on storing the list of recent searches and when we request it will automatically |
| [07:45](https://www.youtube.com/watch?v=RFFcBkSupxk&t=465s) | RFFcBkSupxk | 102 | 07:45 | 07:50 | provide that answer so it's just nothing but a memory for that particular |
| [07:50](https://www.youtube.com/watch?v=RFFcBkSupxk&t=470s) | RFFcBkSupxk | 103 | 07:50 | 07:55 | conversation so let's try this in action assigning that as a root agent and I'm |
| [07:55](https://www.youtube.com/watch?v=RFFcBkSupxk&t=475s) | RFFcBkSupxk | 104 | 07:55 | 07:59 | going to restart the current setup ADK web coming back to the UI I'm going to |
| [07:59](https://www.youtube.com/watch?v=RFFcBkSupxk&t=479s) | RFFcBkSupxk | 105 | 07:59 | 08:05 | ask what is the stock price of of Tesla so I got the answer here both for Apple |
| [08:05](https://www.youtube.com/watch?v=RFFcBkSupxk&t=485s) | RFFcBkSupxk | 106 | 08:05 | 08:11 | and Tesla but at the same time if you see here in the state you got Apple and |
| [08:11](https://www.youtube.com/watch?v=RFFcBkSupxk&t=491s) | RFFcBkSupxk | 107 | 08:11 | 08:17 | Tesla getting stored in the recent searches so the AI agents can remember |
| [08:17](https://www.youtube.com/watch?v=RFFcBkSupxk&t=497s) | RFFcBkSupxk | 108 | 08:17 | 08:21 | all the searches we did stock price of Google I'm adding one more and you can |
| [08:21](https://www.youtube.com/watch?v=RFFcBkSupxk&t=501s) | RFFcBkSupxk | 109 | 08:21 | 08:26 | see it got automatically added here so the AI agent clearly remembers the list |
| [08:26](https://www.youtube.com/watch?v=RFFcBkSupxk&t=506s) | RFFcBkSupxk | 110 | 08:26 | 08:32 | of company we searched for so that's where this state comes in and in the |
| [08:32](https://www.youtube.com/watch?v=RFFcBkSupxk&t=512s) | RFFcBkSupxk | 111 | 08:32 | 08:36 | events you can see all the list of conversation if I click a new session |
| [08:36](https://www.youtube.com/watch?v=RFFcBkSupxk&t=516s) | RFFcBkSupxk | 112 | 08:36 | 08:40 | you can see the conversation is not there because it's completely new |
| [08:40](https://www.youtube.com/watch?v=RFFcBkSupxk&t=520s) | RFFcBkSupxk | 113 | 08:40 | 08:45 | conversation and for this conversation you will have a dedicated state for the |
| [08:45](https://www.youtube.com/watch?v=RFFcBkSupxk&t=525s) | RFFcBkSupxk | 114 | 08:45 | 08:49 | previous sessions you can even go to the sessions so I click this session and you |
| [08:49](https://www.youtube.com/watch?v=RFFcBkSupxk&t=529s) | RFFcBkSupxk | 115 | 08:49 | 08:53 | can see the conversation which we just had and I can even continue the |
| [08:53](https://www.youtube.com/watch?v=RFFcBkSupxk&t=533s) | RFFcBkSupxk | 116 | 08:53 | 08:58 | conversation from here so now we have successfully created agent with state |
| [08:58](https://www.youtube.com/watch?v=RFFcBkSupxk&t=538s) | RFFcBkSupxk | 117 | 08:58 | 09:04 | ability to remember specific information next feature number four multi tool |
| [09:04](https://www.youtube.com/watch?v=RFFcBkSupxk&t=544s) | RFFcBkSupxk | 118 | 09:04 | 09:09 | agent so this same as single tool agent but we are going to provide two |
| [09:09](https://www.youtube.com/watch?v=RFFcBkSupxk&t=549s) | RFFcBkSupxk | 119 | 09:09 | 09:14 | different tools one is get stock price and another one is get stock info the |
| [09:14](https://www.youtube.com/watch?v=RFFcBkSupxk&t=554s) | RFFcBkSupxk | 120 | 09:14 | 09:19 | info will be provided with company name the ticker symbol and the sector so it's |
| [09:19](https://www.youtube.com/watch?v=RFFcBkSupxk&t=559s) | RFFcBkSupxk | 121 | 09:19 | 09:24 | a multi tool agent but same as before creating the agent agent with multiple |
| [09:24](https://www.youtube.com/watch?v=RFFcBkSupxk&t=564s) | RFFcBkSupxk | 122 | 09:24 | 09:28 | tools get stock price and get stock info going to assign the multi tool agent |
| [09:28](https://www.youtube.com/watch?v=RFFcBkSupxk&t=568s) | RFFcBkSupxk | 123 | 09:28 | 09:33 | here so adding multiple tools is simple just create each function like this and |
| [09:33](https://www.youtube.com/watch?v=RFFcBkSupxk&t=573s) | RFFcBkSupxk | 124 | 09:33 | 09:38 | then provide that to function name in the tools list now I'm going to run this |
| [09:38](https://www.youtube.com/watch?v=RFFcBkSupxk&t=578s) | RFFcBkSupxk | 125 | 09:38 | 09:44 | code just restarting give me stock price of Apple and info now you can see it |
| [09:44](https://www.youtube.com/watch?v=RFFcBkSupxk&t=584s) | RFFcBkSupxk | 126 | 09:44 | 09:48 | used the get stock price function and then get stock info function so here is |
| [09:48](https://www.youtube.com/watch?v=RFFcBkSupxk&t=588s) | RFFcBkSupxk | 127 | 09:48 | 09:52 | the interaction for get stock price get stock info and the response get stock |
| [09:52](https://www.youtube.com/watch?v=RFFcBkSupxk&t=592s) | RFFcBkSupxk | 128 | 09:52 | 09:57 | price and get stock info here is the final answer so this came from the get |
| [09:57](https://www.youtube.com/watch?v=RFFcBkSupxk&t=597s) | RFFcBkSupxk | 129 | 09:57 | 10:02 | stock price function and this is technology sector this is from get stock |
| [10:02](https://www.youtube.com/watch?v=RFFcBkSupxk&t=602s) | RFFcBkSupxk | 130 | 10:02 | 10:08 | info now feature number five structured output agent so importing agents this |
| [10:08](https://www.youtube.com/watch?v=RFFcBkSupxk&t=608s) | RFFcBkSupxk | 131 | 10:08 | 10:12 | time I'm using pydantic that's where you're going to define your structured |
| [10:12](https://www.youtube.com/watch?v=RFFcBkSupxk&t=612s) | RFFcBkSupxk | 132 | 10:12 | 10:17 | output pydantic is a popular tool to get a structured response from AI agents if |
| [10:17](https://www.youtube.com/watch?v=RFFcBkSupxk&t=617s) | RFFcBkSupxk | 133 | 10:17 | 10:21 | you want to know more about pydantic I've already created another video |
| [10:21](https://www.youtube.com/watch?v=RFFcBkSupxk&t=621s) | RFFcBkSupxk | 134 | 10:21 | 10:24 | which I'll put the link in the description now I'm going to create a |
| [10:24](https://www.youtube.com/watch?v=RFFcBkSupxk&t=624s) | RFFcBkSupxk | 135 | 10:24 | 10:30 | class with stock analysis and the response I need to get a ticker symbol |
| [10:30](https://www.youtube.com/watch?v=RFFcBkSupxk&t=630s) | RFFcBkSupxk | 136 | 10:30 | 10:35 | and the recommendation whether to buy or sell so now same as before I'm going to |
| [10:35](https://www.youtube.com/watch?v=RFFcBkSupxk&t=635s) | RFFcBkSupxk | 137 | 10:35 | 10:41 | create a tool called get stock data which returns the stock price and the |
| [10:41](https://www.youtube.com/watch?v=RFFcBkSupxk&t=641s) | RFFcBkSupxk | 138 | 10:41 | 10:45 | target price next creating the structured agent for this I'm using LLM |
| [10:45](https://www.youtube.com/watch?v=RFFcBkSupxk&t=645s) | RFFcBkSupxk | 139 | 10:45 | 10:49 | agent that is the only difference so after that I'm going to create a |
| [10:49](https://www.youtube.com/watch?v=RFFcBkSupxk&t=649s) | RFFcBkSupxk | 140 | 10:49 | 10:54 | structured agent the structure agent will have the output schema that's the |
| [10:54](https://www.youtube.com/watch?v=RFFcBkSupxk&t=654s) | RFFcBkSupxk | 141 | 10:54 | 11:00 | stock analysis so it's here and the output key stock analysis so these two |
| [11:00](https://www.youtube.com/watch?v=RFFcBkSupxk&t=660s) | RFFcBkSupxk | 142 | 11:00 | 11:04 | are required and I'm assigning the structured agent to the root agent so by |
| [11:04](https://www.youtube.com/watch?v=RFFcBkSupxk&t=664s) | RFFcBkSupxk | 143 | 11:04 | 11:09 | default agents generally create a random response without any structure by |
| [11:09](https://www.youtube.com/watch?v=RFFcBkSupxk&t=669s) | RFFcBkSupxk | 144 | 11:09 | 11:15 | defining like this you are able to make the agent respond in a structured way so |
| [11:15](https://www.youtube.com/watch?v=RFFcBkSupxk&t=675s) | RFFcBkSupxk | 145 | 11:15 | 11:20 | let's try this restarting tell me about the stock of Apple so now you can see |
| [11:20](https://www.youtube.com/watch?v=RFFcBkSupxk&t=680s) | RFFcBkSupxk | 146 | 11:20 | 11:25 | we got a structured response ticker Apple and the recommendation is by this |
| [11:25](https://www.youtube.com/watch?v=RFFcBkSupxk&t=685s) | RFFcBkSupxk | 147 | 11:25 | 11:31 | brilliant even if I asked Tesla you can see the response it's consistent I'm |
| [11:31](https://www.youtube.com/watch?v=RFFcBkSupxk&t=691s) | RFFcBkSupxk | 148 | 11:31 | 11:35 | going to ask Google and I got the consistent response one thing to note is |
| [11:35](https://www.youtube.com/watch?v=RFFcBkSupxk&t=695s) | RFFcBkSupxk | 149 | 11:35 | 11:41 | that currently this structured response doesn't support tools but probably that |
| [11:41](https://www.youtube.com/watch?v=RFFcBkSupxk&t=701s) | RFFcBkSupxk | 150 | 11:41 | 11:46 | will get added soon now the final feature callback agent so same as before |
| [11:46](https://www.youtube.com/watch?v=RFFcBkSupxk&t=706s) | RFFcBkSupxk | 151 | 11:46 | 11:51 | I'm importing all these modules creating function number one get stock data |
| [11:51](https://www.youtube.com/watch?v=RFFcBkSupxk&t=711s) | RFFcBkSupxk | 152 | 11:51 | 11:56 | returns the ticker symbol and the stock price a second function before tool |
| [11:56](https://www.youtube.com/watch?v=RFFcBkSupxk&t=716s) | RFFcBkSupxk | 153 | 11:56 | 12:00 | callback so this is going to be run before running the tool next we are |
| [12:00](https://www.youtube.com/watch?v=RFFcBkSupxk&t=720s) | RFFcBkSupxk | 154 | 12:00 | 12:05 | going to create after tool after tool callback this runs after the tool is |
| [12:05](https://www.youtube.com/watch?v=RFFcBkSupxk&t=725s) | RFFcBkSupxk | 155 | 12:05 | 12:09 | being called now we are going to create a state just for our reference |
| [12:09](https://www.youtube.com/watch?v=RFFcBkSupxk&t=729s) | RFFcBkSupxk | 156 | 12:09 | 12:14 | initializing state tool usage and now time to create the callback agent |
| [12:14](https://www.youtube.com/watch?v=RFFcBkSupxk&t=734s) | RFFcBkSupxk | 157 | 12:14 | 12:20 | callback agent and here's the callback agent with tools before tool callback |
| [12:20](https://www.youtube.com/watch?v=RFFcBkSupxk&t=740s) | RFFcBkSupxk | 158 | 12:20 | 12:24 | and after tool callback so before running this get stock data function it |
| [12:24](https://www.youtube.com/watch?v=RFFcBkSupxk&t=744s) | RFFcBkSupxk | 159 | 12:24 | 12:29 | will run this tool and after running this this will be run and going to use |
| [12:29](https://www.youtube.com/watch?v=RFFcBkSupxk&t=749s) | RFFcBkSupxk | 160 | 12:29 | 12:33 | the callback agent as a root agent that's it as simple as that we created |
| [12:33](https://www.youtube.com/watch?v=RFFcBkSupxk&t=753s) | RFFcBkSupxk | 161 | 12:33 | 12:39 | three functions get stock data is a key function or the key tool and the callback |
| [12:39](https://www.youtube.com/watch?v=RFFcBkSupxk&t=759s) | RFFcBkSupxk | 162 | 12:39 | 12:43 | function is before tool callback and after tool callback and assigning that |
| [12:43](https://www.youtube.com/watch?v=RFFcBkSupxk&t=763s) | RFFcBkSupxk | 163 | 12:43 | 12:47 | here so in this way we can debug this further and get more information what |
| [12:47](https://www.youtube.com/watch?v=RFFcBkSupxk&t=767s) | RFFcBkSupxk | 164 | 12:47 | 12:51 | happened before calling this tool and what happened after calling this tool |
| [12:51](https://www.youtube.com/watch?v=RFFcBkSupxk&t=771s) | RFFcBkSupxk | 165 | 12:51 | 12:55 | now I'm going to run this coming back to the UI what is the stock price of Apple |
| [12:55](https://www.youtube.com/watch?v=RFFcBkSupxk&t=775s) | RFFcBkSupxk | 166 | 12:55 | 13:01 | and you can see here get stock data and you can see the callback function is |
| [13:01](https://www.youtube.com/watch?v=RFFcBkSupxk&t=781s) | RFFcBkSupxk | 167 | 13:01 | 13:07 | used to record this tool usage so if I say stock price of Tesla you can see the |
| [13:07](https://www.youtube.com/watch?v=RFFcBkSupxk&t=787s) | RFFcBkSupxk | 168 | 13:07 | 13:12 | get stock data became two because I've called us two times you can even trace |
| [13:12](https://www.youtube.com/watch?v=RFFcBkSupxk&t=792s) | RFFcBkSupxk | 169 | 13:12 | 13:17 | that using trace function here so clicking this you can see clear trace |
| [13:17](https://www.youtube.com/watch?v=RFFcBkSupxk&t=797s) | RFFcBkSupxk | 170 | 13:17 | 13:22 | information so the agent was run then before callback after callback and the |
| [13:22](https://www.youtube.com/watch?v=RFFcBkSupxk&t=802s) | RFFcBkSupxk | 171 | 13:22 | 13:26 | response here as simple as that next we are going to see how you can deploy your |
| [13:26](https://www.youtube.com/watch?v=RFFcBkSupxk&t=806s) | RFFcBkSupxk | 172 | 13:26 | 13:31 | agent so you got three different option one is deploying on vertex AI agent |
| [13:31](https://www.youtube.com/watch?v=RFFcBkSupxk&t=811s) | RFFcBkSupxk | 173 | 13:31 | 13:35 | engine or cloud run or custom infrastructure for this tutorial I'm |
| [13:35](https://www.youtube.com/watch?v=RFFcBkSupxk&t=815s) | RFFcBkSupxk | 174 | 13:35 | 13:39 | going to deploy in cloud run so as a basic requirement you need to log into |
| [13:39](https://www.youtube.com/watch?v=RFFcBkSupxk&t=819s) | RFFcBkSupxk | 175 | 13:39 | 13:46 | to cloud.google.com and sign up for an account then gcloud cli once after that is done in your |
| [13:46](https://www.youtube.com/watch?v=RFFcBkSupxk&t=826s) | RFFcBkSupxk | 176 | 13:46 | 13:54 | terminal gcloud auth login to log into your account next adk deploy cloud run space app and |
| [13:54](https://www.youtube.com/watch?v=RFFcBkSupxk&t=834s) | RFFcBkSupxk | 177 | 13:54 | 13:59 | then click enter this will ask where do you want to deploy the application you can choose a location |
| [13:59](https://www.youtube.com/watch?v=RFFcBkSupxk&t=839s) | RFFcBkSupxk | 178 | 13:59 | 14:03 | and finally you can see it got deployed just with one command last thing we are going to see |
| [14:03](https://www.youtube.com/watch?v=RFFcBkSupxk&t=843s) | RFFcBkSupxk | 179 | 14:03 | 14:10 | is to set up api server so again it's just one command adk api server and it'll automatically |
| [14:10](https://www.youtube.com/watch?v=RFFcBkSupxk&t=850s) | RFFcBkSupxk | 180 | 14:10 | 14:16 | start the api server and i can open this url i'm adding slash docs to get the documentation |
| [14:16](https://www.youtube.com/watch?v=RFFcBkSupxk&t=856s) | RFFcBkSupxk | 181 | 14:16 | 14:21 | on the list of api endpoints and this is brilliant there are more functions such as |
| [14:21](https://www.youtube.com/watch?v=RFFcBkSupxk&t=861s) | RFFcBkSupxk | 182 | 14:21 | 14:27 | runner setting up mcp tools within this agent and i'll be covering those in the upcoming videos so |
| [14:27](https://www.youtube.com/watch?v=RFFcBkSupxk&t=867s) | RFFcBkSupxk | 183 | 14:27 | 14:33 | stay tuned now we have successfully created a agent with all these features do let me know in |
| [14:33](https://www.youtube.com/watch?v=RFFcBkSupxk&t=873s) | RFFcBkSupxk | 184 | 14:33 | 14:38 | the comments below what do you think about this considering you already like ai agent i also |
| [14:38](https://www.youtube.com/watch?v=RFFcBkSupxk&t=878s) | RFFcBkSupxk | 185 | 14:38 | 14:43 | created another video about olama mcp agent which i highly recommend for you to watch and i will see |
| [14:43](https://www.youtube.com/watch?v=RFFcBkSupxk&t=883s) | RFFcBkSupxk | 186 | 14:43 | 14:48 | you there |
