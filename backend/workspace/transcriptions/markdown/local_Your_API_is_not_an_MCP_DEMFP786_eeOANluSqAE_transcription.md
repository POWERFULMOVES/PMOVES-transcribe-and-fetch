# Transcription for Video: [eeOANluSqAE](https://www.youtube.com/watch?v=eeOANluSqAE)

| Timestamp Link | Video ID | Seg ID | Start | End | Text |
|---|---|---|---|---|---|
| [00:00](https://www.youtube.com/watch?v=eeOANluSqAE&t=0s) | eeOANluSqAE | 0 | 00:00 | 00:04 | All right. Nice to see you, everyone. Thank you for joining. |
| [00:05](https://www.youtube.com/watch?v=eeOANluSqAE&t=5s) | eeOANluSqAE | 1 | 00:05 | 00:07 | My name is David. I work at a company called Neon. |
| [00:08](https://www.youtube.com/watch?v=eeOANluSqAE&t=8s) | eeOANluSqAE | 2 | 00:08 | 00:10 | We're a serverless Postgres provider. |
| [00:10](https://www.youtube.com/watch?v=eeOANluSqAE&t=10s) | eeOANluSqAE | 3 | 00:10 | 00:14 | So the people want Postgres, we give them Postgres. |
| [00:15](https://www.youtube.com/watch?v=eeOANluSqAE&t=15s) | eeOANluSqAE | 4 | 00:15 | 00:17 | And today I'm going to be talking about MCP servers. |
| [00:18](https://www.youtube.com/watch?v=eeOANluSqAE&t=18s) | eeOANluSqAE | 5 | 00:18 | 00:25 | In specific, I'm going to be talking about how not to build MCP servers |
| [00:26](https://www.youtube.com/watch?v=eeOANluSqAE&t=26s) | eeOANluSqAE | 6 | 00:26 | 00:31 | and then how to actually go about it in the right way. |
| [00:32](https://www.youtube.com/watch?v=eeOANluSqAE&t=32s) | eeOANluSqAE | 7 | 00:32 | 00:41 | So if you're unfamiliar with MCP, it's a new protocol that was developed by Anthropic, |
| [00:42](https://www.youtube.com/watch?v=eeOANluSqAE&t=42s) | eeOANluSqAE | 8 | 00:42 | 00:50 | which is a way for LLMs to be able to interface with real-world apps and services. |
| [00:50](https://www.youtube.com/watch?v=eeOANluSqAE&t=50s) | eeOANluSqAE | 9 | 00:50 | 00:58 | So essentially, it's an open protocol that standardizes how applications provide context to LLMs |
| [00:58](https://www.youtube.com/watch?v=eeOANluSqAE&t=58s) | eeOANluSqAE | 10 | 00:58 | 01:02 | and how LLMs can use real-world products. |
| [01:02](https://www.youtube.com/watch?v=eeOANluSqAE&t=62s) | eeOANluSqAE | 11 | 01:02 | 01:06 | It's very new. |
| [01:06](https://www.youtube.com/watch?v=eeOANluSqAE&t=66s) | eeOANluSqAE | 12 | 01:06 | 01:09 | It's about six, seven months old, |
| [01:09](https://www.youtube.com/watch?v=eeOANluSqAE&t=69s) | eeOANluSqAE | 13 | 01:09 | 01:11 | but it's getting tremendous adoption. |
| [01:12](https://www.youtube.com/watch?v=eeOANluSqAE&t=72s) | eeOANluSqAE | 14 | 01:12 | 01:14 | So if you saw the keynote yesterday from Satya, |
| [01:15](https://www.youtube.com/watch?v=eeOANluSqAE&t=75s) | eeOANluSqAE | 15 | 01:15 | 01:19 | the Windows co-pilot will become an NCP client soon. |
| [01:19](https://www.youtube.com/watch?v=eeOANluSqAE&t=79s) | eeOANluSqAE | 16 | 01:19 | 01:23 | Just today in the morning at Google Code, |
| [01:23](https://www.youtube.com/watch?v=eeOANluSqAE&t=83s) | eeOANluSqAE | 17 | 01:23 | 01:25 | they announced, or Google I.O. rather, |
| [01:25](https://www.youtube.com/watch?v=eeOANluSqAE&t=85s) | eeOANluSqAE | 18 | 01:25 | 01:29 | they announced that Gemini will support NCP as well. |
| [01:29](https://www.youtube.com/watch?v=eeOANluSqAE&t=89s) | eeOANluSqAE | 19 | 01:29 | 01:30 | OpenAI already supports NCP, |
| [01:30](https://www.youtube.com/watch?v=eeOANluSqAE&t=90s) | eeOANluSqAE | 20 | 01:30 | 01:34 | and Cloud, of course, has supported MCP from the beginning. |
| [01:35](https://www.youtube.com/watch?v=eeOANluSqAE&t=95s) | eeOANluSqAE | 21 | 01:35 | 01:36 | What does that mean? |
| [01:36](https://www.youtube.com/watch?v=eeOANluSqAE&t=96s) | eeOANluSqAE | 22 | 01:36 | 01:38 | It means that if you're building an app or a service |
| [01:38](https://www.youtube.com/watch?v=eeOANluSqAE&t=98s) | eeOANluSqAE | 23 | 01:38 | 01:42 | and you want LLMs to use your app, you need an MCP server. |
| [01:44](https://www.youtube.com/watch?v=eeOANluSqAE&t=104s) | eeOANluSqAE | 24 | 01:44 | 01:50 | So this has led to a lot of companies building MCP servers in a rush |
| [01:50](https://www.youtube.com/watch?v=eeOANluSqAE&t=110s) | eeOANluSqAE | 25 | 01:50 | 01:56 | in order to make their services available to LLMs like Cloud and OpenAI's chat GPT. |
| [01:56](https://www.youtube.com/watch?v=eeOANluSqAE&t=116s) | eeOANluSqAE | 26 | 01:56 | 01:58 | So let's break it down. |
| [01:58](https://www.youtube.com/watch?v=eeOANluSqAE&t=118s) | eeOANluSqAE | 27 | 01:58 | 02:00 | What makes up an MCP server? |
| [02:00](https://www.youtube.com/watch?v=eeOANluSqAE&t=120s) | eeOANluSqAE | 28 | 02:00 | 02:06 | MCP servers have tools, resources, and prompts. |
| [02:06](https://www.youtube.com/watch?v=eeOANluSqAE&t=126s) | eeOANluSqAE | 29 | 02:06 | 02:11 | These are the three main concepts of an MCP server. |
| [02:11](https://www.youtube.com/watch?v=eeOANluSqAE&t=131s) | eeOANluSqAE | 30 | 02:11 | 02:15 | And these are the things that an MCP server exposes |
| [02:15](https://www.youtube.com/watch?v=eeOANluSqAE&t=135s) | eeOANluSqAE | 31 | 02:15 | 02:18 | to the underlying LLM, which is the MCP client. |
| [02:18](https://www.youtube.com/watch?v=eeOANluSqAE&t=138s) | eeOANluSqAE | 32 | 02:18 | 02:22 | The most important of these by far are the tools. |
| [02:22](https://www.youtube.com/watch?v=eeOANluSqAE&t=142s) | eeOANluSqAE | 33 | 02:22 | 02:25 | Tools, you can think of them as actions. |
| [02:25](https://www.youtube.com/watch?v=eeOANluSqAE&t=145s) | eeOANluSqAE | 34 | 02:25 | 02:29 | These are things that the LLM might want to perform. |
| [02:29](https://www.youtube.com/watch?v=eeOANluSqAE&t=149s) | eeOANluSqAE | 35 | 02:29 | 02:31 | An example would be if you're building |
| [02:31](https://www.youtube.com/watch?v=eeOANluSqAE&t=151s) | eeOANluSqAE | 36 | 02:31 | 02:36 | an e-commerce website to buy an item on your website. |
| [02:36](https://www.youtube.com/watch?v=eeOANluSqAE&t=156s) | eeOANluSqAE | 37 | 02:36 | 02:39 | In our case, we're a Postgres provider. |
| [02:39](https://www.youtube.com/watch?v=eeOANluSqAE&t=159s) | eeOANluSqAE | 38 | 02:39 | 02:41 | We give people Postgres. |
| [02:41](https://www.youtube.com/watch?v=eeOANluSqAE&t=161s) | eeOANluSqAE | 39 | 02:41 | 02:45 | An example of a tool would be to create a Postgres database. |
| [02:45](https://www.youtube.com/watch?v=eeOANluSqAE&t=165s) | eeOANluSqAE | 40 | 02:45 | 02:49 | This would be a request that comes in from the LLM. |
| [02:49](https://www.youtube.com/watch?v=eeOANluSqAE&t=169s) | eeOANluSqAE | 41 | 02:49 | 02:55 | The resources and prompts are not as interesting, |
| [02:55](https://www.youtube.com/watch?v=eeOANluSqAE&t=175s) | eeOANluSqAE | 42 | 02:55 | 02:59 | so I won't spend any time on them today. |
| [02:59](https://www.youtube.com/watch?v=eeOANluSqAE&t=179s) | eeOANluSqAE | 43 | 02:59 | 03:06 | If the concept of an MCP server still hasn't permeated, |
| [03:06](https://www.youtube.com/watch?v=eeOANluSqAE&t=186s) | eeOANluSqAE | 44 | 03:06 | 03:09 | it can be like a tricky thing to really understand. |
| [03:10](https://www.youtube.com/watch?v=eeOANluSqAE&t=190s) | eeOANluSqAE | 45 | 03:10 | 03:16 | I have a very quick demo here of Neon's MCP server in production. |
| [03:17](https://www.youtube.com/watch?v=eeOANluSqAE&t=197s) | eeOANluSqAE | 46 | 03:17 | 03:27 | So I have a video here of a Cursor user asking Cursor to create an application using Neon. |
| [03:27](https://www.youtube.com/watch?v=eeOANluSqAE&t=207s) | eeOANluSqAE | 47 | 03:27 | 03:30 | And what Cursor will do, and I know you can't see the video, |
| [03:30](https://www.youtube.com/watch?v=eeOANluSqAE&t=210s) | eeOANluSqAE | 48 | 03:30 | 03:38 | But what Cursor will do is it'll interface with our MCP server in order to request a Postgres database, |
| [03:38](https://www.youtube.com/watch?v=eeOANluSqAE&t=218s) | eeOANluSqAE | 49 | 03:38 | 03:42 | and it will then use said Postgres database to create an application. |
| [03:43](https://www.youtube.com/watch?v=eeOANluSqAE&t=223s) | eeOANluSqAE | 50 | 03:43 | 03:50 | So if you look at the prompt there, it says, build me a to-do list app, use Neon Postgres and use Neon Auth. |
| [03:50](https://www.youtube.com/watch?v=eeOANluSqAE&t=230s) | eeOANluSqAE | 51 | 03:50 | 03:58 | And what Cursor will do is it'll use our MCP server to provision a Postgres database with Neon Auth. |
| [03:58](https://www.youtube.com/watch?v=eeOANluSqAE&t=238s) | eeOANluSqAE | 52 | 03:58 | 04:02 | and in just a few minutes, the application will be fully functional |
| [04:02](https://www.youtube.com/watch?v=eeOANluSqAE&t=242s) | eeOANluSqAE | 53 | 04:02 | 04:06 | and have a real database, a real physical Postgres database, |
| [04:07](https://www.youtube.com/watch?v=eeOANluSqAE&t=247s) | eeOANluSqAE | 54 | 04:07 | 04:09 | thanks to our MCP server. |
| [04:10](https://www.youtube.com/watch?v=eeOANluSqAE&t=250s) | eeOANluSqAE | 55 | 04:10 | 04:13 | So MCP is awesome. |
| [04:13](https://www.youtube.com/watch?v=eeOANluSqAE&t=253s) | eeOANluSqAE | 56 | 04:13 | 04:15 | I think we've established that. |
| [04:16](https://www.youtube.com/watch?v=eeOANluSqAE&t=256s) | eeOANluSqAE | 57 | 04:16 | 04:21 | The problem now is creating an MCP server is a lot of work. |
| [04:21](https://www.youtube.com/watch?v=eeOANluSqAE&t=261s) | eeOANluSqAE | 58 | 04:21 | 04:24 | Our MCP server, which is actually open source, |
| [04:25](https://www.youtube.com/watch?v=eeOANluSqAE&t=265s) | eeOANluSqAE | 59 | 04:25 | 04:28 | is around 500 lines of code. |
| [04:28](https://www.youtube.com/watch?v=eeOANluSqAE&t=268s) | eeOANluSqAE | 60 | 04:28 | 04:32 | So it's not that large, but it's still, you know, |
| [04:32](https://www.youtube.com/watch?v=eeOANluSqAE&t=272s) | eeOANluSqAE | 61 | 04:32 | 04:34 | a significant amount of work to put it together. |
| [04:35](https://www.youtube.com/watch?v=eeOANluSqAE&t=275s) | eeOANluSqAE | 62 | 04:35 | 04:36 | You have to write tests. |
| [04:36](https://www.youtube.com/watch?v=eeOANluSqAE&t=276s) | eeOANluSqAE | 63 | 04:36 | 04:37 | You have to think of it. |
| [04:37](https://www.youtube.com/watch?v=eeOANluSqAE&t=277s) | eeOANluSqAE | 64 | 04:37 | 04:40 | And so a lot of companies have decided |
| [04:40](https://www.youtube.com/watch?v=eeOANluSqAE&t=280s) | eeOANluSqAE | 65 | 04:40 | 04:43 | to just auto-generate their MCP server. |
| [04:44](https://www.youtube.com/watch?v=eeOANluSqAE&t=284s) | eeOANluSqAE | 66 | 04:44 | 04:47 | And in fact, a lot of services recently came out |
| [04:47](https://www.youtube.com/watch?v=eeOANluSqAE&t=287s) | eeOANluSqAE | 67 | 04:47 | 04:48 | that help you do this. |
| [04:48](https://www.youtube.com/watch?v=eeOANluSqAE&t=288s) | eeOANluSqAE | 68 | 04:48 | 04:49 | So how does that work? |
| [04:50](https://www.youtube.com/watch?v=eeOANluSqAE&t=290s) | eeOANluSqAE | 69 | 04:50 | 04:54 | Every API has an OpenAPI spec, |
| [04:54](https://www.youtube.com/watch?v=eeOANluSqAE&t=294s) | eeOANluSqAE | 70 | 04:54 | 04:55 | an OpenAPI schema, |
| [04:55](https://www.youtube.com/watch?v=eeOANluSqAE&t=295s) | eeOANluSqAE | 71 | 04:55 | 04:57 | which describes all the endpoints, |
| [04:58](https://www.youtube.com/watch?v=eeOANluSqAE&t=298s) | eeOANluSqAE | 72 | 04:58 | 05:00 | the inputs and outputs to all of those endpoints. |
| [05:00](https://www.youtube.com/watch?v=eeOANluSqAE&t=300s) | eeOANluSqAE | 73 | 05:00 | 05:13 | In theory, well, not just in theory, I mean, quite simply, one could take an OpenAI, OpenAPI schema and just auto-generate an MCP server. |
| [05:15](https://www.youtube.com/watch?v=eeOANluSqAE&t=315s) | eeOANluSqAE | 74 | 05:15 | 05:16 | Siri got in the way. |
| [05:20](https://www.youtube.com/watch?v=eeOANluSqAE&t=320s) | eeOANluSqAE | 75 | 05:20 | 05:23 | You can just take an OpenAPI schema and auto-generate an MCP server. |
| [05:23](https://www.youtube.com/watch?v=eeOANluSqAE&t=323s) | eeOANluSqAE | 76 | 05:23 | 05:24 | It's very easy. |
| [05:24](https://www.youtube.com/watch?v=eeOANluSqAE&t=324s) | eeOANluSqAE | 77 | 05:24 | 05:26 | It'll take less than a minute. |
| [05:26](https://www.youtube.com/watch?v=eeOANluSqAE&t=326s) | eeOANluSqAE | 78 | 05:26 | 05:29 | And then you have an MCP server. |
| [05:29](https://www.youtube.com/watch?v=eeOANluSqAE&t=329s) | eeOANluSqAE | 79 | 05:29 | 05:35 | Now, the problem with this is that it isn't quite right. |
| [05:35](https://www.youtube.com/watch?v=eeOANluSqAE&t=335s) | eeOANluSqAE | 80 | 05:35 | 05:40 | So while it is very easy, and like I said, there's a bunch of services like Stainless, |
| [05:40](https://www.youtube.com/watch?v=eeOANluSqAE&t=340s) | eeOANluSqAE | 81 | 05:40 | 05:47 | BigEasy, Mintlify, and there's even a few more, it isn't the right thing to do. |
| [05:47](https://www.youtube.com/watch?v=eeOANluSqAE&t=347s) | eeOANluSqAE | 82 | 05:47 | 05:49 | Let's talk about why. |
| [05:51](https://www.youtube.com/watch?v=eeOANluSqAE&t=351s) | eeOANluSqAE | 83 | 05:51 | 05:56 | The first problem is that APIs tend to be very extensive. |
| [05:57](https://www.youtube.com/watch?v=eeOANluSqAE&t=357s) | eeOANluSqAE | 84 | 05:57 | 06:03 | In the case of Neon's API, we have around 75 to 100 different endpoints. |
| [06:04](https://www.youtube.com/watch?v=eeOANluSqAE&t=364s) | eeOANluSqAE | 85 | 06:04 | 06:07 | I'm not showing them all on the slide, but we have a lot of endpoints. |
| [06:08](https://www.youtube.com/watch?v=eeOANluSqAE&t=368s) | eeOANluSqAE | 86 | 06:08 | 06:11 | And LLMs are really, really terrible |
| [06:11](https://www.youtube.com/watch?v=eeOANluSqAE&t=371s) | eeOANluSqAE | 87 | 06:11 | 06:15 | at choosing from a long list of tools. |
| [06:15](https://www.youtube.com/watch?v=eeOANluSqAE&t=375s) | eeOANluSqAE | 88 | 06:15 | 06:17 | So if you give them too much choice, |
| [06:17](https://www.youtube.com/watch?v=eeOANluSqAE&t=377s) | eeOANluSqAE | 89 | 06:17 | 06:18 | they won't really know what to do. |
| [06:18](https://www.youtube.com/watch?v=eeOANluSqAE&t=378s) | eeOANluSqAE | 90 | 06:18 | 06:20 | They'll get very confused. |
| [06:20](https://www.youtube.com/watch?v=eeOANluSqAE&t=380s) | eeOANluSqAE | 91 | 06:20 | 06:24 | Even though context windows have been increasing |
| [06:24](https://www.youtube.com/watch?v=eeOANluSqAE&t=384s) | eeOANluSqAE | 92 | 06:24 | 06:25 | and you hear about a million tokens, |
| [06:25](https://www.youtube.com/watch?v=eeOANluSqAE&t=385s) | eeOANluSqAE | 93 | 06:25 | 06:30 | 5 million tokens, unlimited token context window, |
| [06:30](https://www.youtube.com/watch?v=eeOANluSqAE&t=390s) | eeOANluSqAE | 94 | 06:30 | 06:34 | that doesn't mean that an LLM performs just as well |
| [06:34](https://www.youtube.com/watch?v=eeOANluSqAE&t=394s) | eeOANluSqAE | 95 | 06:34 | 06:37 | with a large context than it does with a smaller context. |
| [06:37](https://www.youtube.com/watch?v=eeOANluSqAE&t=397s) | eeOANluSqAE | 96 | 06:37 | 06:39 | In fact, the opposite is true. |
| [06:39](https://www.youtube.com/watch?v=eeOANluSqAE&t=399s) | eeOANluSqAE | 97 | 06:39 | 06:43 | LLMs perform much better with a reduced context size. |
| [06:43](https://www.youtube.com/watch?v=eeOANluSqAE&t=403s) | eeOANluSqAE | 98 | 06:43 | 06:45 | So if you give them too many tools, |
| [06:45](https://www.youtube.com/watch?v=eeOANluSqAE&t=405s) | eeOANluSqAE | 99 | 06:45 | 06:46 | they won't know what to do. |
| [06:46](https://www.youtube.com/watch?v=eeOANluSqAE&t=406s) | eeOANluSqAE | 100 | 06:46 | 06:50 | So if you auto-generate MCP server, |
| [06:50](https://www.youtube.com/watch?v=eeOANluSqAE&t=410s) | eeOANluSqAE | 101 | 06:50 | 06:55 | you're gonna get all of your API endpoints as MCP tools |
| [06:55](https://www.youtube.com/watch?v=eeOANluSqAE&t=415s) | eeOANluSqAE | 102 | 06:55 | 07:00 | and LLMs will not perform well against your service. |
| [07:00](https://www.youtube.com/watch?v=eeOANluSqAE&t=420s) | eeOANluSqAE | 103 | 07:00 | 07:03 | So you have to make a choice here. |
| [07:03](https://www.youtube.com/watch?v=eeOANluSqAE&t=423s) | eeOANluSqAE | 104 | 07:03 | 07:07 | Then the second problem is that API descriptions |
| [07:07](https://www.youtube.com/watch?v=eeOANluSqAE&t=427s) | eeOANluSqAE | 105 | 07:07 | 07:12 | in your existing API are probably not that well written |
| [07:12](https://www.youtube.com/watch?v=eeOANluSqAE&t=432s) | eeOANluSqAE | 106 | 07:12 | 07:13 | for LLMs. |
| [07:13](https://www.youtube.com/watch?v=eeOANluSqAE&t=433s) | eeOANluSqAE | 107 | 07:13 | 07:16 | This is sometimes more true than others, |
| [07:16](https://www.youtube.com/watch?v=eeOANluSqAE&t=436s) | eeOANluSqAE | 108 | 07:16 | 07:18 | but for the most part, in my experience, |
| [07:19](https://www.youtube.com/watch?v=eeOANluSqAE&t=439s) | eeOANluSqAE | 109 | 07:19 | 07:23 | API endpoints are written for humans who can Google things |
| [07:23](https://www.youtube.com/watch?v=eeOANluSqAE&t=443s) | eeOANluSqAE | 110 | 07:23 | 07:25 | and can reason about things, |
| [07:25](https://www.youtube.com/watch?v=eeOANluSqAE&t=445s) | eeOANluSqAE | 111 | 07:25 | 07:29 | but LLMs need you to be a lot more direct with them. |
| [07:29](https://www.youtube.com/watch?v=eeOANluSqAE&t=449s) | eeOANluSqAE | 112 | 07:29 | 07:34 | And also LLMs need examples much more than humans do. |
| [07:34](https://www.youtube.com/watch?v=eeOANluSqAE&t=454s) | eeOANluSqAE | 113 | 07:34 | 07:37 | So in our case, for our MCP server, |
| [07:37](https://www.youtube.com/watch?v=eeOANluSqAE&t=457s) | eeOANluSqAE | 114 | 07:37 | 07:41 | Our tool descriptions are actually written in XML |
| [07:41](https://www.youtube.com/watch?v=eeOANluSqAE&t=461s) | eeOANluSqAE | 115 | 07:41 | 07:46 | and we write them in this very organized manner |
| [07:46](https://www.youtube.com/watch?v=eeOANluSqAE&t=466s) | eeOANluSqAE | 116 | 07:46 | 07:50 | and we try to give the LLM as much context as possible |
| [07:50](https://www.youtube.com/watch?v=eeOANluSqAE&t=470s) | eeOANluSqAE | 117 | 07:50 | 07:54 | about each individual tool and when to use it, |
| [07:54](https://www.youtube.com/watch?v=eeOANluSqAE&t=474s) | eeOANluSqAE | 118 | 07:54 | 07:56 | which is something that you probably |
| [07:56](https://www.youtube.com/watch?v=eeOANluSqAE&t=476s) | eeOANluSqAE | 119 | 07:56 | 07:58 | are not doing in your APIs today. |
| [07:58](https://www.youtube.com/watch?v=eeOANluSqAE&t=478s) | eeOANluSqAE | 120 | 07:58 | 08:02 | So in a way, writing for an LLM is different |
| [08:02](https://www.youtube.com/watch?v=eeOANluSqAE&t=482s) | eeOANluSqAE | 121 | 08:02 | 08:04 | than writing for a human, |
| [08:04](https://www.youtube.com/watch?v=eeOANluSqAE&t=484s) | eeOANluSqAE | 122 | 08:04 | 08:07 | which is why you want to think about |
| [08:07](https://www.youtube.com/watch?v=eeOANluSqAE&t=487s) | eeOANluSqAE | 123 | 08:07 | 08:11 | how to write the descriptions of all of your MCP tools |
| [08:11](https://www.youtube.com/watch?v=eeOANluSqAE&t=491s) | eeOANluSqAE | 124 | 08:11 | 08:12 | for LLMs. |
| [08:12](https://www.youtube.com/watch?v=eeOANluSqAE&t=492s) | eeOANluSqAE | 125 | 08:12 | 08:15 | And then what you should also think about doing |
| [08:15](https://www.youtube.com/watch?v=eeOANluSqAE&t=495s) | eeOANluSqAE | 126 | 08:15 | 08:17 | is writing tests for this. |
| [08:17](https://www.youtube.com/watch?v=eeOANluSqAE&t=497s) | eeOANluSqAE | 127 | 08:17 | 08:22 | So we have evals, which are basically tests in the AI world. |
| [08:22](https://www.youtube.com/watch?v=eeOANluSqAE&t=502s) | eeOANluSqAE | 128 | 08:22 | 08:26 | We have evals to make sure that LLMs |
| [08:26](https://www.youtube.com/watch?v=eeOANluSqAE&t=506s) | eeOANluSqAE | 129 | 08:26 | 08:29 | are calling the right tool for the right job. |
| [08:29](https://www.youtube.com/watch?v=eeOANluSqAE&t=509s) | eeOANluSqAE | 130 | 08:29 | 08:33 | And we run these evals 100, 1,000, 10,000 times, |
| [08:33](https://www.youtube.com/watch?v=eeOANluSqAE&t=513s) | eeOANluSqAE | 131 | 08:33 | 08:36 | because obviously LLMs are not deterministic. |
| [08:36](https://www.youtube.com/watch?v=eeOANluSqAE&t=516s) | eeOANluSqAE | 132 | 08:36 | 08:39 | and we make sure that the tools that we're exposing |
| [08:39](https://www.youtube.com/watch?v=eeOANluSqAE&t=519s) | eeOANluSqAE | 133 | 08:39 | 08:43 | to the LLM have good descriptions. |
| [08:43](https://www.youtube.com/watch?v=eeOANluSqAE&t=523s) | eeOANluSqAE | 134 | 08:43 | 08:48 | And we iterate on these descriptions as our evals evolve. |
| [08:48](https://www.youtube.com/watch?v=eeOANluSqAE&t=528s) | eeOANluSqAE | 135 | 08:48 | 08:53 | The third problem is that most APIs out there today |
| [08:53](https://www.youtube.com/watch?v=eeOANluSqAE&t=533s) | eeOANluSqAE | 136 | 08:53 | 08:56 | are designed for low level resource management |
| [08:56](https://www.youtube.com/watch?v=eeOANluSqAE&t=536s) | eeOANluSqAE | 137 | 08:56 | 08:58 | and automation. |
| [08:58](https://www.youtube.com/watch?v=eeOANluSqAE&t=538s) | eeOANluSqAE | 138 | 08:58 | 09:03 | The reason most of businesses have an API |
| [09:03](https://www.youtube.com/watch?v=eeOANluSqAE&t=543s) | eeOANluSqAE | 139 | 09:03 | 09:08 | are for developers to go and use those APIs for automation. |
| [09:08](https://www.youtube.com/watch?v=eeOANluSqAE&t=548s) | eeOANluSqAE | 140 | 09:08 | 09:12 | But this is not what LLMs need from an API. |
| [09:12](https://www.youtube.com/watch?v=eeOANluSqAE&t=552s) | eeOANluSqAE | 141 | 09:12 | 09:16 | LLMs need tasks, they need actions and tools. |
| [09:16](https://www.youtube.com/watch?v=eeOANluSqAE&t=556s) | eeOANluSqAE | 142 | 09:16 | 09:19 | LLMs are much more human-like in that sense. |
| [09:19](https://www.youtube.com/watch?v=eeOANluSqAE&t=559s) | eeOANluSqAE | 143 | 09:19 | 09:21 | And so an LLM doesn't really care |
| [09:21](https://www.youtube.com/watch?v=eeOANluSqAE&t=561s) | eeOANluSqAE | 144 | 09:21 | 09:26 | about like low level resource creation. |
| [09:26](https://www.youtube.com/watch?v=eeOANluSqAE&t=566s) | eeOANluSqAE | 145 | 09:26 | 09:28 | It cares about achieving a specific goal. |
| [09:28](https://www.youtube.com/watch?v=eeOANluSqAE&t=568s) | eeOANluSqAE | 146 | 09:28 | 09:32 | And so when you design an MCP server, |
| [09:32](https://www.youtube.com/watch?v=eeOANluSqAE&t=572s) | eeOANluSqAE | 147 | 09:32 | 09:34 | when you design the list of tools, |
| [09:34](https://www.youtube.com/watch?v=eeOANluSqAE&t=574s) | eeOANluSqAE | 148 | 09:34 | 09:39 | you need to design that with that in mind. |
| [09:39](https://www.youtube.com/watch?v=eeOANluSqAE&t=579s) | eeOANluSqAE | 149 | 09:39 | 09:42 | And this is not what you do with an API. |
| [09:42](https://www.youtube.com/watch?v=eeOANluSqAE&t=582s) | eeOANluSqAE | 150 | 09:42 | 09:45 | And that's part of the reason why Anthropic decided |
| [09:45](https://www.youtube.com/watch?v=eeOANluSqAE&t=585s) | eeOANluSqAE | 151 | 09:45 | 09:46 | to create MCP in the first place, |
| [09:46](https://www.youtube.com/watch?v=eeOANluSqAE&t=586s) | eeOANluSqAE | 152 | 09:46 | 09:50 | is because open API schemas out there today |
| [09:50](https://www.youtube.com/watch?v=eeOANluSqAE&t=590s) | eeOANluSqAE | 153 | 09:50 | 09:55 | are not really prepared for this kind of design. |
| [09:55](https://www.youtube.com/watch?v=eeOANluSqAE&t=595s) | eeOANluSqAE | 154 | 09:55 | 09:57 | And then finally, if you just take your API |
| [09:57](https://www.youtube.com/watch?v=eeOANluSqAE&t=597s) | eeOANluSqAE | 155 | 09:57 | 09:59 | and expose it as an MCP, |
| [09:59](https://www.youtube.com/watch?v=eeOANluSqAE&t=599s) | eeOANluSqAE | 156 | 09:59 | 10:01 | you're missing out on the potential |
| [10:01](https://www.youtube.com/watch?v=eeOANluSqAE&t=601s) | eeOANluSqAE | 157 | 10:01 | 10:04 | to create many more interesting things. |
| [10:05](https://www.youtube.com/watch?v=eeOANluSqAE&t=605s) | eeOANluSqAE | 158 | 10:05 | 10:09 | And I'll walk you through an example from our MCP server. |
| [10:09](https://www.youtube.com/watch?v=eeOANluSqAE&t=609s) | eeOANluSqAE | 159 | 10:09 | 10:12 | So one of the things that LLMs need to do |
| [10:12](https://www.youtube.com/watch?v=eeOANluSqAE&t=612s) | eeOANluSqAE | 160 | 10:12 | 10:15 | when they're building an app is do database migrations. |
| [10:15](https://www.youtube.com/watch?v=eeOANluSqAE&t=615s) | eeOANluSqAE | 161 | 10:15 | 10:19 | That's true about humans, that's true about LLMs. |
| [10:19](https://www.youtube.com/watch?v=eeOANluSqAE&t=619s) | eeOANluSqAE | 162 | 10:19 | 10:23 | And so we have to expose this in our MCP server |
| [10:23](https://www.youtube.com/watch?v=eeOANluSqAE&t=623s) | eeOANluSqAE | 163 | 10:23 | 10:26 | so that LLMs using Neon for Postgres |
| [10:26](https://www.youtube.com/watch?v=eeOANluSqAE&t=626s) | eeOANluSqAE | 164 | 10:26 | 10:28 | can do database migrations. |
| [10:28](https://www.youtube.com/watch?v=eeOANluSqAE&t=628s) | eeOANluSqAE | 165 | 10:28 | 10:31 | The naive approach is to expose a single tool |
| [10:31](https://www.youtube.com/watch?v=eeOANluSqAE&t=631s) | eeOANluSqAE | 166 | 10:31 | 10:35 | called run SQL and then expect LLMs to call that tool |
| [10:35](https://www.youtube.com/watch?v=eeOANluSqAE&t=635s) | eeOANluSqAE | 167 | 10:35 | 10:38 | to do database migrations. |
| [10:38](https://www.youtube.com/watch?v=eeOANluSqAE&t=638s) | eeOANluSqAE | 168 | 10:38 | 10:40 | So if we have a tool called run SQL, |
| [10:40](https://www.youtube.com/watch?v=eeOANluSqAE&t=640s) | eeOANluSqAE | 169 | 10:40 | 10:42 | which we actually do in our MCP server, |
| [10:42](https://www.youtube.com/watch?v=eeOANluSqAE&t=642s) | eeOANluSqAE | 170 | 10:42 | 10:48 | an LLM can go and use it and pass through any alter table statements that it wants |
| [10:48](https://www.youtube.com/watch?v=eeOANluSqAE&t=648s) | eeOANluSqAE | 171 | 10:48 | 10:51 | and just do database migrations like that. |
| [10:51](https://www.youtube.com/watch?v=eeOANluSqAE&t=651s) | eeOANluSqAE | 172 | 10:51 | 10:59 | But it's a lot more interesting to use the opportunity that you're developing an MCP server |
| [10:59](https://www.youtube.com/watch?v=eeOANluSqAE&t=659s) | eeOANluSqAE | 173 | 10:59 | 11:03 | to think about doing more than just the basic. |
| [11:04](https://www.youtube.com/watch?v=eeOANluSqAE&t=664s) | eeOANluSqAE | 174 | 11:04 | 11:07 | So when we created our MCP server, |
| [11:08](https://www.youtube.com/watch?v=eeOANluSqAE&t=668s) | eeOANluSqAE | 175 | 11:08 | 11:13 | we decided to expose purpose-built MCP tools for database migrations. |
| [11:13](https://www.youtube.com/watch?v=eeOANluSqAE&t=673s) | eeOANluSqAE | 176 | 11:13 | 11:18 | So we have a prepared database migration tool and we have a complete database migration tool. |
| [11:19](https://www.youtube.com/watch?v=eeOANluSqAE&t=679s) | eeOANluSqAE | 177 | 11:19 | 11:26 | And LLMs are eager to use these tools over the run SQL tool. |
| [11:26](https://www.youtube.com/watch?v=eeOANluSqAE&t=686s) | eeOANluSqAE | 178 | 11:26 | 11:32 | We actually encourage LLMs to use these tools if they're wanting to do database migrations on their Neon database. |
| [11:33](https://www.youtube.com/watch?v=eeOANluSqAE&t=693s) | eeOANluSqAE | 179 | 11:33 | 11:41 | And the way it works is the first tool sort of stages the database migration on a temporary Neon branch. |
| [11:41](https://www.youtube.com/watch?v=eeOANluSqAE&t=701s) | eeOANluSqAE | 180 | 11:41 | 11:51 | And then once that's done, we actually respond back to the LLM and say, hey, the database migration you're trying to run is now staged on this branch. |
| [11:51](https://www.youtube.com/watch?v=eeOANluSqAE&t=711s) | eeOANluSqAE | 181 | 11:51 | 11:55 | Please go and test the migration before you commit it. |
| [11:56](https://www.youtube.com/watch?v=eeOANluSqAE&t=716s) | eeOANluSqAE | 182 | 11:56 | 12:00 | And then we actually teach the LLM how to commit the migration. |
| [12:00](https://www.youtube.com/watch?v=eeOANluSqAE&t=720s) | eeOANluSqAE | 183 | 12:00 | 12:08 | So you can see in the end we say, call the finished database migration to complete this job. |
| [12:08](https://www.youtube.com/watch?v=eeOANluSqAE&t=728s) | eeOANluSqAE | 184 | 12:08 | 12:16 | And then the LLM can call the complete database migration when it decides that it's ready to go for their main database branch. |
| [12:18](https://www.youtube.com/watch?v=eeOANluSqAE&t=738s) | eeOANluSqAE | 185 | 12:18 | 12:21 | This kind of thing, we wouldn't really expose it in our API. |
| [12:22](https://www.youtube.com/watch?v=eeOANluSqAE&t=742s) | eeOANluSqAE | 186 | 12:22 | 12:28 | It doesn't really make sense to have such a complex multi-step workflow in our REST API. |
| [12:28](https://www.youtube.com/watch?v=eeOANluSqAE&t=748s) | eeOANluSqAE | 187 | 12:28 | 12:33 | But it is totally the kind of thing that makes a lot of sense for LLMs. |
| [12:33](https://www.youtube.com/watch?v=eeOANluSqAE&t=753s) | eeOANluSqAE | 188 | 12:33 | 12:37 | Especially because LLMs are not that good at SQL. |
| [12:37](https://www.youtube.com/watch?v=eeOANluSqAE&t=757s) | eeOANluSqAE | 189 | 12:37 | 12:41 | and so we kind of want to help them test their SQL |
| [12:41](https://www.youtube.com/watch?v=eeOANluSqAE&t=761s) | eeOANluSqAE | 190 | 12:41 | 12:44 | before they apply it on their main database branch. |
| [12:45](https://www.youtube.com/watch?v=eeOANluSqAE&t=765s) | eeOANluSqAE | 191 | 12:45 | 12:47 | So if you're building an MCP server today, |
| [12:48](https://www.youtube.com/watch?v=eeOANluSqAE&t=768s) | eeOANluSqAE | 192 | 12:48 | 12:50 | if you haven't built your company's MCP server yet, |
| [12:51](https://www.youtube.com/watch?v=eeOANluSqAE&t=771s) | eeOANluSqAE | 193 | 12:51 | 12:51 | what should you do? |
| [12:51](https://www.youtube.com/watch?v=eeOANluSqAE&t=771s) | eeOANluSqAE | 194 | 12:51 | 12:52 | Should you write it from scratch |
| [12:52](https://www.youtube.com/watch?v=eeOANluSqAE&t=772s) | eeOANluSqAE | 195 | 12:52 | 12:54 | or should you auto-generate it |
| [12:54](https://www.youtube.com/watch?v=eeOANluSqAE&t=774s) | eeOANluSqAE | 196 | 12:54 | 12:57 | using one of the tools that I mentioned before? |
| [12:57](https://www.youtube.com/watch?v=eeOANluSqAE&t=777s) | eeOANluSqAE | 197 | 12:57 | 13:00 | I would say definitely don't auto-generate it. |
| [13:01](https://www.youtube.com/watch?v=eeOANluSqAE&t=781s) | eeOANluSqAE | 198 | 13:01 | 13:02 | I really don't think that's the way to go. |
| [13:03](https://www.youtube.com/watch?v=eeOANluSqAE&t=783s) | eeOANluSqAE | 199 | 13:03 | 13:04 | But a hybrid solution |
| [13:04](https://www.youtube.com/watch?v=eeOANluSqAE&t=784s) | eeOANluSqAE | 200 | 13:04 | 13:07 | where you start by auto-generating an MCP server |
| [13:07](https://www.youtube.com/watch?v=eeOANluSqAE&t=787s) | eeOANluSqAE | 201 | 13:07 | 13:08 | and then cut it down, |
| [13:08](https://www.youtube.com/watch?v=eeOANluSqAE&t=788s) | eeOANluSqAE | 202 | 13:08 | 13:10 | can make a lot of sense. |
| [13:10](https://www.youtube.com/watch?v=eeOANluSqAE&t=790s) | eeOANluSqAE | 203 | 13:10 | 13:11 | I haven't tried it myself, |
| [13:12](https://www.youtube.com/watch?v=eeOANluSqAE&t=792s) | eeOANluSqAE | 204 | 13:12 | 13:14 | but in principle, |
| [13:15](https://www.youtube.com/watch?v=eeOANluSqAE&t=795s) | eeOANluSqAE | 205 | 13:15 | 13:16 | you should be able to auto-generate an MCP server |
| [13:16](https://www.youtube.com/watch?v=eeOANluSqAE&t=796s) | eeOANluSqAE | 206 | 13:16 | 13:18 | from your open API schema |
| [13:18](https://www.youtube.com/watch?v=eeOANluSqAE&t=798s) | eeOANluSqAE | 207 | 13:18 | 13:21 | and then cut down as many tools as possible. |
| [13:22](https://www.youtube.com/watch?v=eeOANluSqAE&t=802s) | eeOANluSqAE | 208 | 13:22 | 13:24 | The worst thing you can give an LLM is too much choice. |
| [13:25](https://www.youtube.com/watch?v=eeOANluSqAE&t=805s) | eeOANluSqAE | 209 | 13:25 | 13:28 | So remove any tools that you don't think are essential |
| [13:28](https://www.youtube.com/watch?v=eeOANluSqAE&t=808s) | eeOANluSqAE | 210 | 13:28 | 13:29 | for an LLM to consume |
| [13:29](https://www.youtube.com/watch?v=eeOANluSqAE&t=809s) | eeOANluSqAE | 211 | 13:29 | 13:33 | and then evaluate the descriptions for all of your tools |
| [13:33](https://www.youtube.com/watch?v=eeOANluSqAE&t=813s) | eeOANluSqAE | 212 | 13:33 | 13:36 | and then think about interesting tools |
| [13:36](https://www.youtube.com/watch?v=eeOANluSqAE&t=816s) | eeOANluSqAE | 213 | 13:36 | 13:38 | that you might want to expose to an LLM |
| [13:38](https://www.youtube.com/watch?v=eeOANluSqAE&t=818s) | eeOANluSqAE | 214 | 13:38 | 13:41 | but you maybe don't want to have in your API |
| [13:41](https://www.youtube.com/watch?v=eeOANluSqAE&t=821s) | eeOANluSqAE | 215 | 13:41 | 13:44 | and then write your evals. |
| [13:45](https://www.youtube.com/watch?v=eeOANluSqAE&t=825s) | eeOANluSqAE | 216 | 13:45 | 13:47 | That would be a whole other talk, |
| [13:47](https://www.youtube.com/watch?v=eeOANluSqAE&t=827s) | eeOANluSqAE | 217 | 13:47 | 13:49 | but if you're building an MCP server, |
| [13:49](https://www.youtube.com/watch?v=eeOANluSqAE&t=829s) | eeOANluSqAE | 218 | 13:49 | 13:52 | you should have evals and you should have tests |
| [13:52](https://www.youtube.com/watch?v=eeOANluSqAE&t=832s) | eeOANluSqAE | 219 | 13:52 | 13:55 | to ensure that LLMs can use your MCP server correctly. |
| [13:57](https://www.youtube.com/watch?v=eeOANluSqAE&t=837s) | eeOANluSqAE | 220 | 13:57 | 13:58 | That's it for me today. |
| [13:59](https://www.youtube.com/watch?v=eeOANluSqAE&t=839s) | eeOANluSqAE | 221 | 13:59 | 14:03 | I just want to say, like, please reach out. |
| [14:03](https://www.youtube.com/watch?v=eeOANluSqAE&t=843s) | eeOANluSqAE | 222 | 14:03 | 14:05 | I'm an MCP nerd. |
| [14:05](https://www.youtube.com/watch?v=eeOANluSqAE&t=845s) | eeOANluSqAE | 223 | 14:05 | 14:06 | I'm a database nerd. |
| [14:06](https://www.youtube.com/watch?v=eeOANluSqAE&t=846s) | eeOANluSqAE | 224 | 14:06 | 14:09 | I'm happy to talk about remote MCP servers. |
| [14:10](https://www.youtube.com/watch?v=eeOANluSqAE&t=850s) | eeOANluSqAE | 225 | 14:10 | 14:13 | We've been running our MCP server in production |
| [14:13](https://www.youtube.com/watch?v=eeOANluSqAE&t=853s) | eeOANluSqAE | 226 | 14:13 | 14:16 | for more than a month now. |
| [14:17](https://www.youtube.com/watch?v=eeOANluSqAE&t=857s) | eeOANluSqAE | 227 | 14:17 | 14:20 | If you want to talk about tests or evals for MCP servers, |
| [14:20](https://www.youtube.com/watch?v=eeOANluSqAE&t=860s) | eeOANluSqAE | 228 | 14:20 | 14:22 | happy to nerd out about that as well. |
| [14:23](https://www.youtube.com/watch?v=eeOANluSqAE&t=863s) | eeOANluSqAE | 229 | 14:23 | 14:26 | Authentication for MCP or just anything database related. |
| [14:27](https://www.youtube.com/watch?v=eeOANluSqAE&t=867s) | eeOANluSqAE | 230 | 14:27 | 14:28 | I'm really into databases. |
| [14:29](https://www.youtube.com/watch?v=eeOANluSqAE&t=869s) | eeOANluSqAE | 231 | 14:29 | 14:30 | That's it for me today. |
| [14:31](https://www.youtube.com/watch?v=eeOANluSqAE&t=871s) | eeOANluSqAE | 232 | 14:31 | 14:32 | Thank you all very much for your time. |
