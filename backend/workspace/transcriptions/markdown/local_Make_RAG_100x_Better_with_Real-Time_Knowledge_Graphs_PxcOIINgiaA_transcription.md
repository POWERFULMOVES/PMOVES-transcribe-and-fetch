# Transcription for Video: [PxcOIINgiaA](https://www.youtube.com/watch?v=PxcOIINgiaA)

| Timestamp Link | Video ID | Seg ID | Start | End | Text |
|---|---|---|---|---|---|
| [00:00](https://www.youtube.com/watch?v=PxcOIINgiaA&t=0s) | PxcOIINgiaA | 0 | 00:00 | 00:04 | Retrieval augmented generation is used in most AI agents. |
| [00:04](https://www.youtube.com/watch?v=PxcOIINgiaA&t=4s) | PxcOIINgiaA | 1 | 00:04 | 00:07 | It is the way to give your documents and data to your agent |
| [00:07](https://www.youtube.com/watch?v=PxcOIINgiaA&t=7s) | PxcOIINgiaA | 2 | 00:07 | 00:09 | to build up a knowledge base for them. |
| [00:09](https://www.youtube.com/watch?v=PxcOIINgiaA&t=9s) | PxcOIINgiaA | 3 | 00:09 | 00:11 | But as I always say on my channel, |
| [00:11](https://www.youtube.com/watch?v=PxcOIINgiaA&t=11s) | PxcOIINgiaA | 4 | 00:11 | 00:14 | RAG by itself, without additional strategies built on top, |
| [00:14](https://www.youtube.com/watch?v=PxcOIINgiaA&t=14s) | PxcOIINgiaA | 5 | 00:14 | 00:16 | has some pretty big limitations. |
| [00:16](https://www.youtube.com/watch?v=PxcOIINgiaA&t=16s) | PxcOIINgiaA | 6 | 00:16 | 00:20 | And one of those biggest ones is that RAG is very static. |
| [00:20](https://www.youtube.com/watch?v=PxcOIINgiaA&t=20s) | PxcOIINgiaA | 7 | 00:20 | 00:23 | And what I mean by that is it is your responsibility |
| [00:23](https://www.youtube.com/watch?v=PxcOIINgiaA&t=23s) | PxcOIINgiaA | 8 | 00:23 | 00:25 | to constantly keep the agent's knowledge base |
| [00:25](https://www.youtube.com/watch?v=PxcOIINgiaA&t=25s) | PxcOIINgiaA | 9 | 00:25 | 00:27 | in sync with your data store. |
| [00:27](https://www.youtube.com/watch?v=PxcOIINgiaA&t=27s) | PxcOIINgiaA | 10 | 00:27 | 00:30 | That process is inefficient and unreliable. |
| [00:31](https://www.youtube.com/watch?v=PxcOIINgiaA&t=31s) | PxcOIINgiaA | 11 | 00:31 | 00:35 | And so that's a problem because when your business or platform is constantly evolving |
| [00:35](https://www.youtube.com/watch?v=PxcOIINgiaA&t=35s) | PxcOIINgiaA | 12 | 00:35 | 00:40 | and you're working with constantly changing data like user preferences or internal metrics |
| [00:40](https://www.youtube.com/watch?v=PxcOIINgiaA&t=40s) | PxcOIINgiaA | 13 | 00:40 | 00:43 | or market conditions, RAG just can't keep up. |
| [00:43](https://www.youtube.com/watch?v=PxcOIINgiaA&t=43s) | PxcOIINgiaA | 14 | 00:43 | 00:47 | And so that's why I'm really excited to dive into an open source platform with you right |
| [00:47](https://www.youtube.com/watch?v=PxcOIINgiaA&t=47s) | PxcOIINgiaA | 15 | 00:47 | 00:48 | now called Graffiti. |
| [00:48](https://www.youtube.com/watch?v=PxcOIINgiaA&t=48s) | PxcOIINgiaA | 16 | 00:48 | 00:52 | Graffiti is all about building temporal aware knowledge graphs. |
| [00:52](https://www.youtube.com/watch?v=PxcOIINgiaA&t=52s) | PxcOIINgiaA | 17 | 00:52 | 00:57 | And it sounds fancy, but basically it's a layer on top of RAG that is meant for constantly |
| [00:57](https://www.youtube.com/watch?v=PxcOIINgiaA&t=57s) | PxcOIINgiaA | 18 | 00:57 | 01:02 | ingesting ever-changing data, also keeping a historical record of how your data has changed. |
| [01:02](https://www.youtube.com/watch?v=PxcOIINgiaA&t=62s) | PxcOIINgiaA | 19 | 01:02 | 01:07 | So your agent is aware of how the knowledge base is changing over time. It's just so powerful |
| [01:07](https://www.youtube.com/watch?v=PxcOIINgiaA&t=67s) | PxcOIINgiaA | 20 | 01:07 | 01:12 | for these very dynamic environments that you want to inject your agents in. And so right now, |
| [01:12](https://www.youtube.com/watch?v=PxcOIINgiaA&t=72s) | PxcOIINgiaA | 21 | 01:12 | 01:16 | I'm going to introduce you to graffiti and how to use it. It's super easy. And I'll even compare it |
| [01:16](https://www.youtube.com/watch?v=PxcOIINgiaA&t=76s) | PxcOIINgiaA | 22 | 01:16 | 01:22 | to other knowledge graphs like light rag and how you can use graffiti with other rag strategies. |
| [01:22](https://www.youtube.com/watch?v=PxcOIINgiaA&t=82s) | PxcOIINgiaA | 23 | 01:22 | 01:25 | A lot of value packed into this video, so let's dive right into it. |
| [01:25](https://www.youtube.com/watch?v=PxcOIINgiaA&t=85s) | PxcOIINgiaA | 24 | 01:25 | 01:30 | So here is the GitHub repository for Graffiti, which I'll link to below in the description. |
| [01:30](https://www.youtube.com/watch?v=PxcOIINgiaA&t=90s) | PxcOIINgiaA | 25 | 01:30 | 01:33 | And man, this is one of the best written remes I've seen in a while. |
| [01:33](https://www.youtube.com/watch?v=PxcOIINgiaA&t=93s) | PxcOIINgiaA | 26 | 01:33 | 01:37 | It gets you up and running so quickly, and you do it completely for free. |
| [01:37](https://www.youtube.com/watch?v=PxcOIINgiaA&t=97s) | PxcOIINgiaA | 27 | 01:37 | 01:42 | And so we'll dive into that in a little bit, getting it set up ourselves, going through their quick start. |
| [01:42](https://www.youtube.com/watch?v=PxcOIINgiaA&t=102s) | PxcOIINgiaA | 28 | 01:42 | 01:45 | But first, I want to cover a bit more why we want to use Graffiti, |
| [01:45](https://www.youtube.com/watch?v=PxcOIINgiaA&t=105s) | PxcOIINgiaA | 29 | 01:45 | 01:48 | what it really looks like to have a temporal aware knowledge graph. |
| [01:49](https://www.youtube.com/watch?v=PxcOIINgiaA&t=109s) | PxcOIINgiaA | 30 | 01:49 | 01:51 | And so we have this fact here that Kendra loves Adidas shoes. |
| [01:51](https://www.youtube.com/watch?v=PxcOIINgiaA&t=111s) | PxcOIINgiaA | 31 | 01:51 | 01:54 | But then she sends a message that says, oh, my shoes broke. |
| [01:54](https://www.youtube.com/watch?v=PxcOIINgiaA&t=114s) | PxcOIINgiaA | 32 | 01:54 | 01:57 | Now, I think Puma shoes are the best. |
| [01:57](https://www.youtube.com/watch?v=PxcOIINgiaA&t=117s) | PxcOIINgiaA | 33 | 01:57 | 02:00 | And instead of just replacing that fact in our knowledge base, we're adding in both, |
| [02:01](https://www.youtube.com/watch?v=PxcOIINgiaA&t=121s) | PxcOIINgiaA | 34 | 02:01 | 02:05 | but then we're adding some historical context here, saying that she doesn't like these shoes |
| [02:05](https://www.youtube.com/watch?v=PxcOIINgiaA&t=125s) | PxcOIINgiaA | 35 | 02:05 | 02:05 | anymore. |
| [02:05](https://www.youtube.com/watch?v=PxcOIINgiaA&t=125s) | PxcOIINgiaA | 36 | 02:05 | 02:08 | She used to, but now she likes Puma shoes. |
| [02:08](https://www.youtube.com/watch?v=PxcOIINgiaA&t=128s) | PxcOIINgiaA | 37 | 02:08 | 02:11 | And having things like user preferences evolve over time. |
| [02:11](https://www.youtube.com/watch?v=PxcOIINgiaA&t=131s) | PxcOIINgiaA | 38 | 02:11 | 02:15 | This is a very simple example, but it shows how powerful that is. |
| [02:15](https://www.youtube.com/watch?v=PxcOIINgiaA&t=135s) | PxcOIINgiaA | 39 | 02:15 | 02:19 | Because a lot of times, if we have something like a customer support agent, it needs to |
| [02:19](https://www.youtube.com/watch?v=PxcOIINgiaA&t=139s) | PxcOIINgiaA | 40 | 02:19 | 02:23 | know their past preferences as well, not just what they currently like, because that gives |
| [02:23](https://www.youtube.com/watch?v=PxcOIINgiaA&t=143s) | PxcOIINgiaA | 41 | 02:23 | 02:28 | that extra context to really give that personalized and above and beyond customer experience. And |
| [02:28](https://www.youtube.com/watch?v=PxcOIINgiaA&t=148s) | PxcOIINgiaA | 42 | 02:28 | 02:32 | again, you could take this and apply it to so many other different kinds of dynamic environments |
| [02:32](https://www.youtube.com/watch?v=PxcOIINgiaA&t=152s) | PxcOIINgiaA | 43 | 02:32 | 02:38 | that you have for your business or your platform. And all of this temporal aware knowledge is stored |
| [02:38](https://www.youtube.com/watch?v=PxcOIINgiaA&t=158s) | PxcOIINgiaA | 44 | 02:38 | 02:44 | in a knowledge graph that looks like this. And so this is Neo4j. That is the engine behind the |
| [02:44](https://www.youtube.com/watch?v=PxcOIINgiaA&t=164s) | PxcOIINgiaA | 45 | 02:44 | 02:48 | scenes powering our knowledge graph for the graffiti that we'll get into in a little bit. |
| [02:48](https://www.youtube.com/watch?v=PxcOIINgiaA&t=168s) | PxcOIINgiaA | 46 | 02:48 | 02:52 | And so we have all of these pieces of information that are linked together. So we have |
| [02:52](https://www.youtube.com/watch?v=PxcOIINgiaA&t=172s) | PxcOIINgiaA | 47 | 02:52 | 02:57 | relationships that help us understand how all the information in our knowledge base relates to each |
| [02:57](https://www.youtube.com/watch?v=PxcOIINgiaA&t=177s) | PxcOIINgiaA | 48 | 02:57 | 03:03 | other and also because graffiti is temporal how it changed over time and so like for example we |
| [03:03](https://www.youtube.com/watch?v=PxcOIINgiaA&t=183s) | PxcOIINgiaA | 49 | 03:03 | 03:10 | have gpt4 it relates to gpt 3.5 in the sense that it is a previous version so we have this kind of |
| [03:10](https://www.youtube.com/watch?v=PxcOIINgiaA&t=190s) | PxcOIINgiaA | 50 | 03:10 | 03:15 | metadata that helps us tie all of our information together this is why knowledge graphs in general |
| [03:15](https://www.youtube.com/watch?v=PxcOIINgiaA&t=195s) | PxcOIINgiaA | 51 | 03:15 | 03:20 | are just a lot more powerful than traditional rag and they both serve their purposes and so a lot of |
| [03:20](https://www.youtube.com/watch?v=PxcOIINgiaA&t=200s) | PxcOIINgiaA | 52 | 03:20 | 03:25 | times you'll have one tool given to your agent to search a knowledge graph, and then another tool |
| [03:25](https://www.youtube.com/watch?v=PxcOIINgiaA&t=205s) | PxcOIINgiaA | 53 | 03:25 | 03:29 | for to do a more traditional lookup in a vector database. Combining those two things together are |
| [03:29](https://www.youtube.com/watch?v=PxcOIINgiaA&t=209s) | PxcOIINgiaA | 54 | 03:29 | 03:34 | very powerful. So I don't mean to say, use knowledge graphs and just screw traditional |
| [03:34](https://www.youtube.com/watch?v=PxcOIINgiaA&t=214s) | PxcOIINgiaA | 55 | 03:34 | 03:39 | rag, like you still want to have that and build on those additional strategies like hybrid rag, |
| [03:39](https://www.youtube.com/watch?v=PxcOIINgiaA&t=219s) | PxcOIINgiaA | 56 | 03:39 | 03:44 | and contextual rag, things I've covered previously on my channel. But yeah, this is a very important |
| [03:44](https://www.youtube.com/watch?v=PxcOIINgiaA&t=224s) | PxcOIINgiaA | 57 | 03:44 | 03:49 | component to have in most of your AI agents so that you can represent how knowledge is related |
| [03:49](https://www.youtube.com/watch?v=PxcOIINgiaA&t=229s) | PxcOIINgiaA | 58 | 03:49 | 03:54 | when your agent is searching through it. And there are a lot of other implementations |
| [03:54](https://www.youtube.com/watch?v=PxcOIINgiaA&t=234s) | PxcOIINgiaA | 59 | 03:54 | 04:00 | for knowledge graphs as well. One really popular one is graph rag. And then there's a version of |
| [04:00](https://www.youtube.com/watch?v=PxcOIINgiaA&t=240s) | PxcOIINgiaA | 60 | 04:00 | 04:05 | it that I covered on my channel called light rag. But graffiti definitely serves different use cases |
| [04:05](https://www.youtube.com/watch?v=PxcOIINgiaA&t=245s) | PxcOIINgiaA | 61 | 04:05 | 04:10 | has some pros over these other more static knowledge graphs. Now full disclosure here, |
| [04:10](https://www.youtube.com/watch?v=PxcOIINgiaA&t=250s) | PxcOIINgiaA | 62 | 04:10 | 04:15 | before I dive into the comparison, I have actually partnered up with graffiti to bring you this video. |
| [04:15](https://www.youtube.com/watch?v=PxcOIINgiaA&t=255s) | PxcOIINgiaA | 63 | 04:15 | 04:17 | However, I was going to cover it anyway. |
| [04:17](https://www.youtube.com/watch?v=PxcOIINgiaA&t=257s) | PxcOIINgiaA | 64 | 04:17 | 04:19 | A lot of you have been asking me to do so. |
| [04:19](https://www.youtube.com/watch?v=PxcOIINgiaA&t=259s) | PxcOIINgiaA | 65 | 04:19 | 04:23 | And these are my honest thoughts comparing graffiti to other knowledge graph solutions |
| [04:23](https://www.youtube.com/watch?v=PxcOIINgiaA&t=263s) | PxcOIINgiaA | 66 | 04:23 | 04:25 | that I've covered in the past, like LightRag. |
| [04:25](https://www.youtube.com/watch?v=PxcOIINgiaA&t=265s) | PxcOIINgiaA | 67 | 04:25 | 04:30 | Because the thing is, with GraphRag and LightRag and other similar solutions, they're meant |
| [04:30](https://www.youtube.com/watch?v=PxcOIINgiaA&t=270s) | PxcOIINgiaA | 68 | 04:30 | 04:32 | more for static document summarization. |
| [04:32](https://www.youtube.com/watch?v=PxcOIINgiaA&t=272s) | PxcOIINgiaA | 69 | 04:32 | 04:37 | And so when you have information like maybe documentation that doesn't change very often, |
| [04:37](https://www.youtube.com/watch?v=PxcOIINgiaA&t=277s) | PxcOIINgiaA | 70 | 04:37 | 04:41 | using something like this, like LightRag, might actually be better. |
| [04:41](https://www.youtube.com/watch?v=PxcOIINgiaA&t=281s) | PxcOIINgiaA | 71 | 04:41 | 04:44 | Graffiti is meant more for working with dynamic data. |
| [04:44](https://www.youtube.com/watch?v=PxcOIINgiaA&t=284s) | PxcOIINgiaA | 72 | 04:44 | 04:52 | But the thing is, for most of your use cases, working with your platform or your business or just your life, like you're working with very dynamic data. |
| [04:52](https://www.youtube.com/watch?v=PxcOIINgiaA&t=292s) | PxcOIINgiaA | 73 | 04:52 | 04:57 | And that's why I'm so excited about graffiti, why I've really been looking forward to covering this for quite a while now. |
| [04:57](https://www.youtube.com/watch?v=PxcOIINgiaA&t=297s) | PxcOIINgiaA | 74 | 04:57 | 05:05 | It's all about working with continuous incremental updates to your information, building out that historical context that we saw earlier with that example. |
| [05:06](https://www.youtube.com/watch?v=PxcOIINgiaA&t=306s) | PxcOIINgiaA | 75 | 05:06 | 05:09 | And also graffiti is a lot more lightweight and scalable. |
| [05:09](https://www.youtube.com/watch?v=PxcOIINgiaA&t=309s) | PxcOIINgiaA | 76 | 05:09 | 05:18 | One of the things that I didn't really like about LightRag was how slow it was with both building up the knowledge graph and then also for the querying itself. |
| [05:18](https://www.youtube.com/watch?v=PxcOIINgiaA&t=318s) | PxcOIINgiaA | 77 | 05:18 | 05:22 | But graffiti is super fast for both, typically sub-second latency. |
| [05:22](https://www.youtube.com/watch?v=PxcOIINgiaA&t=322s) | PxcOIINgiaA | 78 | 05:22 | 05:24 | And we'll see this when we dive into the quick start. |
| [05:24](https://www.youtube.com/watch?v=PxcOIINgiaA&t=324s) | PxcOIINgiaA | 79 | 05:24 | 05:25 | Very, very impressive. |
| [05:26](https://www.youtube.com/watch?v=PxcOIINgiaA&t=326s) | PxcOIINgiaA | 80 | 05:26 | 05:27 | It also makes it a lot more scalable. |
| [05:27](https://www.youtube.com/watch?v=PxcOIINgiaA&t=327s) | PxcOIINgiaA | 81 | 05:27 | 05:36 | So you can seriously take graffiti all the way to production environments to build the ultimate rag solution with knowledge graphs for your AI agents. |
| [05:36](https://www.youtube.com/watch?v=PxcOIINgiaA&t=336s) | PxcOIINgiaA | 82 | 05:36 | 05:39 | So with that, let's now dive into a quick start. |
| [05:39](https://www.youtube.com/watch?v=PxcOIINgiaA&t=339s) | PxcOIINgiaA | 83 | 05:39 | 05:42 | Let's get our hands dirty with some code here, seeing graffiti in action. |
| [05:42](https://www.youtube.com/watch?v=PxcOIINgiaA&t=342s) | PxcOIINgiaA | 84 | 05:42 | 05:47 | So I'll walk you through a simple quick start so we can understand the basics of how to build with graffiti. |
| [05:48](https://www.youtube.com/watch?v=PxcOIINgiaA&t=348s) | PxcOIINgiaA | 85 | 05:48 | 05:53 | And then I'll also show you how to build a full knowledge graph RAG AI agent with Pydantic AI, |
| [05:53](https://www.youtube.com/watch?v=PxcOIINgiaA&t=353s) | PxcOIINgiaA | 86 | 05:53 | 05:58 | where we can use graffiti as the tools for our agent so that our agent can search our knowledge graph. |
| [05:59](https://www.youtube.com/watch?v=PxcOIINgiaA&t=359s) | PxcOIINgiaA | 87 | 05:59 | 06:00 | Got a lot of stuff wrapped here for you. |
| [06:00](https://www.youtube.com/watch?v=PxcOIINgiaA&t=360s) | PxcOIINgiaA | 88 | 06:00 | 06:03 | And the quick start is based on what we have here in the readme. |
| [06:03](https://www.youtube.com/watch?v=PxcOIINgiaA&t=363s) | PxcOIINgiaA | 89 | 06:03 | 06:14 | And there are only a couple of prerequisites for Graffiti, which is Python, Neo4j, which is our knowledge graph engine, and then we'll be using OpenAI for our LLMs and embedding models. |
| [06:14](https://www.youtube.com/watch?v=PxcOIINgiaA&t=374s) | PxcOIINgiaA | 90 | 06:14 | 06:19 | But you can use a lot of other providers as well, like Gemini or Anthropic. |
| [06:20](https://www.youtube.com/watch?v=PxcOIINgiaA&t=380s) | PxcOIINgiaA | 91 | 06:20 | 06:22 | And so they have a lot of documentation that covers this. |
| [06:22](https://www.youtube.com/watch?v=PxcOIINgiaA&t=382s) | PxcOIINgiaA | 92 | 06:22 | 06:30 | Like if we go later on in their readme, they show us with an example how to use Graffiti with Azure OpenAI and Gemini models as well. |
| [06:30](https://www.youtube.com/watch?v=PxcOIINgiaA&t=390s) | PxcOIINgiaA | 93 | 06:30 | 06:39 | And then if you go into their official documentation, which I'll link to this in the description too, and go to the installation tab, they have some instructions for working with different LLM providers. |
| [06:39](https://www.youtube.com/watch?v=PxcOIINgiaA&t=399s) | PxcOIINgiaA | 94 | 06:39 | 06:50 | And this could be something like Ollama if you want this entire implementation to be 100% local, which will work because we can host Neo4j completely locally since it is an open source knowledge graph engine. |
| [06:50](https://www.youtube.com/watch?v=PxcOIINgiaA&t=410s) | PxcOIINgiaA | 95 | 06:50 | 06:53 | And then we can use Ollama for our LLMs, which is super, super neat. |
| [06:53](https://www.youtube.com/watch?v=PxcOIINgiaA&t=413s) | PxcOIINgiaA | 96 | 06:53 | 07:00 | And speaking of Neo4j, there are two primary ways that we can run Neo4j on our own machine. |
| [07:00](https://www.youtube.com/watch?v=PxcOIINgiaA&t=420s) | PxcOIINgiaA | 97 | 07:00 | 07:04 | The first way that they recommend is to use Neo4j desktops. |
| [07:05](https://www.youtube.com/watch?v=PxcOIINgiaA&t=425s) | PxcOIINgiaA | 98 | 07:05 | 07:09 | You can just go to this link, go through the instructions to get this downloaded, set up on your computer, |
| [07:09](https://www.youtube.com/watch?v=PxcOIINgiaA&t=429s) | PxcOIINgiaA | 99 | 07:09 | 07:14 | and then there's a few pieces of information that you have to save, which is going to be the URL for Neo4j, |
| [07:14](https://www.youtube.com/watch?v=PxcOIINgiaA&t=434s) | PxcOIINgiaA | 100 | 07:14 | 07:18 | and then your username and password. We'll use those later in our environment variables. |
| [07:19](https://www.youtube.com/watch?v=PxcOIINgiaA&t=439s) | PxcOIINgiaA | 101 | 07:19 | 07:19 | So that's one way. |
| [07:19](https://www.youtube.com/watch?v=PxcOIINgiaA&t=439s) | PxcOIINgiaA | 102 | 07:19 | 07:23 | The other way that actually I would recommend, because I put effort into doing this for you, |
| [07:24](https://www.youtube.com/watch?v=PxcOIINgiaA&t=444s) | PxcOIINgiaA | 103 | 07:24 | 07:28 | is I took my local AI package, which I've covered a lot on my channel before, where |
| [07:28](https://www.youtube.com/watch?v=PxcOIINgiaA&t=448s) | PxcOIINgiaA | 104 | 07:28 | 07:32 | I curated a bunch of open source solutions that you can run all together, and I added |
| [07:32](https://www.youtube.com/watch?v=PxcOIINgiaA&t=452s) | PxcOIINgiaA | 105 | 07:32 | 07:34 | in Neo4j. |
| [07:34](https://www.youtube.com/watch?v=PxcOIINgiaA&t=454s) | PxcOIINgiaA | 106 | 07:34 | 07:38 | And so you can refer to this video if you want setup instructions for the local AI package. |
| [07:38](https://www.youtube.com/watch?v=PxcOIINgiaA&t=458s) | PxcOIINgiaA | 107 | 07:38 | 07:42 | It's a little bit older, but everything still works, except you'll just have to set a couple |
| [07:42](https://www.youtube.com/watch?v=PxcOIINgiaA&t=462s) | PxcOIINgiaA | 108 | 07:42 | 07:47 | of extra environment variables for things like the Neo4j username and password. |
| [07:47](https://www.youtube.com/watch?v=PxcOIINgiaA&t=467s) | PxcOIINgiaA | 109 | 07:47 | 07:49 | Very easy to get this up and running, though. |
| [07:49](https://www.youtube.com/watch?v=PxcOIINgiaA&t=469s) | PxcOIINgiaA | 110 | 07:49 | 07:56 | And I can even show you that within my own Docker desktop here, I have Neo4j that is running as a part of my stack. |
| [07:56](https://www.youtube.com/watch?v=PxcOIINgiaA&t=476s) | PxcOIINgiaA | 111 | 07:56 | 07:58 | So we can see it at the top right here. |
| [07:58](https://www.youtube.com/watch?v=PxcOIINgiaA&t=478s) | PxcOIINgiaA | 112 | 07:58 | 08:00 | So this is my knowledge graph. |
| [08:00](https://www.youtube.com/watch?v=PxcOIINgiaA&t=480s) | PxcOIINgiaA | 113 | 08:00 | 08:06 | And that's what I showed you earlier when we were looking at the knowledge graph here with all of these nodes that we have all connected together. |
| [08:06](https://www.youtube.com/watch?v=PxcOIINgiaA&t=486s) | PxcOIINgiaA | 114 | 08:06 | 08:08 | And we'll build this up in our quick start too. |
| [08:09](https://www.youtube.com/watch?v=PxcOIINgiaA&t=489s) | PxcOIINgiaA | 115 | 08:09 | 08:11 | So that's getting Neo4j installed. |
| [08:11](https://www.youtube.com/watch?v=PxcOIINgiaA&t=491s) | PxcOIINgiaA | 116 | 08:11 | 08:12 | A couple of ways to do it. |
| [08:12](https://www.youtube.com/watch?v=PxcOIINgiaA&t=492s) | PxcOIINgiaA | 117 | 08:12 | 08:13 | Very easy. |
| [08:13](https://www.youtube.com/watch?v=PxcOIINgiaA&t=493s) | PxcOIINgiaA | 118 | 08:13 | 08:15 | And then with that, we can dive into the quick start. |
| [08:15](https://www.youtube.com/watch?v=PxcOIINgiaA&t=495s) | PxcOIINgiaA | 119 | 08:15 | 08:19 | And so I'm going to go off this readme now because I have my own version of the quick |
| [08:19](https://www.youtube.com/watch?v=PxcOIINgiaA&t=499s) | PxcOIINgiaA | 120 | 08:19 | 08:21 | start that I want to share with you. |
| [08:21](https://www.youtube.com/watch?v=PxcOIINgiaA&t=501s) | PxcOIINgiaA | 121 | 08:21 | 08:21 | So let me show you this. |
| [08:21](https://www.youtube.com/watch?v=PxcOIINgiaA&t=501s) | PxcOIINgiaA | 122 | 08:21 | 08:27 | So within my AI IDE, I have everything shown here that we're going to be diving into. |
| [08:27](https://www.youtube.com/watch?v=PxcOIINgiaA&t=507s) | PxcOIINgiaA | 123 | 08:27 | 08:30 | And I'll have a link to this in the description as well. |
| [08:30](https://www.youtube.com/watch?v=PxcOIINgiaA&t=510s) | PxcOIINgiaA | 124 | 08:30 | 08:35 | If you want to dive into this GitHub repository, take these examples that I built for you, |
| [08:35](https://www.youtube.com/watch?v=PxcOIINgiaA&t=515s) | PxcOIINgiaA | 125 | 08:35 | 08:39 | test them out, use this as a starting point to use graffiti, however you want to use it. |
| [08:39](https://www.youtube.com/watch?v=PxcOIINgiaA&t=519s) | PxcOIINgiaA | 126 | 08:39 | 08:41 | And this readme has instructions to set up everything. |
| [08:41](https://www.youtube.com/watch?v=PxcOIINgiaA&t=521s) | PxcOIINgiaA | 127 | 08:41 | 08:45 | And the prerequisites are the same as the ones we saw in the graffiti readme. |
| [08:45](https://www.youtube.com/watch?v=PxcOIINgiaA&t=525s) | PxcOIINgiaA | 128 | 08:45 | 08:51 | So follow this if you want to get everything installed and ready to go to follow along or just use this template for yourself. |
| [08:51](https://www.youtube.com/watch?v=PxcOIINgiaA&t=531s) | PxcOIINgiaA | 129 | 08:51 | 08:54 | There are two things that I want to cover with you here. |
| [08:54](https://www.youtube.com/watch?v=PxcOIINgiaA&t=534s) | PxcOIINgiaA | 130 | 08:54 | 09:01 | I want to start with a quick start where we are going to add data into our knowledge graph with graffiti and do some simple querying. |
| [09:01](https://www.youtube.com/watch?v=PxcOIINgiaA&t=541s) | PxcOIINgiaA | 131 | 09:01 | 09:11 | And then I want to show you how we can build a full AI agent to leverage this knowledge base as tools for the agent so that we can run this script to evolve our knowledge base over time. |
| [09:11](https://www.youtube.com/watch?v=PxcOIINgiaA&t=551s) | PxcOIINgiaA | 132 | 09:11 | 09:16 | and then in parallel, ask the same question a couple of times to our agent. So we can see how |
| [09:16](https://www.youtube.com/watch?v=PxcOIINgiaA&t=556s) | PxcOIINgiaA | 133 | 09:16 | 09:21 | our data evolves over time, how that also changes the answers of our agent over time. And so let's |
| [09:21](https://www.youtube.com/watch?v=PxcOIINgiaA&t=561s) | PxcOIINgiaA | 134 | 09:21 | 09:26 | start with the quick start. So we can get a sense for how graffiti really works. And so they have |
| [09:26](https://www.youtube.com/watch?v=PxcOIINgiaA&t=566s) | PxcOIINgiaA | 135 | 09:26 | 09:32 | some boilerplate at the top here. The first thing that's important is making our connection to Neo4j. |
| [09:32](https://www.youtube.com/watch?v=PxcOIINgiaA&t=572s) | PxcOIINgiaA | 136 | 09:32 | 09:36 | So we have to pull all of our environment variables for Neo4j, which you can just set in the |
| [09:36](https://www.youtube.com/watch?v=PxcOIINgiaA&t=576s) | PxcOIINgiaA | 137 | 09:36 | 09:41 | dot env dot example file instructions, then read me, of course. And then in our main function, |
| [09:41](https://www.youtube.com/watch?v=PxcOIINgiaA&t=581s) | PxcOIINgiaA | 138 | 09:41 | 09:47 | we make that first call to initialize graffiti with all of those Neo4j credentials. And then |
| [09:47](https://www.youtube.com/watch?v=PxcOIINgiaA&t=587s) | PxcOIINgiaA | 139 | 09:47 | 09:52 | we build our indices and constraints, just setting up our initial knowledge graph once we are |
| [09:52](https://www.youtube.com/watch?v=PxcOIINgiaA&t=592s) | PxcOIINgiaA | 140 | 09:52 | 09:58 | connected to Neo4j. And then we can start adding in our episodes. So episodes are all of the pieces |
| [09:58](https://www.youtube.com/watch?v=PxcOIINgiaA&t=598s) | PxcOIINgiaA | 141 | 09:58 | 10:02 | of information that we want to store in our knowledge graph. That's just what graffiti |
| [10:02](https://www.youtube.com/watch?v=PxcOIINgiaA&t=602s) | PxcOIINgiaA | 142 | 10:02 | 10:08 | calls them. And the best part about these episodes is they don't have to follow a specific format. |
| [10:09](https://www.youtube.com/watch?v=PxcOIINgiaA&t=609s) | PxcOIINgiaA | 143 | 10:09 | 10:14 | Like in this case, we have the content here, which is just a string. And so for this example, |
| [10:14](https://www.youtube.com/watch?v=PxcOIINgiaA&t=614s) | PxcOIINgiaA | 144 | 10:14 | 10:17 | I'm just going to be putting in a bunch of information about different LLMs like Claude |
| [10:17](https://www.youtube.com/watch?v=PxcOIINgiaA&t=617s) | PxcOIINgiaA | 145 | 10:17 | 10:22 | and GPT. So for this first episode, it's just a string, a single piece of information. We do that |
| [10:22](https://www.youtube.com/watch?v=PxcOIINgiaA&t=622s) | PxcOIINgiaA | 146 | 10:22 | 10:27 | for Claude, but then for GPT, the content is actually an object. So instead of it being a |
| [10:27](https://www.youtube.com/watch?v=PxcOIINgiaA&t=627s) | PxcOIINgiaA | 147 | 10:27 | 10:34 | text episode type, it is a JSON episode type. And so we can specify these key and value pairs. And |
| [10:34](https://www.youtube.com/watch?v=PxcOIINgiaA&t=634s) | PxcOIINgiaA | 148 | 10:34 | 10:37 | so no matter how you have to represent the information that you want to store in your |
| [10:37](https://www.youtube.com/watch?v=PxcOIINgiaA&t=637s) | PxcOIINgiaA | 149 | 10:37 | 10:41 | knowledge graph, you can do that. And there's different formats that are available to you. |
| [10:41](https://www.youtube.com/watch?v=PxcOIINgiaA&t=641s) | PxcOIINgiaA | 150 | 10:41 | 10:48 | And this actually shows what we saw in the example earlier, where that relationship between GPT-4 and |
| [10:48](https://www.youtube.com/watch?v=PxcOIINgiaA&t=648s) | PxcOIINgiaA | 151 | 10:48 | 10:55 | 3.5 was that 3.5 was the previous version of 4. And so when the LLM is working with our episodes |
| [10:55](https://www.youtube.com/watch?v=PxcOIINgiaA&t=655s) | PxcOIINgiaA | 152 | 10:55 | 10:58 | and inserting those into the knowledge graph |
| [10:58](https://www.youtube.com/watch?v=PxcOIINgiaA&t=658s) | PxcOIINgiaA | 153 | 10:58 | 10:59 | and building up those relations, |
| [10:59](https://www.youtube.com/watch?v=PxcOIINgiaA&t=659s) | PxcOIINgiaA | 154 | 10:59 | 11:01 | it goes off of these values to do that. |
| [11:01](https://www.youtube.com/watch?v=PxcOIINgiaA&t=661s) | PxcOIINgiaA | 155 | 11:01 | 11:04 | And so we have this dynamic creation of our knowledge graph |
| [11:04](https://www.youtube.com/watch?v=PxcOIINgiaA&t=664s) | PxcOIINgiaA | 156 | 11:04 | 11:06 | just based on how the LLM is understanding |
| [11:06](https://www.youtube.com/watch?v=PxcOIINgiaA&t=666s) | PxcOIINgiaA | 157 | 11:06 | 11:08 | the data that we are giving it. |
| [11:08](https://www.youtube.com/watch?v=PxcOIINgiaA&t=668s) | PxcOIINgiaA | 158 | 11:08 | 11:09 | That's what makes it so powerful. |
| [11:10](https://www.youtube.com/watch?v=PxcOIINgiaA&t=670s) | PxcOIINgiaA | 159 | 11:10 | 11:12 | And we'll dive into what the knowledge graph looks like again |
| [11:12](https://www.youtube.com/watch?v=PxcOIINgiaA&t=672s) | PxcOIINgiaA | 160 | 11:12 | 11:13 | once we run this quick start. |
| [11:14](https://www.youtube.com/watch?v=PxcOIINgiaA&t=674s) | PxcOIINgiaA | 161 | 11:14 | 11:15 | And so after we create our episodes, |
| [11:15](https://www.youtube.com/watch?v=PxcOIINgiaA&t=675s) | PxcOIINgiaA | 162 | 11:15 | 11:18 | we're just gonna call graffiti.addEpisode for each one. |
| [11:18](https://www.youtube.com/watch?v=PxcOIINgiaA&t=678s) | PxcOIINgiaA | 163 | 11:18 | 11:19 | We have some metadata as well, |
| [11:20](https://www.youtube.com/watch?v=PxcOIINgiaA&t=680s) | PxcOIINgiaA | 164 | 11:20 | 11:22 | like the name of the episode and the source. |
| [11:22](https://www.youtube.com/watch?v=PxcOIINgiaA&t=682s) | PxcOIINgiaA | 165 | 11:22 | 11:24 | And because this is a temporal knowledge graph, |
| [11:24](https://www.youtube.com/watch?v=PxcOIINgiaA&t=684s) | PxcOIINgiaA | 166 | 11:24 | 11:26 | we need the reference time as well. |
| [11:26](https://www.youtube.com/watch?v=PxcOIINgiaA&t=686s) | PxcOIINgiaA | 167 | 11:26 | 11:27 | That is super important |
| [11:27](https://www.youtube.com/watch?v=PxcOIINgiaA&t=687s) | PxcOIINgiaA | 168 | 11:27 | 11:29 | because we have to know when we inserted this information. |
| [11:30](https://www.youtube.com/watch?v=PxcOIINgiaA&t=690s) | PxcOIINgiaA | 169 | 11:30 | 11:32 | And then also if we do ever invalidate it in the future, |
| [11:32](https://www.youtube.com/watch?v=PxcOIINgiaA&t=692s) | PxcOIINgiaA | 170 | 11:32 | 11:35 | like Kendra doesn't like Adidas shoes anymore, |
| [11:35](https://www.youtube.com/watch?v=PxcOIINgiaA&t=695s) | PxcOIINgiaA | 171 | 11:35 | 11:38 | we also have to know when this data became invalid. |
| [11:38](https://www.youtube.com/watch?v=PxcOIINgiaA&t=698s) | PxcOIINgiaA | 172 | 11:38 | 11:40 | And that happens more under the hood. |
| [11:40](https://www.youtube.com/watch?v=PxcOIINgiaA&t=700s) | PxcOIINgiaA | 173 | 11:40 | 11:42 | And then there are a few different ways |
| [11:42](https://www.youtube.com/watch?v=PxcOIINgiaA&t=702s) | PxcOIINgiaA | 174 | 11:42 | 11:44 | for us to search our knowledge graph. |
| [11:44](https://www.youtube.com/watch?v=PxcOIINgiaA&t=704s) | PxcOIINgiaA | 175 | 11:44 | 11:46 | And Graffiti makes it so, so easy. |
| [11:46](https://www.youtube.com/watch?v=PxcOIINgiaA&t=706s) | PxcOIINgiaA | 176 | 11:46 | 11:47 | Take a look at this. |
| [11:47](https://www.youtube.com/watch?v=PxcOIINgiaA&t=707s) | PxcOIINgiaA | 177 | 11:47 | 11:50 | It is a single function call, graffiti.search. |
| [11:50](https://www.youtube.com/watch?v=PxcOIINgiaA&t=710s) | PxcOIINgiaA | 178 | 11:50 | 11:51 | And then we can ask a question |
| [11:51](https://www.youtube.com/watch?v=PxcOIINgiaA&t=711s) | PxcOIINgiaA | 179 | 11:51 | 11:54 | like which AI assistant is from Anthropic. |
| [11:54](https://www.youtube.com/watch?v=PxcOIINgiaA&t=714s) | PxcOIINgiaA | 180 | 11:54 | 11:56 | And there are other parameters you can specify here, |
| [11:57](https://www.youtube.com/watch?v=PxcOIINgiaA&t=717s) | PxcOIINgiaA | 181 | 11:57 | 11:59 | like the number of nodes or facts that you get back. |
| [12:00](https://www.youtube.com/watch?v=PxcOIINgiaA&t=720s) | PxcOIINgiaA | 182 | 12:00 | 12:01 | You can check out their documentation |
| [12:01](https://www.youtube.com/watch?v=PxcOIINgiaA&t=721s) | PxcOIINgiaA | 183 | 12:01 | 12:02 | if you're interested in that. |
| [12:02](https://www.youtube.com/watch?v=PxcOIINgiaA&t=722s) | PxcOIINgiaA | 184 | 12:02 | 12:03 | I'm just keeping it really simple here, |
| [12:03](https://www.youtube.com/watch?v=PxcOIINgiaA&t=723s) | PxcOIINgiaA | 185 | 12:03 | 12:05 | like they did in their quick start. |
| [12:05](https://www.youtube.com/watch?v=PxcOIINgiaA&t=725s) | PxcOIINgiaA | 186 | 12:05 | 12:08 | And then for each of the results that we get back, |
| [12:08](https://www.youtube.com/watch?v=PxcOIINgiaA&t=728s) | PxcOIINgiaA | 187 | 12:08 | 12:11 | we have a unique identifier that we have for the node. |
| [12:12](https://www.youtube.com/watch?v=PxcOIINgiaA&t=732s) | PxcOIINgiaA | 188 | 12:12 | 12:13 | We have the fact itself. |
| [12:13](https://www.youtube.com/watch?v=PxcOIINgiaA&t=733s) | PxcOIINgiaA | 189 | 12:13 | 12:16 | This is the actual information that we stored. |
| [12:16](https://www.youtube.com/watch?v=PxcOIINgiaA&t=736s) | PxcOIINgiaA | 190 | 12:16 | 12:18 | And then we have valid add. |
| [12:18](https://www.youtube.com/watch?v=PxcOIINgiaA&t=738s) | PxcOIINgiaA | 191 | 12:18 | 12:20 | This is when we put the information in the knowledge graph. |
| [12:20](https://www.youtube.com/watch?v=PxcOIINgiaA&t=740s) | PxcOIINgiaA | 192 | 12:20 | 12:21 | And then like I said earlier, |
| [12:21](https://www.youtube.com/watch?v=PxcOIINgiaA&t=741s) | PxcOIINgiaA | 193 | 12:21 | 12:23 | if we invalidate at any point, |
| [12:23](https://www.youtube.com/watch?v=PxcOIINgiaA&t=743s) | PxcOIINgiaA | 194 | 12:23 | 12:25 | we'll also have this information available to us. |
| [12:25](https://www.youtube.com/watch?v=PxcOIINgiaA&t=745s) | PxcOIINgiaA | 195 | 12:25 | 12:28 | And this is so powerful to give to our AI agents |
| [12:28](https://www.youtube.com/watch?v=PxcOIINgiaA&t=748s) | PxcOIINgiaA | 196 | 12:28 | 12:30 | so we can reason about what information |
| [12:30](https://www.youtube.com/watch?v=PxcOIINgiaA&t=750s) | PxcOIINgiaA | 197 | 12:30 | 12:33 | is actually still relevant for answering our question. |
| [12:33](https://www.youtube.com/watch?v=PxcOIINgiaA&t=753s) | PxcOIINgiaA | 198 | 12:33 | 12:35 | And then another really cool thing that you can do |
| [12:35](https://www.youtube.com/watch?v=PxcOIINgiaA&t=755s) | PxcOIINgiaA | 199 | 12:35 | 12:38 | is you can do a center node search. |
| [12:38](https://www.youtube.com/watch?v=PxcOIINgiaA&t=758s) | PxcOIINgiaA | 200 | 12:38 | 12:41 | And so like if you pick out a specific piece of information |
| [12:41](https://www.youtube.com/watch?v=PxcOIINgiaA&t=761s) | PxcOIINgiaA | 201 | 12:41 | 12:44 | and you want to search more kind of around |
| [12:44](https://www.youtube.com/watch?v=PxcOIINgiaA&t=764s) | PxcOIINgiaA | 202 | 12:44 | 12:46 | that specific node, you can do that. |
| [12:46](https://www.youtube.com/watch?v=PxcOIINgiaA&t=766s) | PxcOIINgiaA | 203 | 12:46 | 12:48 | So like, for example, we can take the top result |
| [12:48](https://www.youtube.com/watch?v=PxcOIINgiaA&t=768s) | PxcOIINgiaA | 204 | 12:48 | 12:49 | from our first search, |
| [12:50](https://www.youtube.com/watch?v=PxcOIINgiaA&t=770s) | PxcOIINgiaA | 205 | 12:50 | 12:52 | and then we can do a more refined search |
| [12:52](https://www.youtube.com/watch?v=PxcOIINgiaA&t=772s) | PxcOIINgiaA | 206 | 12:52 | 12:55 | using a center node to dictate this operation. |
| [12:55](https://www.youtube.com/watch?v=PxcOIINgiaA&t=775s) | PxcOIINgiaA | 207 | 12:55 | 12:56 | So it's just another parameter |
| [12:56](https://www.youtube.com/watch?v=PxcOIINgiaA&t=776s) | PxcOIINgiaA | 208 | 12:56 | 12:58 | that we add to our graffiti search. |
| [12:58](https://www.youtube.com/watch?v=PxcOIINgiaA&t=778s) | PxcOIINgiaA | 209 | 12:58 | 12:59 | So maybe for example, |
| [13:00](https://www.youtube.com/watch?v=PxcOIINgiaA&t=780s) | PxcOIINgiaA | 210 | 13:00 | 13:03 | we know that we're asking a question related to clod four. |
| [13:03](https://www.youtube.com/watch?v=PxcOIINgiaA&t=783s) | PxcOIINgiaA | 211 | 13:03 | 13:05 | So if we first find clod four in our knowledge graph, |
| [13:05](https://www.youtube.com/watch?v=PxcOIINgiaA&t=785s) | PxcOIINgiaA | 212 | 13:05 | 13:07 | then we can search around that. |
| [13:07](https://www.youtube.com/watch?v=PxcOIINgiaA&t=787s) | PxcOIINgiaA | 213 | 13:07 | 13:09 | Like what is the parameter size, for example? |
| [13:09](https://www.youtube.com/watch?v=PxcOIINgiaA&t=789s) | PxcOIINgiaA | 214 | 13:09 | 13:11 | So then it wouldn't accidentally pull |
| [13:11](https://www.youtube.com/watch?v=PxcOIINgiaA&t=791s) | PxcOIINgiaA | 215 | 13:11 | 13:15 | the parameter size for a GPT or the cost for GPT. |
| [13:15](https://www.youtube.com/watch?v=PxcOIINgiaA&t=795s) | PxcOIINgiaA | 216 | 13:15 | 13:16 | Like whatever we're searching, |
| [13:16](https://www.youtube.com/watch?v=PxcOIINgiaA&t=796s) | PxcOIINgiaA | 217 | 13:16 | 13:17 | we can make it more specific. |
| [13:17](https://www.youtube.com/watch?v=PxcOIINgiaA&t=797s) | PxcOIINgiaA | 218 | 13:17 | 13:19 | So just another really good example to show |
| [13:19](https://www.youtube.com/watch?v=PxcOIINgiaA&t=799s) | PxcOIINgiaA | 219 | 13:19 | 13:22 | like how powerful having these knowledge graphs are. |
| [13:22](https://www.youtube.com/watch?v=PxcOIINgiaA&t=802s) | PxcOIINgiaA | 220 | 13:22 | 13:24 | Like not only is it easier for our agents |
| [13:24](https://www.youtube.com/watch?v=PxcOIINgiaA&t=804s) | PxcOIINgiaA | 221 | 13:24 | 13:26 | to understand relationships between things, |
| [13:26](https://www.youtube.com/watch?v=PxcOIINgiaA&t=806s) | PxcOIINgiaA | 222 | 13:26 | 13:28 | but also we can make our searches more refined |
| [13:28](https://www.youtube.com/watch?v=PxcOIINgiaA&t=808s) | PxcOIINgiaA | 223 | 13:28 | 13:30 | by doing something like searching on a center node |
| [13:30](https://www.youtube.com/watch?v=PxcOIINgiaA&t=810s) | PxcOIINgiaA | 224 | 13:30 | 13:32 | and then just printing those results |
| [13:32](https://www.youtube.com/watch?v=PxcOIINgiaA&t=812s) | PxcOIINgiaA | 225 | 13:32 | 13:33 | in pretty much the same way. |
| [13:34](https://www.youtube.com/watch?v=PxcOIINgiaA&t=814s) | PxcOIINgiaA | 226 | 13:34 | 13:36 | And then another thing that Graffiti showed |
| [13:36](https://www.youtube.com/watch?v=PxcOIINgiaA&t=816s) | PxcOIINgiaA | 227 | 13:36 | 13:38 | in their quick start that I don't wanna cover too much here |
| [13:38](https://www.youtube.com/watch?v=PxcOIINgiaA&t=818s) | PxcOIINgiaA | 228 | 13:38 | 13:39 | just to keep things brief. |
| [13:40](https://www.youtube.com/watch?v=PxcOIINgiaA&t=820s) | PxcOIINgiaA | 229 | 13:40 | 13:41 | There are different search recipes. |
| [13:41](https://www.youtube.com/watch?v=PxcOIINgiaA&t=821s) | PxcOIINgiaA | 230 | 13:41 | 13:44 | So different ways you can explore the knowledge graph |
| [13:44](https://www.youtube.com/watch?v=PxcOIINgiaA&t=824s) | PxcOIINgiaA | 231 | 13:44 | 13:45 | and perform these searches |
| [13:45](https://www.youtube.com/watch?v=PxcOIINgiaA&t=825s) | PxcOIINgiaA | 232 | 13:45 | 13:49 | based on what is optimal for your use case. |
| [13:49](https://www.youtube.com/watch?v=PxcOIINgiaA&t=829s) | PxcOIINgiaA | 233 | 13:49 | 13:52 | So check out their documentation and dive into this if you are interested. |
| [13:52](https://www.youtube.com/watch?v=PxcOIINgiaA&t=832s) | PxcOIINgiaA | 234 | 13:52 | 13:54 | Just yet another way we can take this further. |
| [13:55](https://www.youtube.com/watch?v=PxcOIINgiaA&t=835s) | PxcOIINgiaA | 235 | 13:55 | 13:59 | And so we're just doing a different kind of search type where we're looking at nodes directly instead of edges. |
| [13:59](https://www.youtube.com/watch?v=PxcOIINgiaA&t=839s) | PxcOIINgiaA | 236 | 13:59 | 14:06 | Everything looks pretty similar except for this extra configuration that we build out and then printing things in pretty much the same way. |
| [14:06](https://www.youtube.com/watch?v=PxcOIINgiaA&t=846s) | PxcOIINgiaA | 237 | 14:06 | 14:09 | And then also at the very end here, this is important to prevent memory leaks. |
| [14:09](https://www.youtube.com/watch?v=PxcOIINgiaA&t=849s) | PxcOIINgiaA | 238 | 14:09 | 14:12 | We have to close that connection in Neo4j. |
| [14:12](https://www.youtube.com/watch?v=PxcOIINgiaA&t=852s) | PxcOIINgiaA | 239 | 14:12 | 14:15 | We don't want that to persist after our script is done running. |
| [14:16](https://www.youtube.com/watch?v=PxcOIINgiaA&t=856s) | PxcOIINgiaA | 240 | 14:16 | 14:18 | So that is everything for our quick start. |
| [14:18](https://www.youtube.com/watch?v=PxcOIINgiaA&t=858s) | PxcOIINgiaA | 241 | 14:18 | 14:24 | And so what we can do, and I'll go through the knowledge graph again and show these nodes in action as they're being created. |
| [14:24](https://www.youtube.com/watch?v=PxcOIINgiaA&t=864s) | PxcOIINgiaA | 242 | 14:24 | 14:29 | But I can go ahead in my terminal here and now just running Python quickstart.py. |
| [14:29](https://www.youtube.com/watch?v=PxcOIINgiaA&t=869s) | PxcOIINgiaA | 243 | 14:29 | 14:33 | And then it's going to run a lot of things under the hood, but I'll actually show you. |
| [14:33](https://www.youtube.com/watch?v=PxcOIINgiaA&t=873s) | PxcOIINgiaA | 244 | 14:33 | 14:38 | Like I'll refresh this constantly so we can watch our knowledge graph getting built over time. |
| [14:38](https://www.youtube.com/watch?v=PxcOIINgiaA&t=878s) | PxcOIINgiaA | 245 | 14:38 | 14:39 | So it's completely cleared right now. |
| [14:40](https://www.youtube.com/watch?v=PxcOIINgiaA&t=880s) | PxcOIINgiaA | 246 | 14:40 | 14:41 | I cleared the demo that I showed you earlier. |
| [14:42](https://www.youtube.com/watch?v=PxcOIINgiaA&t=882s) | PxcOIINgiaA | 247 | 14:42 | 14:45 | But I'm going to click play here, go to graph mode, and then boom. |
| [14:45](https://www.youtube.com/watch?v=PxcOIINgiaA&t=885s) | PxcOIINgiaA | 248 | 14:45 | 14:49 | We have the first couple of nodes that are added to our knowledge graph for Claude. |
| [14:50](https://www.youtube.com/watch?v=PxcOIINgiaA&t=890s) | PxcOIINgiaA | 249 | 14:50 | 14:55 | And then it's going to be doing some more processing for OpenAI, all those episodes that I showed you earlier. |
| [14:55](https://www.youtube.com/watch?v=PxcOIINgiaA&t=895s) | PxcOIINgiaA | 250 | 14:55 | 14:57 | And if we look at the terminal here, let me actually go up. |
| [14:57](https://www.youtube.com/watch?v=PxcOIINgiaA&t=897s) | PxcOIINgiaA | 251 | 14:57 | 15:03 | There are a ton of different requests that are happening to OpenAI, both with the embedding model and then the LLM itself. |
| [15:03](https://www.youtube.com/watch?v=PxcOIINgiaA&t=903s) | PxcOIINgiaA | 252 | 15:03 | 15:09 | And the reason that there are so many requests is because we have to process those episodes and build all these relations. |
| [15:09](https://www.youtube.com/watch?v=PxcOIINgiaA&t=909s) | PxcOIINgiaA | 253 | 15:09 | 15:11 | There's so much that is happening under the hood. |
| [15:11](https://www.youtube.com/watch?v=PxcOIINgiaA&t=911s) | PxcOIINgiaA | 254 | 15:11 | 15:15 | And you can definitely use cheaper LLMs to make sure this process isn't too expensive. |
| [15:16](https://www.youtube.com/watch?v=PxcOIINgiaA&t=916s) | PxcOIINgiaA | 255 | 15:16 | 15:17 | It's really not that bad. |
| [15:17](https://www.youtube.com/watch?v=PxcOIINgiaA&t=917s) | PxcOIINgiaA | 256 | 15:17 | 15:18 | And so I'll run this again. |
| [15:18](https://www.youtube.com/watch?v=PxcOIINgiaA&t=918s) | PxcOIINgiaA | 257 | 15:18 | 15:19 | And boom, there we go. |
| [15:19](https://www.youtube.com/watch?v=PxcOIINgiaA&t=919s) | PxcOIINgiaA | 258 | 15:19 | 15:22 | We have one kind of cluster here for GPT-4. |
| [15:22](https://www.youtube.com/watch?v=PxcOIINgiaA&t=922s) | PxcOIINgiaA | 259 | 15:22 | 15:25 | And then we have another cluster for Claude. |
| [15:25](https://www.youtube.com/watch?v=PxcOIINgiaA&t=925s) | PxcOIINgiaA | 260 | 15:25 | 15:29 | And sometimes the LLM will connect these together like it did in the demo I showed you earlier. |
| [15:29](https://www.youtube.com/watch?v=PxcOIINgiaA&t=929s) | PxcOIINgiaA | 261 | 15:29 | 15:36 | There is a bit of unpredictability with Knowledge Grasp because we are relying on an LLM to build up these relations when we are adding these episodes. |
| [15:36](https://www.youtube.com/watch?v=PxcOIINgiaA&t=936s) | PxcOIINgiaA | 262 | 15:36 | 15:39 | But overall, like this works really, really well. |
| [15:39](https://www.youtube.com/watch?v=PxcOIINgiaA&t=939s) | PxcOIINgiaA | 263 | 15:39 | 15:44 | And so I can't even go back to my terminal here and I'll show you some of these searches that we had. |
| [15:44](https://www.youtube.com/watch?v=PxcOIINgiaA&t=944s) | PxcOIINgiaA | 264 | 15:44 | 15:48 | So first of all, we had that basic search, which AI assistant is from Anthropic. |
| [15:48](https://www.youtube.com/watch?v=PxcOIINgiaA&t=948s) | PxcOIINgiaA | 265 | 15:48 | 15:51 | And then we do get the ranked results back. |
| [15:51](https://www.youtube.com/watch?v=PxcOIINgiaA&t=951s) | PxcOIINgiaA | 266 | 15:51 | 15:54 | So this top fact actually directly answers our question. |
| [15:55](https://www.youtube.com/watch?v=PxcOIINgiaA&t=955s) | PxcOIINgiaA | 267 | 15:55 | 15:57 | Claude is the flagship AI assistant from Anthropic. |
| [15:58](https://www.youtube.com/watch?v=PxcOIINgiaA&t=958s) | PxcOIINgiaA | 268 | 15:58 | 16:01 | And then we can search based on the center node as well. |
| [16:01](https://www.youtube.com/watch?v=PxcOIINgiaA&t=961s) | PxcOIINgiaA | 269 | 16:01 | 16:05 | So we have this re-ranking search where we're using the center node of Claude4. |
| [16:05](https://www.youtube.com/watch?v=PxcOIINgiaA&t=965s) | PxcOIINgiaA | 270 | 16:05 | 16:10 | And so like I was saying earlier, like maybe we want to ask the token limit for an LLM. |
| [16:10](https://www.youtube.com/watch?v=PxcOIINgiaA&t=970s) | PxcOIINgiaA | 271 | 16:10 | 16:15 | We would want to, if we're looking at Claude specifically, use Claude as the center node. |
| [16:15](https://www.youtube.com/watch?v=PxcOIINgiaA&t=975s) | PxcOIINgiaA | 272 | 16:15 | 16:20 | So that way we don't accidentally pull the token limit for GPT-4. |
| [16:20](https://www.youtube.com/watch?v=PxcOIINgiaA&t=980s) | PxcOIINgiaA | 273 | 16:20 | 16:22 | And so we can do that kind of as a re-ranking technique. |
| [16:23](https://www.youtube.com/watch?v=PxcOIINgiaA&t=983s) | PxcOIINgiaA | 274 | 16:23 | 16:26 | And in this case, the question is still answered by this fact. |
| [16:26](https://www.youtube.com/watch?v=PxcOIINgiaA&t=986s) | PxcOIINgiaA | 275 | 16:26 | 16:27 | So this one is still at the top. |
| [16:27](https://www.youtube.com/watch?v=PxcOIINgiaA&t=987s) | PxcOIINgiaA | 276 | 16:27 | 16:31 | But you can envision scenarios where we don't quite get the right information. |
| [16:31](https://www.youtube.com/watch?v=PxcOIINgiaA&t=991s) | PxcOIINgiaA | 277 | 16:31 | 16:33 | But then we can do a research with that as the center. |
| [16:33](https://www.youtube.com/watch?v=PxcOIINgiaA&t=993s) | PxcOIINgiaA | 278 | 16:33 | 16:39 | So hopefully the adjacent nodes that we pull does have, you know, the perfect context that we need. |
| [16:39](https://www.youtube.com/watch?v=PxcOIINgiaA&t=999s) | PxcOIINgiaA | 279 | 16:39 | 16:43 | And then we just have that other search as well with a different strategy that I don't want to cover right here. |
| [16:43](https://www.youtube.com/watch?v=PxcOIINgiaA&t=1003s) | PxcOIINgiaA | 280 | 16:43 | 16:45 | But yeah, that is everything for our quick start. |
| [16:46](https://www.youtube.com/watch?v=PxcOIINgiaA&t=1006s) | PxcOIINgiaA | 281 | 16:46 | 16:53 | So back to our readme now, because I want to move on to building out a full AI agent using a lot of what we just covered. |
| [16:53](https://www.youtube.com/watch?v=PxcOIINgiaA&t=1013s) | PxcOIINgiaA | 282 | 16:53 | 16:57 | But now something that we can talk to that will use the knowledge graph as a tool. |
| [16:57](https://www.youtube.com/watch?v=PxcOIINgiaA&t=1017s) | PxcOIINgiaA | 283 | 16:57 | 17:03 | And so I'll start with this script right here because this is where I'm going to be adding in more information to our knowledge graph |
| [17:03](https://www.youtube.com/watch?v=PxcOIINgiaA&t=1023s) | PxcOIINgiaA | 284 | 17:03 | 17:08 | But I'm doing it in a special way where I do it in batches and then we can talk to our agent in between each batch |
| [17:08](https://www.youtube.com/watch?v=PxcOIINgiaA&t=1028s) | PxcOIINgiaA | 285 | 17:08 | 17:14 | So we can see how the information evolves over time also how that changes our agent's answer over time |
| [17:14](https://www.youtube.com/watch?v=PxcOIINgiaA&t=1034s) | PxcOIINgiaA | 286 | 17:14 | 17:17 | I think this is really the best way to show you the power of graffiti |
| [17:17](https://www.youtube.com/watch?v=PxcOIINgiaA&t=1037s) | PxcOIINgiaA | 287 | 17:17 | 17:22 | And so within this script we are connecting to neo4j in the exact same way |
| [17:22](https://www.youtube.com/watch?v=PxcOIINgiaA&t=1042s) | PxcOIINgiaA | 288 | 17:22 | 17:27 | We have this function to add episodes all of this is going to be very similar to the quick start |
| [17:28](https://www.youtube.com/watch?v=PxcOIINgiaA&t=1048s) | PxcOIINgiaA | 289 | 17:28 | 17:31 | But then what we're doing is we're adding information in phases. |
| [17:31](https://www.youtube.com/watch?v=PxcOIINgiaA&t=1051s) | PxcOIINgiaA | 290 | 17:31 | 17:36 | And so in phase one, we're adding in some episodes here talking about the best LLMs. |
| [17:36](https://www.youtube.com/watch?v=PxcOIINgiaA&t=1056s) | PxcOIINgiaA | 291 | 17:36 | 17:42 | And so we're going to talk about GPT 4.1, Gemini 2.5 Pro, and Claude 3.7 Sonnet. |
| [17:42](https://www.youtube.com/watch?v=PxcOIINgiaA&t=1062s) | PxcOIINgiaA | 292 | 17:42 | 17:45 | So all that information is added in phase one. |
| [17:45](https://www.youtube.com/watch?v=PxcOIINgiaA&t=1065s) | PxcOIINgiaA | 293 | 17:45 | 17:50 | But then within phase two, we're going to add in that Anthropic just released Claude 4. |
| [17:50](https://www.youtube.com/watch?v=PxcOIINgiaA&t=1070s) | PxcOIINgiaA | 294 | 17:50 | 17:52 | Now we have a new best LLM. |
| [17:52](https://www.youtube.com/watch?v=PxcOIINgiaA&t=1072s) | PxcOIINgiaA | 295 | 17:52 | 17:56 | Before, it was Gemini 2.5 Pro, but now it's Claude 4. |
| [17:56](https://www.youtube.com/watch?v=PxcOIINgiaA&t=1076s) | PxcOIINgiaA | 296 | 17:56 | 18:03 | And so we're going to see how our knowledge graph will update as certain things become invalidated as we add newer, more relevant information. |
| [18:04](https://www.youtube.com/watch?v=PxcOIINgiaA&t=1084s) | PxcOIINgiaA | 297 | 18:04 | 18:08 | And then in our last phase, just kind of as a joke, this isn't real. |
| [18:08](https://www.youtube.com/watch?v=PxcOIINgiaA&t=1088s) | PxcOIINgiaA | 298 | 18:08 | 18:17 | I'm saying there's a new revolutionary type of AI model called the massive language models or MLMs for short, not to be confused with multi-level marketing. |
| [18:18](https://www.youtube.com/watch?v=PxcOIINgiaA&t=1098s) | PxcOIINgiaA | 299 | 18:18 | 18:21 | So we have this brand new thing that's making LLMs completely irrelevant. |
| [18:22](https://www.youtube.com/watch?v=PxcOIINgiaA&t=1102s) | PxcOIINgiaA | 300 | 18:22 | 18:24 | We've got our first MLM, which is called Nexus One. |
| [18:25](https://www.youtube.com/watch?v=PxcOIINgiaA&t=1105s) | PxcOIINgiaA | 301 | 18:25 | 18:28 | And so yeah, like now LLMs are completely obsolete. |
| [18:28](https://www.youtube.com/watch?v=PxcOIINgiaA&t=1108s) | PxcOIINgiaA | 302 | 18:28 | 18:29 | We had to focus on MLMs |
| [18:29](https://www.youtube.com/watch?v=PxcOIINgiaA&t=1109s) | PxcOIINgiaA | 303 | 18:29 | 18:32 | and we'll see how our agent responds to this information |
| [18:32](https://www.youtube.com/watch?v=PxcOIINgiaA&t=1112s) | PxcOIINgiaA | 304 | 18:32 | 18:34 | being added into the knowledge graph. |
| [18:34](https://www.youtube.com/watch?v=PxcOIINgiaA&t=1114s) | PxcOIINgiaA | 305 | 18:34 | 18:35 | And so yeah, we're just connecting it to graffiti |
| [18:35](https://www.youtube.com/watch?v=PxcOIINgiaA&t=1115s) | PxcOIINgiaA | 306 | 18:35 | 18:38 | in our main function, running each of these phases |
| [18:38](https://www.youtube.com/watch?v=PxcOIINgiaA&t=1118s) | PxcOIINgiaA | 307 | 18:38 | 18:40 | and then waiting for the user to input like, |
| [18:40](https://www.youtube.com/watch?v=PxcOIINgiaA&t=1120s) | PxcOIINgiaA | 308 | 18:40 | 18:42 | yes, it's time to move on to the next phase. |
| [18:42](https://www.youtube.com/watch?v=PxcOIINgiaA&t=1122s) | PxcOIINgiaA | 309 | 18:42 | 18:44 | And we'll see this when I do a live demo with you. |
| [18:45](https://www.youtube.com/watch?v=PxcOIINgiaA&t=1125s) | PxcOIINgiaA | 310 | 18:45 | 18:47 | And then for our AI agent, |
| [18:47](https://www.youtube.com/watch?v=PxcOIINgiaA&t=1127s) | PxcOIINgiaA | 311 | 18:47 | 18:49 | it's just a simple agent built with Pydantic AI. |
| [18:49](https://www.youtube.com/watch?v=PxcOIINgiaA&t=1129s) | PxcOIINgiaA | 312 | 18:49 | 18:51 | And I'm not gonna dive into exactly |
| [18:51](https://www.youtube.com/watch?v=PxcOIINgiaA&t=1131s) | PxcOIINgiaA | 313 | 18:51 | 18:53 | how Pydantic AI works in this video. |
| [18:53](https://www.youtube.com/watch?v=PxcOIINgiaA&t=1133s) | PxcOIINgiaA | 314 | 18:53 | 18:56 | There's a lot of other content on my channel for PyDantic AI. |
| [18:56](https://www.youtube.com/watch?v=PxcOIINgiaA&t=1136s) | PxcOIINgiaA | 315 | 18:56 | 19:03 | But we have our dependencies here where we're going to pass in the Graffiti client to our agent so it can use it in its tools. |
| [19:03](https://www.youtube.com/watch?v=PxcOIINgiaA&t=1143s) | PxcOIINgiaA | 316 | 19:03 | 19:12 | We'll set up our model based on our environment variables and then create the instance of our agent itself with the dependencies here that includes our Graffiti client. |
| [19:12](https://www.youtube.com/watch?v=PxcOIINgiaA&t=1152s) | PxcOIINgiaA | 317 | 19:12 | 19:20 | And then within the single tool that we have for this agent, just keeping it very simple, it is one to call Graffiti to search our knowledge graph. |
| [19:20](https://www.youtube.com/watch?v=PxcOIINgiaA&t=1160s) | PxcOIINgiaA | 318 | 19:20 | 19:24 | And so we have the context passed in with our graffiti client, and then also the user query |
| [19:24](https://www.youtube.com/watch?v=PxcOIINgiaA&t=1164s) | PxcOIINgiaA | 319 | 19:24 | 19:29 | that the agent decides. So it will figure out what it wants to query our knowledge graph with, |
| [19:29](https://www.youtube.com/watch?v=PxcOIINgiaA&t=1169s) | PxcOIINgiaA | 320 | 19:29 | 19:33 | and then we're going to perform that graffiti search. And then very similar to our quick start, |
| [19:34](https://www.youtube.com/watch?v=PxcOIINgiaA&t=1174s) | PxcOIINgiaA | 321 | 19:34 | 19:38 | we're going to loop over all the results and create a nicely structured result to return |
| [19:38](https://www.youtube.com/watch?v=PxcOIINgiaA&t=1178s) | PxcOIINgiaA | 322 | 19:38 | 19:43 | back to our agent, where we have all the information like the fact itself, when it was |
| [19:43](https://www.youtube.com/watch?v=PxcOIINgiaA&t=1183s) | PxcOIINgiaA | 323 | 19:43 | 19:48 | inserted, and then also if the fact was invalidated, when that happened. And so all that context is |
| [19:48](https://www.youtube.com/watch?v=PxcOIINgiaA&t=1188s) | PxcOIINgiaA | 324 | 19:48 | 19:53 | give them back to our agent to reason about the facts that it wants to use to answer our question. |
| [19:54](https://www.youtube.com/watch?v=PxcOIINgiaA&t=1194s) | PxcOIINgiaA | 325 | 19:54 | 19:59 | And then in the main function, we just have a connection made to graffiti with the Neo4j, |
| [19:59](https://www.youtube.com/watch?v=PxcOIINgiaA&t=1199s) | PxcOIINgiaA | 326 | 19:59 | 20:04 | and then a simple command line interface to talk to our agent. And so I'll show you that right now. |
| [20:04](https://www.youtube.com/watch?v=PxcOIINgiaA&t=1204s) | PxcOIINgiaA | 327 | 20:04 | 20:09 | I have one terminal open where I'll talk to my agent, and then a second terminal open where I |
| [20:09](https://www.youtube.com/watch?v=PxcOIINgiaA&t=1209s) | PxcOIINgiaA | 328 | 20:09 | 20:16 | will run this LLM evolution script. And so I'll start by running agent.py. I'll just show you a |
| [20:16](https://www.youtube.com/watch?v=PxcOIINgiaA&t=1216s) | PxcOIINgiaA | 329 | 20:16 | 20:21 | very basic message to get started. I'll just say hello, nothing really right here. And then I'll |
| [20:21](https://www.youtube.com/watch?v=PxcOIINgiaA&t=1221s) | PxcOIINgiaA | 330 | 20:21 | 20:26 | just say like, what is the best LLM? And so in this case, it's going to call that tool to search |
| [20:26](https://www.youtube.com/watch?v=PxcOIINgiaA&t=1226s) | PxcOIINgiaA | 331 | 20:26 | 20:30 | our knowledge graph. Right now, there's not really a good answer that it has because we haven't run |
| [20:30](https://www.youtube.com/watch?v=PxcOIINgiaA&t=1230s) | PxcOIINgiaA | 332 | 20:30 | 20:36 | the other script yet. And so I'll do that now. I'll go Python LLM evolution.py. And so it's going |
| [20:36](https://www.youtube.com/watch?v=PxcOIINgiaA&t=1236s) | PxcOIINgiaA | 333 | 20:36 | 20:43 | to make that first set of insertions with those episodes for Claude's 3.7 Sonnet, Gemini 2.5 Pro, |
| [20:43](https://www.youtube.com/watch?v=PxcOIINgiaA&t=1243s) | PxcOIINgiaA | 334 | 20:43 | 20:45 | and then also GPT 4.1. |
| [20:45](https://www.youtube.com/watch?v=PxcOIINgiaA&t=1245s) | PxcOIINgiaA | 335 | 20:45 | 20:48 | So I'll go ahead and pause and come back once that is done. |
| [20:48](https://www.youtube.com/watch?v=PxcOIINgiaA&t=1248s) | PxcOIINgiaA | 336 | 20:48 | 20:49 | All right, there we go. |
| [20:49](https://www.youtube.com/watch?v=PxcOIINgiaA&t=1249s) | PxcOIINgiaA | 337 | 20:49 | 20:51 | We have all of our facts inserted. |
| [20:51](https://www.youtube.com/watch?v=PxcOIINgiaA&t=1251s) | PxcOIINgiaA | 338 | 20:51 | 20:54 | And so I'll even go back to Neo4j. |
| [20:54](https://www.youtube.com/watch?v=PxcOIINgiaA&t=1254s) | PxcOIINgiaA | 339 | 20:54 | 20:55 | I'll run the query again. |
| [20:55](https://www.youtube.com/watch?v=PxcOIINgiaA&t=1255s) | PxcOIINgiaA | 340 | 20:55 | 20:57 | And then boom, we have an involved knowledge graph |
| [20:57](https://www.youtube.com/watch?v=PxcOIINgiaA&t=1257s) | PxcOIINgiaA | 341 | 20:57 | 21:00 | with some information on Gemini 2.5 Pro, |
| [21:01](https://www.youtube.com/watch?v=PxcOIINgiaA&t=1261s) | PxcOIINgiaA | 342 | 21:01 | 21:03 | Claude and GPT as well. |
| [21:03](https://www.youtube.com/watch?v=PxcOIINgiaA&t=1263s) | PxcOIINgiaA | 343 | 21:03 | 21:04 | All right, looking good. |
| [21:04](https://www.youtube.com/watch?v=PxcOIINgiaA&t=1264s) | PxcOIINgiaA | 344 | 21:04 | 21:05 | So now I'll go back over to my agent |
| [21:05](https://www.youtube.com/watch?v=PxcOIINgiaA&t=1265s) | PxcOIINgiaA | 345 | 21:05 | 21:07 | and I'll ask it the same question. |
| [21:08](https://www.youtube.com/watch?v=PxcOIINgiaA&t=1268s) | PxcOIINgiaA | 346 | 21:08 | 21:09 | What is the best LLM? |
| [21:10](https://www.youtube.com/watch?v=PxcOIINgiaA&t=1270s) | PxcOIINgiaA | 347 | 21:10 | 21:12 | And there is actually conversation history here. |
| [21:12](https://www.youtube.com/watch?v=PxcOIINgiaA&t=1272s) | PxcOIINgiaA | 348 | 21:12 | 21:14 | So I don't want it to just default to using the same answer as before. |
| [21:15](https://www.youtube.com/watch?v=PxcOIINgiaA&t=1275s) | PxcOIINgiaA | 349 | 21:15 | 21:16 | So I'll say search again. |
| [21:16](https://www.youtube.com/watch?v=PxcOIINgiaA&t=1276s) | PxcOIINgiaA | 350 | 21:16 | 21:20 | So now it'll perform that search and you'll see how fast this is compared to other tools |
| [21:20](https://www.youtube.com/watch?v=PxcOIINgiaA&t=1280s) | PxcOIINgiaA | 351 | 21:20 | 21:21 | like LightRag. |
| [21:21](https://www.youtube.com/watch?v=PxcOIINgiaA&t=1281s) | PxcOIINgiaA | 352 | 21:21 | 21:22 | There we go. |
| [21:22](https://www.youtube.com/watch?v=PxcOIINgiaA&t=1282s) | PxcOIINgiaA | 353 | 21:22 | 21:22 | All right. |
| [21:22](https://www.youtube.com/watch?v=PxcOIINgiaA&t=1282s) | PxcOIINgiaA | 354 | 21:22 | 21:26 | The best large language model right now is Gemini 2.5 Pro. |
| [21:26](https://www.youtube.com/watch?v=PxcOIINgiaA&t=1286s) | PxcOIINgiaA | 355 | 21:26 | 21:28 | In just a couple of seconds, we got our answer. |
| [21:29](https://www.youtube.com/watch?v=PxcOIINgiaA&t=1289s) | PxcOIINgiaA | 356 | 21:29 | 21:29 | That's so good. |
| [21:30](https://www.youtube.com/watch?v=PxcOIINgiaA&t=1290s) | PxcOIINgiaA | 357 | 21:30 | 21:30 | All right. |
| [21:30](https://www.youtube.com/watch?v=PxcOIINgiaA&t=1290s) | PxcOIINgiaA | 358 | 21:30 | 21:36 | And so now we'll go back to my LLM evolution execution and I can just type continue to |
| [21:36](https://www.youtube.com/watch?v=PxcOIINgiaA&t=1296s) | PxcOIINgiaA | 359 | 21:36 | 21:41 | move on to adding the next set of episodes, specifically with the introduction of Clod |
| [21:41](https://www.youtube.com/watch?v=PxcOIINgiaA&t=1301s) | PxcOIINgiaA | 360 | 21:41 | 21:41 | 4. |
| [21:41](https://www.youtube.com/watch?v=PxcOIINgiaA&t=1301s) | PxcOIINgiaA | 361 | 21:41 | 21:46 | So again, I will pause and come back once that is all inserted into Neo4j. |
| [21:46](https://www.youtube.com/watch?v=PxcOIINgiaA&t=1306s) | PxcOIINgiaA | 362 | 21:46 | 21:48 | All right, the information is all inserted. |
| [21:48](https://www.youtube.com/watch?v=PxcOIINgiaA&t=1308s) | PxcOIINgiaA | 363 | 21:48 | 21:50 | Let's take a look at our knowledge graph again. |
| [21:51](https://www.youtube.com/watch?v=PxcOIINgiaA&t=1311s) | PxcOIINgiaA | 364 | 21:51 | 21:53 | And all right, it has grown even more. |
| [21:53](https://www.youtube.com/watch?v=PxcOIINgiaA&t=1313s) | PxcOIINgiaA | 365 | 21:53 | 21:54 | So where is Claude4? |
| [21:54](https://www.youtube.com/watch?v=PxcOIINgiaA&t=1314s) | PxcOIINgiaA | 366 | 21:54 | 21:56 | Okay, so we got Claude4 now. |
| [21:56](https://www.youtube.com/watch?v=PxcOIINgiaA&t=1316s) | PxcOIINgiaA | 367 | 21:56 | 21:58 | It is now the best LLM. |
| [21:58](https://www.youtube.com/watch?v=PxcOIINgiaA&t=1318s) | PxcOIINgiaA | 368 | 21:58 | 22:01 | And I don't know why we have it in two cases here. |
| [22:02](https://www.youtube.com/watch?v=PxcOIINgiaA&t=1322s) | PxcOIINgiaA | 369 | 22:02 | 22:05 | So it might be because I didn't clear everything from my quick start, maybe. |
| [22:06](https://www.youtube.com/watch?v=PxcOIINgiaA&t=1326s) | PxcOIINgiaA | 370 | 22:06 | 22:07 | I'm not entirely sure. |
| [22:07](https://www.youtube.com/watch?v=PxcOIINgiaA&t=1327s) | PxcOIINgiaA | 371 | 22:07 | 22:11 | So like I said, unpredictability of LLMs, these graphs aren't always going to look perfect, |
| [22:11](https://www.youtube.com/watch?v=PxcOIINgiaA&t=1331s) | PxcOIINgiaA | 372 | 22:11 | 22:15 | but they definitely will have the information connected in really powerful ways. |
| [22:15](https://www.youtube.com/watch?v=PxcOIINgiaA&t=1335s) | PxcOIINgiaA | 373 | 22:15 | 22:16 | And so we can even test this now. |
| [22:16](https://www.youtube.com/watch?v=PxcOIINgiaA&t=1336s) | PxcOIINgiaA | 374 | 22:16 | 22:20 | So I'll go back to my agent, and I started it from scratch here, |
| [22:20](https://www.youtube.com/watch?v=PxcOIINgiaA&t=1340s) | PxcOIINgiaA | 375 | 22:20 | 22:22 | so you don't have conversation history messing with anything. |
| [22:22](https://www.youtube.com/watch?v=PxcOIINgiaA&t=1342s) | PxcOIINgiaA | 376 | 22:22 | 22:24 | I'll just ask the same question. |
| [22:24](https://www.youtube.com/watch?v=PxcOIINgiaA&t=1344s) | PxcOIINgiaA | 377 | 22:24 | 22:26 | What is the best LLM right now? |
| [22:26](https://www.youtube.com/watch?v=PxcOIINgiaA&t=1346s) | PxcOIINgiaA | 378 | 22:26 | 22:31 | And so now instead of saying Gemini 2.5 Pro, it should say Claude 4. |
| [22:31](https://www.youtube.com/watch?v=PxcOIINgiaA&t=1351s) | PxcOIINgiaA | 379 | 22:31 | 22:33 | There we go. Claude 4 is now the best LLM. |
| [22:33](https://www.youtube.com/watch?v=PxcOIINgiaA&t=1353s) | PxcOIINgiaA | 380 | 22:33 | 22:37 | And because we are keeping a historical record of this information, |
| [22:37](https://www.youtube.com/watch?v=PxcOIINgiaA&t=1357s) | PxcOIINgiaA | 381 | 22:37 | 22:40 | and at one point Gemini 2.5 Pro was the best, |
| [22:40](https://www.youtube.com/watch?v=PxcOIINgiaA&t=1360s) | PxcOIINgiaA | 382 | 22:40 | 22:42 | It also states this. |
| [22:43](https://www.youtube.com/watch?v=PxcOIINgiaA&t=1363s) | PxcOIINgiaA | 383 | 22:43 | 22:48 | You can just tell from this answer how robust our knowledge base is behind the scenes when |
| [22:48](https://www.youtube.com/watch?v=PxcOIINgiaA&t=1368s) | PxcOIINgiaA | 384 | 22:48 | 22:52 | it is able to give this much information just based on a very simple query because it had |
| [22:52](https://www.youtube.com/watch?v=PxcOIINgiaA&t=1372s) | PxcOIINgiaA | 385 | 22:52 | 22:54 | all these facts returned to it. |
| [22:54](https://www.youtube.com/watch?v=PxcOIINgiaA&t=1374s) | PxcOIINgiaA | 386 | 22:54 | 22:59 | It had two different facts that one said this is the best LLM and the other said that Gemini |
| [22:59](https://www.youtube.com/watch?v=PxcOIINgiaA&t=1379s) | PxcOIINgiaA | 387 | 22:59 | 23:02 | 2.5 Pro was, but we look at the invalid at date. |
| [23:02](https://www.youtube.com/watch?v=PxcOIINgiaA&t=1382s) | PxcOIINgiaA | 388 | 23:02 | 23:07 | We know this is old information, so then this is our real answer, but then it still has |
| [23:07](https://www.youtube.com/watch?v=PxcOIINgiaA&t=1387s) | PxcOIINgiaA | 389 | 23:07 | 23:07 | this caveat. |
| [23:07](https://www.youtube.com/watch?v=PxcOIINgiaA&t=1387s) | PxcOIINgiaA | 390 | 23:07 | 23:11 | Like, man, I just, I appreciate this so, so much. |
| [23:11](https://www.youtube.com/watch?v=PxcOIINgiaA&t=1391s) | PxcOIINgiaA | 391 | 23:11 | 23:13 | And so then the very last test that we'll do here, |
| [23:13](https://www.youtube.com/watch?v=PxcOIINgiaA&t=1393s) | PxcOIINgiaA | 392 | 23:13 | 23:17 | we'll do continue again to add in that whole silly concept |
| [23:17](https://www.youtube.com/watch?v=PxcOIINgiaA&t=1397s) | PxcOIINgiaA | 393 | 23:17 | 23:20 | of massive language models, MLMs. |
| [23:20](https://www.youtube.com/watch?v=PxcOIINgiaA&t=1400s) | PxcOIINgiaA | 394 | 23:20 | 23:21 | So again, I'll pause and come back |
| [23:21](https://www.youtube.com/watch?v=PxcOIINgiaA&t=1401s) | PxcOIINgiaA | 395 | 23:21 | 23:23 | once we have these episodes inserted. |
| [23:24](https://www.youtube.com/watch?v=PxcOIINgiaA&t=1404s) | PxcOIINgiaA | 396 | 23:24 | 23:25 | And there we go. |
| [23:25](https://www.youtube.com/watch?v=PxcOIINgiaA&t=1405s) | PxcOIINgiaA | 397 | 23:25 | 23:27 | We have the rest of our episodes inserted. |
| [23:27](https://www.youtube.com/watch?v=PxcOIINgiaA&t=1407s) | PxcOIINgiaA | 398 | 23:27 | 23:29 | And by the way, this only takes around 20 seconds. |
| [23:29](https://www.youtube.com/watch?v=PxcOIINgiaA&t=1409s) | PxcOIINgiaA | 399 | 23:29 | 23:30 | So it's really fast, |
| [23:30](https://www.youtube.com/watch?v=PxcOIINgiaA&t=1410s) | PxcOIINgiaA | 400 | 23:30 | 23:31 | even though it is building up |
| [23:31](https://www.youtube.com/watch?v=PxcOIINgiaA&t=1411s) | PxcOIINgiaA | 401 | 23:31 | 23:34 | a lot of complex relationships under the hood. |
| [23:34](https://www.youtube.com/watch?v=PxcOIINgiaA&t=1414s) | PxcOIINgiaA | 402 | 23:34 | 23:35 | I mean, just look at how big |
| [23:35](https://www.youtube.com/watch?v=PxcOIINgiaA&t=1415s) | PxcOIINgiaA | 403 | 23:35 | 23:41 | our whole knowledge graph is now. And so we can see if I go to the episode for MLM, |
| [23:42](https://www.youtube.com/watch?v=PxcOIINgiaA&t=1422s) | PxcOIINgiaA | 404 | 23:42 | 23:47 | we have mentions large language models, as in they are no longer relevant anymore, because we have |
| [23:47](https://www.youtube.com/watch?v=PxcOIINgiaA&t=1427s) | PxcOIINgiaA | 405 | 23:47 | 23:53 | MLMs. And then we talk about massive language models, what they are, how they all relate to |
| [23:53](https://www.youtube.com/watch?v=PxcOIINgiaA&t=1433s) | PxcOIINgiaA | 406 | 23:53 | 23:57 | LLMs. Yeah, our knowledge graph is looking really good. And so I'll go back to the agent. And I'll |
| [23:57](https://www.youtube.com/watch?v=PxcOIINgiaA&t=1437s) | PxcOIINgiaA | 407 | 23:57 | 24:02 | say, what is the best LLM? And I'll just say search again. And so a couple of seconds here, |
| [24:02](https://www.youtube.com/watch?v=PxcOIINgiaA&t=1442s) | PxcOIINgiaA | 408 | 24:02 | 24:07 | we'll get our response back. All right, while clod four is currently recognized as the best LLM, |
| [24:08](https://www.youtube.com/watch?v=PxcOIINgiaA&t=1448s) | PxcOIINgiaA | 409 | 24:08 | 24:14 | now there has been a recent emergence of massive language models, MLMs. And so yeah, clod four is |
| [24:14](https://www.youtube.com/watch?v=PxcOIINgiaA&t=1454s) | PxcOIINgiaA | 410 | 24:14 | 24:19 | the best. But now LLMs just aren't the best anymore. This is just the perfect answer. I just |
| [24:19](https://www.youtube.com/watch?v=PxcOIINgiaA&t=1459s) | PxcOIINgiaA | 411 | 24:19 | 24:23 | love the caveats that we're able to get now, because we have that historical information. |
| [24:24](https://www.youtube.com/watch?v=PxcOIINgiaA&t=1464s) | PxcOIINgiaA | 412 | 24:24 | 24:28 | And so I kind of just made up this example on the spot of comparing different LLMs within |
| [24:28](https://www.youtube.com/watch?v=PxcOIINgiaA&t=1468s) | PxcOIINgiaA | 413 | 24:28 | 24:34 | graffiti here. But I think this like really, really shows the power of having a temporal aware |
| [24:34](https://www.youtube.com/watch?v=PxcOIINgiaA&t=1474s) | PxcOIINgiaA | 414 | 24:34 | 24:40 | knowledge graph. And like basically, most AI agents that you want to make with reg could benefit from |
| [24:40](https://www.youtube.com/watch?v=PxcOIINgiaA&t=1480s) | PxcOIINgiaA | 415 | 24:40 | 24:44 | this no matter the business that you're working in, you have dynamic data, like something like |
| [24:44](https://www.youtube.com/watch?v=PxcOIINgiaA&t=1484s) | PxcOIINgiaA | 416 | 24:44 | 24:51 | this is just so powerful. Now, the last thing that I really want to hit on for you is talking about |
| [24:51](https://www.youtube.com/watch?v=PxcOIINgiaA&t=1491s) | PxcOIINgiaA | 417 | 24:51 | 24:58 | using knowledge graphs alongside more traditional reg with vector databases, you don't have to pick |
| [24:58](https://www.youtube.com/watch?v=PxcOIINgiaA&t=1498s) | PxcOIINgiaA | 418 | 24:58 | 25:02 | one over the other. That's why I cover so many different strategies with RAG in general is |
| [25:02](https://www.youtube.com/watch?v=PxcOIINgiaA&t=1502s) | PxcOIINgiaA | 419 | 25:02 | 25:07 | because you can combine a lot of them together. And so I've talked about agentic RAG on my channel |
| [25:07](https://www.youtube.com/watch?v=PxcOIINgiaA&t=1507s) | PxcOIINgiaA | 420 | 25:07 | 25:12 | before. It's just the whole idea of giving your agent the ability to explore your knowledge in |
| [25:12](https://www.youtube.com/watch?v=PxcOIINgiaA&t=1512s) | PxcOIINgiaA | 421 | 25:12 | 25:18 | different ways. And this is an example of that your agent could have a tool to do a search in |
| [25:18](https://www.youtube.com/watch?v=PxcOIINgiaA&t=1518s) | PxcOIINgiaA | 422 | 25:18 | 25:23 | your knowledge graph, and then also a tool to do a search in your vector database. It's very, |
| [25:23](https://www.youtube.com/watch?v=PxcOIINgiaA&t=1523s) | PxcOIINgiaA | 423 | 25:23 | 25:28 | very powerful because sometimes information is represented better in one over the other. And so |
| [25:28](https://www.youtube.com/watch?v=PxcOIINgiaA&t=1528s) | PxcOIINgiaA | 424 | 25:28 | 25:32 | if the agent can reason like, oh, I didn't get what I needed when I searched the knowledge graph, |
| [25:32](https://www.youtube.com/watch?v=PxcOIINgiaA&t=1532s) | PxcOIINgiaA | 425 | 25:32 | 25:37 | let me now look in the vector database or vice versa. Like that'll just give you better answers |
| [25:37](https://www.youtube.com/watch?v=PxcOIINgiaA&t=1537s) | PxcOIINgiaA | 426 | 25:37 | 25:42 | overall. And so that's why I cover so many different strategies on my channel and why I'm |
| [25:42](https://www.youtube.com/watch?v=PxcOIINgiaA&t=1542s) | PxcOIINgiaA | 427 | 25:42 | 25:46 | introducing you to knowledge graphs right now. I think something like this really is what makes up |
| [25:46](https://www.youtube.com/watch?v=PxcOIINgiaA&t=1546s) | PxcOIINgiaA | 428 | 25:46 | 25:52 | the ideal rag solution for most of the agents that you want to create and graffiti being one of the |
| [25:52](https://www.youtube.com/watch?v=PxcOIINgiaA&t=1552s) | PxcOIINgiaA | 429 | 25:52 | 25:58 | best for the knowledge graph. And I just love how this temporal aware just adds so much rich context |
| [25:58](https://www.youtube.com/watch?v=PxcOIINgiaA&t=1558s) | PxcOIINgiaA | 430 | 25:58 | 26:03 | to my agents like you saw in that demo. If that doesn't sell you on the idea of at least trying |
| [26:03](https://www.youtube.com/watch?v=PxcOIINgiaA&t=1563s) | PxcOIINgiaA | 431 | 26:03 | 26:08 | out graffiti, I don't know what would it's just a fantastic platform. So there you have it a clean |
| [26:08](https://www.youtube.com/watch?v=PxcOIINgiaA&t=1568s) | PxcOIINgiaA | 432 | 26:08 | 26:13 | and simple introduction to graffiti. I just love this platform. And I'm definitely thinking about |
| [26:13](https://www.youtube.com/watch?v=PxcOIINgiaA&t=1573s) | PxcOIINgiaA | 433 | 26:13 | 26:17 | making more content on it in the future. So let me know in the comments if you'd be interested in |
| [26:17](https://www.youtube.com/watch?v=PxcOIINgiaA&t=1577s) | PxcOIINgiaA | 434 | 26:17 | 26:23 | that. I really think that for most AI agents, the ideal RAG solution has a knowledge graph |
| [26:23](https://www.youtube.com/watch?v=PxcOIINgiaA&t=1583s) | PxcOIINgiaA | 435 | 26:23 | 26:28 | as one of the search capabilities, and Graffiti is definitely one of the top contenders for a |
| [26:28](https://www.youtube.com/watch?v=PxcOIINgiaA&t=1588s) | PxcOIINgiaA | 436 | 26:28 | 26:33 | knowledge graph tool. And so if you appreciated this content and you're looking forward to more |
| [26:33](https://www.youtube.com/watch?v=PxcOIINgiaA&t=1593s) | PxcOIINgiaA | 437 | 26:33 | 26:38 | things RAG and AI agents, I would really appreciate a like and a subscribe. And with that, I will see |
| [26:38](https://www.youtube.com/watch?v=PxcOIINgiaA&t=1598s) | PxcOIINgiaA | 438 | 26:38 | 26:39 | you in the next video. |
