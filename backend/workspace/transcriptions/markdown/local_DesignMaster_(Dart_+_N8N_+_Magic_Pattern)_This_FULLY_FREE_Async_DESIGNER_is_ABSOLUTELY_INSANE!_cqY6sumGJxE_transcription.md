# Transcription for Video: [cqY6sumGJxE](https://www.youtube.com/watch?v=cqY6sumGJxE)

| Timestamp Link | Video ID | Seg ID | Start | End | Text |
|---|---|---|---|---|---|
| [00:04](https://www.youtube.com/watch?v=cqY6sumGJxE&t=4s) | cqY6sumGJxE | 0 | 00:04 | 00:13 | Hi, welcome to another video. So, recently, Google Jules and Codex took everyone by storm |
| [00:13](https://www.youtube.com/watch?v=cqY6sumGJxE&t=13s) | cqY6sumGJxE | 1 | 00:13 | 00:19 | because of their async nature where it can basically do the work in background. I really |
| [00:19](https://www.youtube.com/watch?v=cqY6sumGJxE&t=19s) | cqY6sumGJxE | 2 | 00:19 | 00:26 | liked them, and I thought to tell you guys that how you can create your own async agents to which |
| [00:26](https://www.youtube.com/watch?v=cqY6sumGJxE&t=26s) | cqY6sumGJxE | 3 | 00:26 | 00:33 | you can assign tasks and they can do stuff for you in the background. So, for that, I'll be |
| [00:33](https://www.youtube.com/watch?v=cqY6sumGJxE&t=33s) | cqY6sumGJxE | 4 | 00:33 | 00:39 | showing you my own new workflow that I use to autonomously create designs with a specific |
| [00:39](https://www.youtube.com/watch?v=cqY6sumGJxE&t=39s) | cqY6sumGJxE | 5 | 00:39 | 00:45 | design agent, and I like to call this Design Master because it uses a combination of tools |
| [00:45](https://www.youtube.com/watch?v=cqY6sumGJxE&t=45s) | cqY6sumGJxE | 6 | 00:45 | 00:52 | to automatically generate designs for us. We're going to set up an AI agent using Dart in |
| [00:52](https://www.youtube.com/watch?v=cqY6sumGJxE&t=52s) | cqY6sumGJxE | 7 | 00:52 | 01:00 | conjunction with N8N and Magic Patterns to do design tasks for us. I have covered Dart before, |
| [01:00](https://www.youtube.com/watch?v=cqY6sumGJxE&t=60s) | cqY6sumGJxE | 8 | 01:00 | 01:06 | and it's the best AI project management hub where we'll create and assign the design task. |
| [01:08](https://www.youtube.com/watch?v=cqY6sumGJxE&t=68s) | cqY6sumGJxE | 9 | 01:08 | 01:12 | For those who don't know about N8N, it is a workflow automation tool, |
| [01:13](https://www.youtube.com/watch?v=cqY6sumGJxE&t=73s) | cqY6sumGJxE | 10 | 01:13 | 01:17 | kind of like a super-powered Zapier that you can even host yourself. |
| [01:18](https://www.youtube.com/watch?v=cqY6sumGJxE&t=78s) | cqY6sumGJxE | 11 | 01:18 | 01:20 | It's the glue that will connect everything together, |
| [01:21](https://www.youtube.com/watch?v=cqY6sumGJxE&t=81s) | cqY6sumGJxE | 12 | 01:21 | 01:24 | and the brains of the operation will be magic patterns, |
| [01:25](https://www.youtube.com/watch?v=cqY6sumGJxE&t=85s) | cqY6sumGJxE | 13 | 01:25 | 01:29 | an AI that can generate designs and code from a simple text prompt. |
| [01:30](https://www.youtube.com/watch?v=cqY6sumGJxE&t=90s) | cqY6sumGJxE | 14 | 01:30 | 01:31 | It's pretty insane. |
| [01:31](https://www.youtube.com/watch?v=cqY6sumGJxE&t=91s) | cqY6sumGJxE | 15 | 01:31 | 01:34 | So, let's go ahead and get started. |
| [01:35](https://www.youtube.com/watch?v=cqY6sumGJxE&t=95s) | cqY6sumGJxE | 16 | 01:35 | 01:42 | To get started, you're going to need an N8N account, a Magic Patterns account, and of course, |
| [01:42](https://www.youtube.com/watch?v=cqY6sumGJxE&t=102s) | cqY6sumGJxE | 17 | 01:42 | 01:48 | your Dart account as well. All of these have free tiers, which is what you generally need. |
| [01:49](https://www.youtube.com/watch?v=cqY6sumGJxE&t=109s) | cqY6sumGJxE | 18 | 01:49 | 01:56 | We're going to be designing this workflow using an example task. So, I've created a task here in |
| [01:56](https://www.youtube.com/watch?v=cqY6sumGJxE&t=116s) | cqY6sumGJxE | 19 | 01:56 | 02:04 | Dart to design a basic number dropdown. And in that task, I also have a description that we're |
| [02:04](https://www.youtube.com/watch?v=cqY6sumGJxE&t=124s) | cqY6sumGJxE | 20 | 02:04 | 02:12 | going to pass on over to our agent. Now, the first step is to go over to N8N and start a new workflow |
| [02:12](https://www.youtube.com/watch?v=cqY6sumGJxE&t=132s) | cqY6sumGJxE | 21 | 02:12 | 02:19 | and add a first step. This step is going to be to use the webhook call node, and once you click on |
| [02:19](https://www.youtube.com/watch?v=cqY6sumGJxE&t=139s) | cqY6sumGJxE | 22 | 02:19 | 02:26 | that, you'll want to grab the webhook URL here. Click that to copy it. Then, we're going to go on |
| [02:26](https://www.youtube.com/watch?v=cqY6sumGJxE&t=146s) | cqY6sumGJxE | 23 | 02:26 | 02:32 | back to Dart, and we're going to go to Settings, and then Agents, and then we're going to add a new |
| [02:32](https://www.youtube.com/watch?v=cqY6sumGJxE&t=152s) | cqY6sumGJxE | 24 | 02:32 | 02:40 | agent. Here I've added an agent. I've given it the name Magic Patterns. I've also uploaded a logo |
| [02:40](https://www.youtube.com/watch?v=cqY6sumGJxE&t=160s) | cqY6sumGJxE | 25 | 02:40 | 02:46 | here for the profile picture, and now we're going to click on Add Workflow. We're going to leave the |
| [02:46](https://www.youtube.com/watch?v=cqY6sumGJxE&t=166s) | cqY6sumGJxE | 26 | 02:46 | 02:53 | workflow to begin with a task is assigned to Magic Patterns. Then for then, we're going to leave it as |
| [02:53](https://www.youtube.com/watch?v=cqY6sumGJxE&t=173s) | cqY6sumGJxE | 27 | 02:53 | 02:59 | Send a Post Request. We're going to paste in that URL that we grabbed from N8N for the webhook, |
| [02:59](https://www.youtube.com/watch?v=cqY6sumGJxE&t=179s) | cqY6sumGJxE | 28 | 02:59 | 03:02 | and then we're going to add some headers. |
| [03:03](https://www.youtube.com/watch?v=cqY6sumGJxE&t=183s) | cqY6sumGJxE | 29 | 03:03 | 03:08 | In this case, content type and then application JSON. |
| [03:09](https://www.youtube.com/watch?v=cqY6sumGJxE&t=189s) | cqY6sumGJxE | 30 | 03:09 | 03:10 | Then we'll leave the body as it is. |
| [03:11](https://www.youtube.com/watch?v=cqY6sumGJxE&t=191s) | cqY6sumGJxE | 31 | 03:11 | 03:14 | Once we've set up our agent in Dart with the workflow, |
| [03:15](https://www.youtube.com/watch?v=cqY6sumGJxE&t=195s) | cqY6sumGJxE | 32 | 03:15 | 03:16 | we're going to go back to N8N, |
| [03:17](https://www.youtube.com/watch?v=cqY6sumGJxE&t=197s) | cqY6sumGJxE | 33 | 03:17 | 03:20 | make sure our HTTP method is post |
| [03:20](https://www.youtube.com/watch?v=cqY6sumGJxE&t=200s) | cqY6sumGJxE | 34 | 03:20 | 03:22 | and then we're going to try testing this. |
| [03:23](https://www.youtube.com/watch?v=cqY6sumGJxE&t=203s) | cqY6sumGJxE | 35 | 03:23 | 03:25 | So we're going to listen for a test event |
| [03:25](https://www.youtube.com/watch?v=cqY6sumGJxE&t=205s) | cqY6sumGJxE | 36 | 03:25 | 03:27 | and we're going to click that button |
| [03:27](https://www.youtube.com/watch?v=cqY6sumGJxE&t=207s) | cqY6sumGJxE | 37 | 03:27 | 03:29 | and then go back over to Dart. |
| [03:30](https://www.youtube.com/watch?v=cqY6sumGJxE&t=210s) | cqY6sumGJxE | 38 | 03:30 | 03:31 | We're going to go to our task |
| [03:31](https://www.youtube.com/watch?v=cqY6sumGJxE&t=211s) | cqY6sumGJxE | 39 | 03:31 | 03:34 | and we're going to assign it to our new agent |
| [03:34](https://www.youtube.com/watch?v=cqY6sumGJxE&t=214s) | cqY6sumGJxE | 40 | 03:34 | 03:39 | and if we go back to n8n, we can see that it seems to be working here. |
| [03:40](https://www.youtube.com/watch?v=cqY6sumGJxE&t=220s) | cqY6sumGJxE | 41 | 03:40 | 03:45 | It goes ahead and gets all the data in literal seconds, which is kind of cool. |
| [03:46](https://www.youtube.com/watch?v=cqY6sumGJxE&t=226s) | cqY6sumGJxE | 42 | 03:46 | 03:51 | Now, let's go out and let's go ahead and add our next node. |
| [03:52](https://www.youtube.com/watch?v=cqY6sumGJxE&t=232s) | cqY6sumGJxE | 43 | 03:52 | 03:58 | So, for this one, we're going to search in nodes for HTTP request and add that in here. |
| [03:59](https://www.youtube.com/watch?v=cqY6sumGJxE&t=239s) | cqY6sumGJxE | 44 | 03:59 | 04:03 | This node is going to be the one that actually interfaces with magic patterns. |
| [04:04](https://www.youtube.com/watch?v=cqY6sumGJxE&t=244s) | cqY6sumGJxE | 45 | 04:04 | 04:06 | So, we'll make the method post. |
| [04:07](https://www.youtube.com/watch?v=cqY6sumGJxE&t=247s) | cqY6sumGJxE | 46 | 04:07 | 04:11 | Then we're going to grab the URL from the Magic Patterns API docs. |
| [04:12](https://www.youtube.com/watch?v=cqY6sumGJxE&t=252s) | cqY6sumGJxE | 47 | 04:12 | 04:18 | I'm on their website, and we'll copy the endpoint to create designs and paste that URL over here. |
| [04:19](https://www.youtube.com/watch?v=cqY6sumGJxE&t=259s) | cqY6sumGJxE | 48 | 04:19 | 04:20 | It looks like this. |
| [04:21](https://www.youtube.com/watch?v=cqY6sumGJxE&t=261s) | cqY6sumGJxE | 49 | 04:21 | 04:26 | Then for authentication, we're going to go with Generic Credential Type and choose a header auth. |
| [04:27](https://www.youtube.com/watch?v=cqY6sumGJxE&t=267s) | cqY6sumGJxE | 50 | 04:27 | 04:29 | Now we want to make a new credential. |
| [04:29](https://www.youtube.com/watch?v=cqY6sumGJxE&t=269s) | cqY6sumGJxE | 51 | 04:29 | 04:34 | For the name, we want to go back over to those Magic Patterns docs, |
| [04:34](https://www.youtube.com/watch?v=cqY6sumGJxE&t=274s) | cqY6sumGJxE | 52 | 04:34 | 04:38 | and we're going to grab XMP API key from authorizations. |
| [04:38](https://www.youtube.com/watch?v=cqY6sumGJxE&t=278s) | cqY6sumGJxE | 53 | 04:38 | 04:42 | So we're going to copy and paste that into name. |
| [04:43](https://www.youtube.com/watch?v=cqY6sumGJxE&t=283s) | cqY6sumGJxE | 54 | 04:43 | 04:47 | And then for the value here, we want to go to our actual Magic Patterns account, |
| [04:48](https://www.youtube.com/watch?v=cqY6sumGJxE&t=288s) | cqY6sumGJxE | 55 | 04:48 | 04:53 | go into Profile Settings, and scroll to the very bottom for API Key Management, |
| [04:54](https://www.youtube.com/watch?v=cqY6sumGJxE&t=294s) | cqY6sumGJxE | 56 | 04:54 | 04:58 | and we're going to create a new key, and then paste in that key. |
| [04:59](https://www.youtube.com/watch?v=cqY6sumGJxE&t=299s) | cqY6sumGJxE | 57 | 04:59 | 05:05 | Back in N8N, I've pasted in my API key, and I'll go ahead and give a name for this. |
| [05:06](https://www.youtube.com/watch?v=cqY6sumGJxE&t=306s) | cqY6sumGJxE | 58 | 05:06 | 05:10 | We'll call it MPNewAuth, and I'm going to go ahead and save that, |
| [05:11](https://www.youtube.com/watch?v=cqY6sumGJxE&t=311s) | cqY6sumGJxE | 59 | 05:11 | 05:13 | and then I'm going to use that header auth right here. |
| [05:14](https://www.youtube.com/watch?v=cqY6sumGJxE&t=314s) | cqY6sumGJxE | 60 | 05:14 | 05:16 | Next, we'll toggle Send Body On. |
| [05:17](https://www.youtube.com/watch?v=cqY6sumGJxE&t=317s) | cqY6sumGJxE | 61 | 05:17 | 05:20 | For Body Content Type, we'll choose Form Data. |
| [05:21](https://www.youtube.com/watch?v=cqY6sumGJxE&t=321s) | cqY6sumGJxE | 62 | 05:21 | 05:23 | And for the name, we'll put Prompt. |
| [05:24](https://www.youtube.com/watch?v=cqY6sumGJxE&t=324s) | cqY6sumGJxE | 63 | 05:24 | 05:27 | For the value, we'll go over here to the left in the Schema section, |
| [05:28](https://www.youtube.com/watch?v=cqY6sumGJxE&t=328s) | cqY6sumGJxE | 64 | 05:28 | 05:31 | and we're going to find the Task Title and Description, |
| [05:32](https://www.youtube.com/watch?v=cqY6sumGJxE&t=332s) | cqY6sumGJxE | 65 | 05:32 | 05:33 | and we'll just bring them on into here. |
| [05:34](https://www.youtube.com/watch?v=cqY6sumGJxE&t=334s) | cqY6sumGJxE | 66 | 05:34 | 05:39 | This will send this information over to Magic Patterns, which is kind of awesome. |
| [05:40](https://www.youtube.com/watch?v=cqY6sumGJxE&t=340s) | cqY6sumGJxE | 67 | 05:40 | 05:44 | Once we have all of this set up here, let's go ahead and test the step. |
| [05:44](https://www.youtube.com/watch?v=cqY6sumGJxE&t=344s) | cqY6sumGJxE | 68 | 05:44 | 05:47 | Once it finishes, we can take a look. |
| [05:48](https://www.youtube.com/watch?v=cqY6sumGJxE&t=348s) | cqY6sumGJxE | 69 | 05:48 | 05:50 | Make sure it generated properly. |
| [05:51](https://www.youtube.com/watch?v=cqY6sumGJxE&t=351s) | cqY6sumGJxE | 70 | 05:51 | 05:52 | And now we've finished this node. |
| [05:53](https://www.youtube.com/watch?v=cqY6sumGJxE&t=353s) | cqY6sumGJxE | 71 | 05:53 | 05:54 | So, congratulations. |
| [05:55](https://www.youtube.com/watch?v=cqY6sumGJxE&t=355s) | cqY6sumGJxE | 72 | 05:55 | 05:59 | We have successfully created the design in magic patterns. |
| [06:00](https://www.youtube.com/watch?v=cqY6sumGJxE&t=360s) | cqY6sumGJxE | 73 | 06:00 | 06:05 | In fact, I'll go ahead and rename this node to design to indicate that. |
| [06:05](https://www.youtube.com/watch?v=cqY6sumGJxE&t=365s) | cqY6sumGJxE | 74 | 06:05 | 06:08 | The next thing we want to do is pass something back over to Dart. |
| [06:09](https://www.youtube.com/watch?v=cqY6sumGJxE&t=369s) | cqY6sumGJxE | 75 | 06:09 | 06:10 | We'll leave a comment. |
| [06:11](https://www.youtube.com/watch?v=cqY6sumGJxE&t=371s) | cqY6sumGJxE | 76 | 06:11 | 06:15 | So, I'll go ahead and add another HTTP request node, |
| [06:16](https://www.youtube.com/watch?v=cqY6sumGJxE&t=376s) | cqY6sumGJxE | 77 | 06:16 | 06:17 | and I'll go ahead and give this a name as well. |
| [06:18](https://www.youtube.com/watch?v=cqY6sumGJxE&t=378s) | cqY6sumGJxE | 78 | 06:18 | 06:20 | We're going to call it comment finished. |
| [06:21](https://www.youtube.com/watch?v=cqY6sumGJxE&t=381s) | cqY6sumGJxE | 79 | 06:21 | 06:27 | We'll choose the method as post, and for the URL, it's time to actually go back to Dart again. |
| [06:28](https://www.youtube.com/watch?v=cqY6sumGJxE&t=388s) | cqY6sumGJxE | 80 | 06:28 | 06:33 | We're going to go to Settings, API, and we're going to open up the API documentation. |
| [06:35](https://www.youtube.com/watch?v=cqY6sumGJxE&t=395s) | cqY6sumGJxE | 81 | 06:35 | 06:37 | We're going to grab the server URL from up here, |
| [06:37](https://www.youtube.com/watch?v=cqY6sumGJxE&t=397s) | cqY6sumGJxE | 82 | 06:37 | 06:44 | and because what we're trying to do is leave a comment in Dart, we'll grab slash comments from here. |
| [06:45](https://www.youtube.com/watch?v=cqY6sumGJxE&t=405s) | cqY6sumGJxE | 83 | 06:45 | 06:53 | So, I'm going to take that URL back over into n8n and paste it here with slash comments. |
| [06:54](https://www.youtube.com/watch?v=cqY6sumGJxE&t=414s) | cqY6sumGJxE | 84 | 06:54 | 06:59 | Then for authentication, we'll do generic, and we'll choose header auth. |
| [07:00](https://www.youtube.com/watch?v=cqY6sumGJxE&t=420s) | cqY6sumGJxE | 85 | 07:00 | 07:04 | For the header auth, we're going to create a new credential. |
| [07:05](https://www.youtube.com/watch?v=cqY6sumGJxE&t=425s) | cqY6sumGJxE | 86 | 07:05 | 07:07 | We're going to name this something like dart new auth. |
| [07:07](https://www.youtube.com/watch?v=cqY6sumGJxE&t=427s) | cqY6sumGJxE | 87 | 07:07 | 07:14 | For the name, we'll use authorization, and for the value, this is a little bit complicated. |
| [07:15](https://www.youtube.com/watch?v=cqY6sumGJxE&t=435s) | cqY6sumGJxE | 88 | 07:15 | 07:19 | We're going to type in bearer, so B-E-A-R-E-R space, |
| [07:20](https://www.youtube.com/watch?v=cqY6sumGJxE&t=440s) | cqY6sumGJxE | 89 | 07:20 | 07:23 | and then we're going to grab the authentication token from Dart. |
| [07:23](https://www.youtube.com/watch?v=cqY6sumGJxE&t=443s) | cqY6sumGJxE | 90 | 07:23 | 07:35 | To do that, we'll go back to Dart, go to Settings, find Agents, and then click on the three dots next to our agent and grab an authentication token here. |
| [07:36](https://www.youtube.com/watch?v=cqY6sumGJxE&t=456s) | cqY6sumGJxE | 91 | 07:36 | 07:41 | We're going to click Create. That will copy it to our clipboard, and we can paste it over here. |
| [07:42](https://www.youtube.com/watch?v=cqY6sumGJxE&t=462s) | cqY6sumGJxE | 92 | 07:42 | 07:47 | So it'll be Bearer Space Our Authentication Token, and then we will save that. |
| [07:48](https://www.youtube.com/watch?v=cqY6sumGJxE&t=468s) | cqY6sumGJxE | 93 | 07:48 | 07:52 | Next, we're going to go down to Send Body and toggle this on. |
| [07:53](https://www.youtube.com/watch?v=cqY6sumGJxE&t=473s) | cqY6sumGJxE | 94 | 07:53 | 07:59 | Choose JSON for the body content type, and the specific body will be using JSON. |
| [08:00](https://www.youtube.com/watch?v=cqY6sumGJxE&t=480s) | cqY6sumGJxE | 95 | 08:00 | 08:02 | I'm going to paste in something that I'll share as well. |
| [08:03](https://www.youtube.com/watch?v=cqY6sumGJxE&t=483s) | cqY6sumGJxE | 96 | 08:03 | 08:05 | It's basically just item. |
| [08:06](https://www.youtube.com/watch?v=cqY6sumGJxE&t=486s) | cqY6sumGJxE | 97 | 08:06 | 08:09 | And then we're going to use the task ID, and then the text. |
| [08:10](https://www.youtube.com/watch?v=cqY6sumGJxE&t=490s) | cqY6sumGJxE | 98 | 08:10 | 08:12 | This is going to be the text of the comment. |
| [08:13](https://www.youtube.com/watch?v=cqY6sumGJxE&t=493s) | cqY6sumGJxE | 99 | 08:13 | 08:16 | It's going to say done, check out the designs here, |
| [08:16](https://www.youtube.com/watch?v=cqY6sumGJxE&t=496s) | cqY6sumGJxE | 100 | 08:16 | 08:20 | and then it's going to create a link to the actual designs using Markdown. |
| [08:22](https://www.youtube.com/watch?v=cqY6sumGJxE&t=502s) | cqY6sumGJxE | 101 | 08:22 | 08:25 | We just need to drag the task ID in from the webhook node, |
| [08:25](https://www.youtube.com/watch?v=cqY6sumGJxE&t=505s) | cqY6sumGJxE | 102 | 08:25 | 08:28 | and the preview URL in from the design node. |
| [08:29](https://www.youtube.com/watch?v=cqY6sumGJxE&t=509s) | cqY6sumGJxE | 103 | 08:29 | 08:30 | Just like that. |
| [08:30](https://www.youtube.com/watch?v=cqY6sumGJxE&t=510s) | cqY6sumGJxE | 104 | 08:30 | 08:32 | And this is all set up perfectly. |
| [08:33](https://www.youtube.com/watch?v=cqY6sumGJxE&t=513s) | cqY6sumGJxE | 105 | 08:33 | 08:35 | So now we're just going to click here to test the step. |
| [08:37](https://www.youtube.com/watch?v=cqY6sumGJxE&t=517s) | cqY6sumGJxE | 106 | 08:37 | 08:39 | Here we can see it looks like we have a proper output. |
| [08:40](https://www.youtube.com/watch?v=cqY6sumGJxE&t=520s) | cqY6sumGJxE | 107 | 08:40 | 08:42 | So now we can just switch back on over to Dart, |
| [08:43](https://www.youtube.com/watch?v=cqY6sumGJxE&t=523s) | cqY6sumGJxE | 108 | 08:43 | 08:44 | open up the task, |
| [08:45](https://www.youtube.com/watch?v=cqY6sumGJxE&t=525s) | cqY6sumGJxE | 109 | 08:45 | 08:47 | and there's the comment from Magic Patterns |
| [08:47](https://www.youtube.com/watch?v=cqY6sumGJxE&t=527s) | cqY6sumGJxE | 110 | 08:47 | 08:49 | with a link to the designs. |
| [08:50](https://www.youtube.com/watch?v=cqY6sumGJxE&t=530s) | cqY6sumGJxE | 111 | 08:50 | 08:51 | And as we can see here, |
| [08:52](https://www.youtube.com/watch?v=cqY6sumGJxE&t=532s) | cqY6sumGJxE | 112 | 08:52 | 08:53 | we have our number picker dropdown. |
| [08:54](https://www.youtube.com/watch?v=cqY6sumGJxE&t=534s) | cqY6sumGJxE | 113 | 08:54 | 08:56 | So we did it. |
| [08:56](https://www.youtube.com/watch?v=cqY6sumGJxE&t=536s) | cqY6sumGJxE | 114 | 08:56 | 08:59 | To wrap up, everything we've done here |
| [08:59](https://www.youtube.com/watch?v=cqY6sumGJxE&t=539s) | cqY6sumGJxE | 115 | 08:59 | 09:01 | has just been to set this up |
| [09:01](https://www.youtube.com/watch?v=cqY6sumGJxE&t=541s) | cqY6sumGJxE | 116 | 09:01 | 09:08 | and test it to make sure it's working. What we need to do now is save our workflow, mark it as |
| [09:08](https://www.youtube.com/watch?v=cqY6sumGJxE&t=548s) | cqY6sumGJxE | 117 | 09:08 | 09:14 | active, and then we're going to go back to the webhook, and this time we need to grab the |
| [09:14](https://www.youtube.com/watch?v=cqY6sumGJxE&t=554s) | cqY6sumGJxE | 118 | 09:14 | 09:21 | production URL. So we'll copy the production URL to our clipboard and go back over to Agents, |
| [09:22](https://www.youtube.com/watch?v=cqY6sumGJxE&t=562s) | cqY6sumGJxE | 119 | 09:22 | 09:29 | open up here, and use the production URL instead. So now everything should be set up with magic |
| [09:29](https://www.youtube.com/watch?v=cqY6sumGJxE&t=569s) | cqY6sumGJxE | 120 | 09:29 | 09:35 | patterns. As you can see, this is a pretty powerful workflow. You can basically automate |
| [09:35](https://www.youtube.com/watch?v=cqY6sumGJxE&t=575s) | cqY6sumGJxE | 121 | 09:35 | 09:42 | a lot of your design process and have magic patterns, take the first stab at it. This is |
| [09:42](https://www.youtube.com/watch?v=cqY6sumGJxE&t=582s) | cqY6sumGJxE | 122 | 09:42 | 09:47 | really good and just works crazily well for all the tasks, which is quite awesome if you ask me. |
| [09:49](https://www.youtube.com/watch?v=cqY6sumGJxE&t=589s) | cqY6sumGJxE | 123 | 09:49 | 09:55 | You can go ahead and create super simple agents for your tasks and everything like that. Overall, |
| [09:55](https://www.youtube.com/watch?v=cqY6sumGJxE&t=595s) | cqY6sumGJxE | 124 | 09:55 | 10:00 | it's pretty cool. Anyway, share your thoughts below and subscribe to the channel. You can also |
| [10:00](https://www.youtube.com/watch?v=cqY6sumGJxE&t=600s) | cqY6sumGJxE | 125 | 10:00 | 10:05 | donate via SuperThanks option or join the channel as well and get some perks. I'll see you in the |
| [10:05](https://www.youtube.com/watch?v=cqY6sumGJxE&t=605s) | cqY6sumGJxE | 126 | 10:05 | 10:06 | next video. Bye! |
