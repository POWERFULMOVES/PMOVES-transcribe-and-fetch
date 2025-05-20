# Transcription for Video: [j8pmyCR-WmQ](https://www.youtube.com/watch?v=j8pmyCR-WmQ)

| Timestamp Link | Video ID | Seg ID | Start | End | Text |
|---|---|---|---|---|---|
| [00:00](https://www.youtube.com/watch?v=j8pmyCR-WmQ&t=0s) | j8pmyCR-WmQ | 0 | 00:00 | 00:08 | we do end up right here with a pull request in the github repository so it is very cool and i |
| [00:08](https://www.youtube.com/watch?v=j8pmyCR-WmQ&t=8s) | j8pmyCR-WmQ | 1 | 00:08 | 00:14 | will say this is absolutely very agentic software development so for today's video we're going to be |
| [00:14](https://www.youtube.com/watch?v=j8pmyCR-WmQ&t=14s) | j8pmyCR-WmQ | 2 | 00:14 | 00:21 | taking a look at the newly released codex software agentic development team from openai now if you |
| [00:21](https://www.youtube.com/watch?v=j8pmyCR-WmQ&t=21s) | j8pmyCR-WmQ | 3 | 00:21 | 00:27 | have watched my channel before one thank you and two you know that i don't necessarily like to |
| [00:27](https://www.youtube.com/watch?v=j8pmyCR-WmQ&t=27s) | j8pmyCR-WmQ | 4 | 00:27 | 00:32 | cover things that are not open source. I will sometimes make exceptions and this is definitely |
| [00:32](https://www.youtube.com/watch?v=j8pmyCR-WmQ&t=32s) | j8pmyCR-WmQ | 5 | 00:32 | 00:37 | one of those cases. Partially the reason for that is everything I see here architecturally and the |
| [00:37](https://www.youtube.com/watch?v=j8pmyCR-WmQ&t=37s) | j8pmyCR-WmQ | 6 | 00:37 | 00:42 | way it functions is something that could be replicated into the open source and likely will |
| [00:42](https://www.youtube.com/watch?v=j8pmyCR-WmQ&t=42s) | j8pmyCR-WmQ | 7 | 00:42 | 00:49 | allow us to have something that can be used with a local LLM somewhat akin to this hopefully in |
| [00:49](https://www.youtube.com/watch?v=j8pmyCR-WmQ&t=49s) | j8pmyCR-WmQ | 8 | 00:49 | 00:54 | the near future. So with that framing of this video we're basically just going to take a quick |
| [00:54](https://www.youtube.com/watch?v=j8pmyCR-WmQ&t=54s) | j8pmyCR-WmQ | 9 | 00:54 | 00:59 | peek at Codex. I am fortunate enough to have access to this through a pro subscription, so |
| [00:59](https://www.youtube.com/watch?v=j8pmyCR-WmQ&t=59s) | j8pmyCR-WmQ | 10 | 00:59 | 01:04 | I figure we can just kind of get a simple but hands-on look at how this actually functions and |
| [01:04](https://www.youtube.com/watch?v=j8pmyCR-WmQ&t=64s) | j8pmyCR-WmQ | 11 | 01:04 | 01:09 | things like that. I saw a lot of coverage of this was just kind of based off of the video that Open |
| [01:09](https://www.youtube.com/watch?v=j8pmyCR-WmQ&t=69s) | j8pmyCR-WmQ | 12 | 01:09 | 01:14 | AI themselves shared when they started to release this in kind of a marketing video, and I was a bit |
| [01:14](https://www.youtube.com/watch?v=j8pmyCR-WmQ&t=74s) | j8pmyCR-WmQ | 13 | 01:14 | 01:20 | turned off by seeing coverage of this based off of a video that Open AI shared, so I want to just |
| [01:20](https://www.youtube.com/watch?v=j8pmyCR-WmQ&t=80s) | j8pmyCR-WmQ | 14 | 01:20 | 01:24 | do some hands-on stuff with it. First and foremost, they do have a bit of documentation right here, |
| [01:25](https://www.youtube.com/watch?v=j8pmyCR-WmQ&t=85s) | j8pmyCR-WmQ | 15 | 01:25 | 01:31 | and I think it is prudent to mention that this is different than the OpenAI Codex CLI, which is a |
| [01:31](https://www.youtube.com/watch?v=j8pmyCR-WmQ&t=91s) | j8pmyCR-WmQ | 16 | 01:31 | 01:37 | lightweight coding agent that runs in your terminal. Obviously, OpenAI's naming schema has been called |
| [01:37](https://www.youtube.com/watch?v=j8pmyCR-WmQ&t=97s) | j8pmyCR-WmQ | 17 | 01:37 | 01:42 | into question a lot, and this is definitely another one of those scenarios, but this is a separate |
| [01:42](https://www.youtube.com/watch?v=j8pmyCR-WmQ&t=102s) | j8pmyCR-WmQ | 18 | 01:42 | 01:49 | entity, if you will. So with that, what is Codex? As we can see right here, Codex is a cloud-based |
| [01:49](https://www.youtube.com/watch?v=j8pmyCR-WmQ&t=109s) | j8pmyCR-WmQ | 19 | 01:49 | 01:54 | software engineering agent. You can use it to fix bugs, review codes, do refractors, and fix pieces |
| [01:54](https://www.youtube.com/watch?v=j8pmyCR-WmQ&t=114s) | j8pmyCR-WmQ | 20 | 01:54 | 01:59 | of code in response to user feedback. Now interestingly enough, it's powered by a version |
| [01:59](https://www.youtube.com/watch?v=j8pmyCR-WmQ&t=119s) | j8pmyCR-WmQ | 21 | 01:59 | 02:05 | of OpenAI 03 that's fine-tuned for real-world software development. So this is not just one |
| [02:05](https://www.youtube.com/watch?v=j8pmyCR-WmQ&t=125s) | j8pmyCR-WmQ | 22 | 02:05 | 02:10 | of the default models that you'd be able to choose if you were in ChatGPT right here like this, |
| [02:10](https://www.youtube.com/watch?v=j8pmyCR-WmQ&t=130s) | j8pmyCR-WmQ | 23 | 02:10 | 02:15 | where basically you see these models right here, but you don't actually have that. All you have, |
| [02:15](https://www.youtube.com/watch?v=j8pmyCR-WmQ&t=135s) | j8pmyCR-WmQ | 24 | 02:15 | 02:21 | the closest thing would be 03. So this is actually a model that's fine tuned off of that to excel at |
| [02:21](https://www.youtube.com/watch?v=j8pmyCR-WmQ&t=141s) | j8pmyCR-WmQ | 25 | 02:21 | 02:26 | software tasks, which is fairly cool. Now with that, I'm not going to go through everything |
| [02:26](https://www.youtube.com/watch?v=j8pmyCR-WmQ&t=146s) | j8pmyCR-WmQ | 26 | 02:26 | 02:31 | here step by step. But just to mention a couple of things. Essentially, this has you connect your |
| [02:31](https://www.youtube.com/watch?v=j8pmyCR-WmQ&t=151s) | j8pmyCR-WmQ | 27 | 02:31 | 02:37 | GitHub. And when I went to do this, they actually prompted me from open AIs and to enable two factor |
| [02:37](https://www.youtube.com/watch?v=j8pmyCR-WmQ&t=157s) | j8pmyCR-WmQ | 28 | 02:37 | 02:43 | authentication with an authenticator app. So they are taking this seriously in terms of what they |
| [02:43](https://www.youtube.com/watch?v=j8pmyCR-WmQ&t=163s) | j8pmyCR-WmQ | 29 | 02:43 | 02:49 | view this thing's ability to actually autonomously perform actions to be. I apologize if that was a |
| [02:49](https://www.youtube.com/watch?v=j8pmyCR-WmQ&t=169s) | j8pmyCR-WmQ | 30 | 02:49 | 02:56 | word salad. But basically, it won't write to your repo without your permission. But it does have |
| [02:56](https://www.youtube.com/watch?v=j8pmyCR-WmQ&t=176s) | j8pmyCR-WmQ | 31 | 02:56 | 03:00 | the ability to clone the repo and the ability to push a pull request to it. So it does have the |
| [03:00](https://www.youtube.com/watch?v=j8pmyCR-WmQ&t=180s) | j8pmyCR-WmQ | 32 | 03:00 | 03:06 | ability to autonomously perform agentic software tasks, I suppose we could say. So at a high level, |
| [03:06](https://www.youtube.com/watch?v=j8pmyCR-WmQ&t=186s) | j8pmyCR-WmQ | 33 | 03:06 | 03:11 | you can specify a prompt right here where it will go to work. And they say about eight to 10 minutes |
| [03:11](https://www.youtube.com/watch?v=j8pmyCR-WmQ&t=191s) | j8pmyCR-WmQ | 34 | 03:11 | 03:16 | later, it kind of gives you back something, there are different modes in which you can execute |
| [03:16](https://www.youtube.com/watch?v=j8pmyCR-WmQ&t=196s) | j8pmyCR-WmQ | 35 | 03:16 | 03:22 | prompts, there is the ask mode where it clones and creates a read only version of your repository and |
| [03:22](https://www.youtube.com/watch?v=j8pmyCR-WmQ&t=202s) | j8pmyCR-WmQ | 36 | 03:22 | 03:27 | a lot of giving you follow up tasks. So at least from what I see right here, it seems like the ask |
| [03:27](https://www.youtube.com/watch?v=j8pmyCR-WmQ&t=207s) | j8pmyCR-WmQ | 37 | 03:27 | 03:33 | mode would be more for needing to better understand the code base you're working with, then it could |
| [03:33](https://www.youtube.com/watch?v=j8pmyCR-WmQ&t=213s) | j8pmyCR-WmQ | 38 | 03:33 | 03:38 | go ahead and kind of explain those things to you versus the code mode, which creates a full fledged |
| [03:38](https://www.youtube.com/watch?v=j8pmyCR-WmQ&t=218s) | j8pmyCR-WmQ | 39 | 03:38 | 03:42 | environment that the agent can run and test against. So the actual environment creation here |
| [03:42](https://www.youtube.com/watch?v=j8pmyCR-WmQ&t=222s) | j8pmyCR-WmQ | 40 | 03:42 | 03:48 | is quite in depth, because if we hop over to codecs right here, and we go up to the top right |
| [03:48](https://www.youtube.com/watch?v=j8pmyCR-WmQ&t=228s) | j8pmyCR-WmQ | 41 | 03:48 | 03:54 | and click environments, if we are to actually go ahead and create a new environment, we can select |
| [03:54](https://www.youtube.com/watch?v=j8pmyCR-WmQ&t=234s) | j8pmyCR-WmQ | 42 | 03:54 | 03:59 | any one of our GitHub repositories that are linked to the GitHub account that we linked with this. So |
| [03:59](https://www.youtube.com/watch?v=j8pmyCR-WmQ&t=239s) | j8pmyCR-WmQ | 43 | 03:59 | 04:04 | in this case, this is my personal GitHub account right here. And these are my public repositories. |
| [04:04](https://www.youtube.com/watch?v=j8pmyCR-WmQ&t=244s) | j8pmyCR-WmQ | 44 | 04:04 | 04:07 | So I think I'll just click Jetson chat for right here |
| [04:07](https://www.youtube.com/watch?v=j8pmyCR-WmQ&t=247s) | j8pmyCR-WmQ | 45 | 04:07 | 04:11 | You can put a description in here for members of your organization |
| [04:11](https://www.youtube.com/watch?v=j8pmyCR-WmQ&t=251s) | j8pmyCR-WmQ | 46 | 04:11 | 04:15 | But in the advanced tab right here is where some of that container stuff comes into play |
| [04:15](https://www.youtube.com/watch?v=j8pmyCR-WmQ&t=255s) | j8pmyCR-WmQ | 47 | 04:15 | 04:19 | So basically you can select a different container images |
| [04:19](https://www.youtube.com/watch?v=j8pmyCR-WmQ&t=259s) | j8pmyCR-WmQ | 48 | 04:19 | 04:26 | You can set package versions for all these different types of software stacks or things like that to put it on |
| [04:26](https://www.youtube.com/watch?v=j8pmyCR-WmQ&t=266s) | j8pmyCR-WmQ | 49 | 04:26 | 04:32 | Scientifically and then you can add environment variables. You can add secrets. You can add a setup script right here |
| [04:32](https://www.youtube.com/watch?v=j8pmyCR-WmQ&t=272s) | j8pmyCR-WmQ | 50 | 04:32 | 04:46 | So this really does allow for some fairly intricate setup here to allow this agent to work in an environment that is akin to the environment that you yourself have used to create this repository, which is quite neat. |
| [04:46](https://www.youtube.com/watch?v=j8pmyCR-WmQ&t=286s) | j8pmyCR-WmQ | 51 | 04:46 | 05:00 | And again, this is kind of some of the stuff I was talking about where I don't mind sharing this or doing a video on it, even though it's closed source and currently rather expensive, because these are all things that architecturally can be replicated into the open source. |
| [05:00](https://www.youtube.com/watch?v=j8pmyCR-WmQ&t=300s) | j8pmyCR-WmQ | 52 | 05:00 | 05:03 | So with that basically what we're gonna do we'll just hop back here |
| [05:03](https://www.youtube.com/watch?v=j8pmyCR-WmQ&t=303s) | j8pmyCR-WmQ | 53 | 05:03 | 05:07 | They have some more things here about like how to actually best use this and things of that sort |
| [05:08](https://www.youtube.com/watch?v=j8pmyCR-WmQ&t=308s) | j8pmyCR-WmQ | 54 | 05:08 | 05:15 | They have the advanced configuration, which we just took a look at here where we can kind of set up our environment akin to our local environment |
| [05:16](https://www.youtube.com/watch?v=j8pmyCR-WmQ&t=316s) | j8pmyCR-WmQ | 55 | 05:16 | 05:17 | prompting tips |
| [05:17](https://www.youtube.com/watch?v=j8pmyCR-WmQ&t=317s) | j8pmyCR-WmQ | 56 | 05:17 | 05:21 | So really not too much here in terms of documentation |
| [05:21](https://www.youtube.com/watch?v=j8pmyCR-WmQ&t=321s) | j8pmyCR-WmQ | 57 | 05:21 | 05:25 | But I suppose that's good because instead of me rambling on we can just start playing with it |
| [05:25](https://www.youtube.com/watch?v=j8pmyCR-WmQ&t=325s) | j8pmyCR-WmQ | 58 | 05:25 | 05:33 | now i do currently have this linked to my r1 open social robot which is a it's basically like a |
| [05:33](https://www.youtube.com/watch?v=j8pmyCR-WmQ&t=333s) | j8pmyCR-WmQ | 59 | 05:33 | 05:38 | little humanoid bust where it's open source you can 3d print it yourself and you have a social |
| [05:38](https://www.youtube.com/watch?v=j8pmyCR-WmQ&t=338s) | j8pmyCR-WmQ | 60 | 05:38 | 05:45 | chat companion that you can put on your table now this is a unity driven like script and package |
| [05:45](https://www.youtube.com/watch?v=j8pmyCR-WmQ&t=345s) | j8pmyCR-WmQ | 61 | 05:45 | 05:50 | and framework and things like that so a lot of this is c-sharp which i didn't necessarily see |
| [05:50](https://www.youtube.com/watch?v=j8pmyCR-WmQ&t=350s) | j8pmyCR-WmQ | 62 | 05:50 | 05:55 | mentioned anywhere at all in any of the codex documentation but basically i think first and |
| [05:55](https://www.youtube.com/watch?v=j8pmyCR-WmQ&t=355s) | j8pmyCR-WmQ | 63 | 05:55 | 06:01 | foremost, let's just ask it to thoroughly and in depth explain this code base to us and things |
| [06:01](https://www.youtube.com/watch?v=j8pmyCR-WmQ&t=361s) | j8pmyCR-WmQ | 64 | 06:01 | 06:08 | like that. And all I'm going to do right now is just click ask. This is a first initial pretty |
| [06:08](https://www.youtube.com/watch?v=j8pmyCR-WmQ&t=368s) | j8pmyCR-WmQ | 65 | 06:08 | 06:15 | light weight test, at least for now, where we want to see what this actually comes up with in |
| [06:15](https://www.youtube.com/watch?v=j8pmyCR-WmQ&t=375s) | j8pmyCR-WmQ | 66 | 06:15 | 06:21 | terms of explaining this repository. Now this is a repository that I know quite well. So I think |
| [06:21](https://www.youtube.com/watch?v=j8pmyCR-WmQ&t=381s) | j8pmyCR-WmQ | 67 | 06:21 | 06:26 | it's fair to ask it and see how it does. Something I think that is interesting about this. Now a lot |
| [06:26](https://www.youtube.com/watch?v=j8pmyCR-WmQ&t=386s) | j8pmyCR-WmQ | 68 | 06:26 | 06:31 | of folks talk about stuff like this replacing software agents and software developers and |
| [06:31](https://www.youtube.com/watch?v=j8pmyCR-WmQ&t=391s) | j8pmyCR-WmQ | 69 | 06:31 | 06:38 | things like that um i have no interest in getting into a discussion on the feasibility or lack |
| [06:38](https://www.youtube.com/watch?v=j8pmyCR-WmQ&t=398s) | j8pmyCR-WmQ | 70 | 06:38 | 06:42 | thereof of such a thing but i will say that i find this actually interesting in assisting |
| [06:42](https://www.youtube.com/watch?v=j8pmyCR-WmQ&t=402s) | j8pmyCR-WmQ | 71 | 06:42 | 06:48 | maybe newer developers or folks who want to learn programming because you can essentially take a |
| [06:48](https://www.youtube.com/watch?v=j8pmyCR-WmQ&t=408s) | j8pmyCR-WmQ | 72 | 06:48 | 06:55 | repository that you're interested in clone it and then using this connect it to your github and then |
| [06:55](https://www.youtube.com/watch?v=j8pmyCR-WmQ&t=415s) | j8pmyCR-WmQ | 73 | 06:55 | 07:00 | ask it to explain pieces of that repository to you. So if there is something you find interesting |
| [07:00](https://www.youtube.com/watch?v=j8pmyCR-WmQ&t=420s) | j8pmyCR-WmQ | 74 | 07:00 | 07:04 | that you want to fork and implement a change into to better suit your personal workflow, |
| [07:05](https://www.youtube.com/watch?v=j8pmyCR-WmQ&t=425s) | j8pmyCR-WmQ | 75 | 07:05 | 07:09 | this would actually be extremely helpful with that just in terms of actually explaining to |
| [07:09](https://www.youtube.com/watch?v=j8pmyCR-WmQ&t=429s) | j8pmyCR-WmQ | 76 | 07:09 | 07:15 | you what the repository does and how you can go about implementing the changes that you yourself |
| [07:15](https://www.youtube.com/watch?v=j8pmyCR-WmQ&t=435s) | j8pmyCR-WmQ | 77 | 07:15 | 07:19 | would like to make to said repository. Also, I do want to quickly mention if you are a business |
| [07:19](https://www.youtube.com/watch?v=j8pmyCR-WmQ&t=439s) | j8pmyCR-WmQ | 78 | 07:19 | 07:25 | looking to integrate AI into some form of your workflow or products, you can book a consultation |
| [07:25](https://www.youtube.com/watch?v=j8pmyCR-WmQ&t=445s) | j8pmyCR-WmQ | 79 | 07:25 | 07:31 | and speak with me at bijamboan.com. All right, so it does seem the task has concluded just based off |
| [07:31](https://www.youtube.com/watch?v=j8pmyCR-WmQ&t=451s) | j8pmyCR-WmQ | 80 | 07:31 | 07:35 | of the visual feedback I'm seeing where it's not actually looking through anything now. So |
| [07:35](https://www.youtube.com/watch?v=j8pmyCR-WmQ&t=455s) | j8pmyCR-WmQ | 81 | 07:35 | 07:41 | I will just go ahead and click on this and open it. And okay, we do have our beautiful graph right |
| [07:41](https://www.youtube.com/watch?v=j8pmyCR-WmQ&t=461s) | j8pmyCR-WmQ | 82 | 07:41 | 07:47 | here, which I suppose beautiful would be up to interpretation there. This repository contains |
| [07:47](https://www.youtube.com/watch?v=j8pmyCR-WmQ&t=467s) | j8pmyCR-WmQ | 83 | 07:47 | 07:53 | the source code and build files for the r1 diy robot kit okay the detailed readme explains all |
| [07:53](https://www.youtube.com/watch?v=j8pmyCR-WmQ&t=473s) | j8pmyCR-WmQ | 84 | 07:53 | 07:57 | of these things additional assets things like that it gives us an overview of the repository |
| [07:57](https://www.youtube.com/watch?v=j8pmyCR-WmQ&t=477s) | j8pmyCR-WmQ | 85 | 07:57 | 08:02 | some key documentation important code sections now this is where i'm a little more interested |
| [08:02](https://www.youtube.com/watch?v=j8pmyCR-WmQ&t=482s) | j8pmyCR-WmQ | 86 | 08:02 | 08:08 | because honestly like everything right here is something that a basic local llm could parse just |
| [08:08](https://www.youtube.com/watch?v=j8pmyCR-WmQ&t=488s) | j8pmyCR-WmQ | 87 | 08:08 | 08:13 | from reading the actual readme in a github repository as well as kind of just getting |
| [08:13](https://www.youtube.com/watch?v=j8pmyCR-WmQ&t=493s) | j8pmyCR-WmQ | 88 | 08:13 | 08:17 | the structure of the file. So none of this is super interesting to me in terms of actually |
| [08:17](https://www.youtube.com/watch?v=j8pmyCR-WmQ&t=497s) | j8pmyCR-WmQ | 89 | 08:17 | 08:22 | assessing the performance of this. However, something like this right here with the important |
| [08:22](https://www.youtube.com/watch?v=j8pmyCR-WmQ&t=502s) | j8pmyCR-WmQ | 90 | 08:22 | 08:29 | code sections definitely is. So we have the robo logic dot CS, which is an integral part of the |
| [08:29](https://www.youtube.com/watch?v=j8pmyCR-WmQ&t=509s) | j8pmyCR-WmQ | 91 | 08:29 | 08:34 | script because it actually handles the communication backbone for the robot. So it handles taking in |
| [08:34](https://www.youtube.com/watch?v=j8pmyCR-WmQ&t=514s) | j8pmyCR-WmQ | 92 | 08:34 | 08:40 | the user speech, sending that to the back end LLM that runs the robot's intelligence, and then kind |
| [08:40](https://www.youtube.com/watch?v=j8pmyCR-WmQ&t=520s) | j8pmyCR-WmQ | 93 | 08:40 | 08:44 | of triggering all of the actions that allow the robot to respond to the user and then have a |
| [08:44](https://www.youtube.com/watch?v=j8pmyCR-WmQ&t=524s) | j8pmyCR-WmQ | 94 | 08:44 | 08:49 | conversational flow, if you will. So as it says right here, this handles communication with a |
| [08:49](https://www.youtube.com/watch?v=j8pmyCR-WmQ&t=529s) | j8pmyCR-WmQ | 95 | 08:49 | 08:55 | local LLM endpoint, it sends chat messages and processes response over HTTP. And it is actually |
| [08:55](https://www.youtube.com/watch?v=j8pmyCR-WmQ&t=535s) | j8pmyCR-WmQ | 96 | 08:55 | 09:04 | showing some seemingly like these are the word eludes me right here sources, citation sources, |
| [09:04](https://www.youtube.com/watch?v=j8pmyCR-WmQ&t=544s) | j8pmyCR-WmQ | 97 | 09:04 | 09:09 | if you will. So that is kind of cool that just shows kind of beyond that it shows a little |
| [09:09](https://www.youtube.com/watch?v=j8pmyCR-WmQ&t=549s) | j8pmyCR-WmQ | 98 | 09:09 | 09:15 | understanding of what is an important part of this code base which in this case is correct |
| [09:16](https://www.youtube.com/watch?v=j8pmyCR-WmQ&t=556s) | j8pmyCR-WmQ | 99 | 09:16 | 09:22 | we have the robolisten.cs which captures speech with azure cognitive speech services and incuse |
| [09:22](https://www.youtube.com/watch?v=j8pmyCR-WmQ&t=562s) | j8pmyCR-WmQ | 100 | 09:22 | 09:26 | results for processing which is correct right there the starter mode and starter mode contain |
| [09:26](https://www.youtube.com/watch?v=j8pmyCR-WmQ&t=566s) | j8pmyCR-WmQ | 101 | 09:26 | 09:31 | unity scripts such as the script right here for speech synthesis and lip sync manager cs for |
| [09:31](https://www.youtube.com/watch?v=j8pmyCR-WmQ&t=571s) | j8pmyCR-WmQ | 102 | 09:31 | 09:38 | mouth animation so that is correct it talks about arduino logic how the head rotation responds to |
| [09:38](https://www.youtube.com/watch?v=j8pmyCR-WmQ&t=578s) | j8pmyCR-WmQ | 103 | 09:38 | 09:43 | sound sensors using a stepper motor library so that's interesting and correct observed issues |
| [09:43](https://www.youtube.com/watch?v=j8pmyCR-WmQ&t=583s) | j8pmyCR-WmQ | 104 | 09:43 | 09:50 | uh oh no this is where i get mad at it now okay numerous mac os artifacts are committed throughout |
| [09:50](https://www.youtube.com/watch?v=j8pmyCR-WmQ&t=590s) | j8pmyCR-WmQ | 105 | 09:50 | 09:56 | the repo okay yeah that's on me my bad i'm not too fluent in github broken pdf link in readme |
| [09:58](https://www.youtube.com/watch?v=j8pmyCR-WmQ&t=598s) | j8pmyCR-WmQ | 106 | 09:58 | 10:03 | oh interesting okay so that's pretty good attention to detail right there incorrect path in |
| [10:03](https://www.youtube.com/watch?v=j8pmyCR-WmQ&t=603s) | j8pmyCR-WmQ | 107 | 10:03 | 10:08 | git attributes for the reference right here okay and then we have our little mermaid diagram right |
| [10:08](https://www.youtube.com/watch?v=j8pmyCR-WmQ&t=608s) | j8pmyCR-WmQ | 108 | 10:08 | 10:15 | here which uh i'm not gonna really try to make sense of right now this repository supplies |
| [10:15](https://www.youtube.com/watch?v=j8pmyCR-WmQ&t=615s) | j8pmyCR-WmQ | 109 | 10:15 | 10:20 | everything for building in r1 robot okay addressing the issues above will clean up the repository and |
| [10:20](https://www.youtube.com/watch?v=j8pmyCR-WmQ&t=620s) | j8pmyCR-WmQ | 110 | 10:20 | 10:26 | fix small path errors so basically from what i see right here i can then go ahead and ask it to |
| [10:26](https://www.youtube.com/watch?v=j8pmyCR-WmQ&t=626s) | j8pmyCR-WmQ | 111 | 10:26 | 10:32 | actually implement these changes and then in that case i would click the code button right here |
| [10:32](https://www.youtube.com/watch?v=j8pmyCR-WmQ&t=632s) | j8pmyCR-WmQ | 112 | 10:32 | 10:40 | because we actually wanted to go ahead and perform a task that so remember the ask where ask was just |
| [10:40](https://www.youtube.com/watch?v=j8pmyCR-WmQ&t=640s) | j8pmyCR-WmQ | 113 | 10:40 | 10:47 | a read-only repository so it could answer questions or things like that um as it said right here ask |
| [10:47](https://www.youtube.com/watch?v=j8pmyCR-WmQ&t=647s) | j8pmyCR-WmQ | 114 | 10:47 | 10:52 | it clones a read-only version booting faster and giving you follow-up tasks code however creates a |
| [10:52](https://www.youtube.com/watch?v=j8pmyCR-WmQ&t=652s) | j8pmyCR-WmQ | 115 | 10:52 | 10:56 | full-fledged environment the agent can run and test against so that's what we're doing now is |
| [10:56](https://www.youtube.com/watch?v=j8pmyCR-WmQ&t=656s) | j8pmyCR-WmQ | 116 | 10:56 | 11:01 | basically having it go ahead and implement these suggested changes it is downloading the repository |
| [11:01](https://www.youtube.com/watch?v=j8pmyCR-WmQ&t=661s) | j8pmyCR-WmQ | 117 | 11:01 | 11:05 | and if we click on this little extension arrow right here it brings us into somewhat of an |
| [11:05](https://www.youtube.com/watch?v=j8pmyCR-WmQ&t=665s) | j8pmyCR-WmQ | 118 | 11:05 | 11:09 | artifact window, I suppose you could say. So basically, I'm just |
| [11:09](https://www.youtube.com/watch?v=j8pmyCR-WmQ&t=669s) | j8pmyCR-WmQ | 119 | 11:09 | 11:13 | going to kind of sit here and watch this. So it is basically |
| [11:13](https://www.youtube.com/watch?v=j8pmyCR-WmQ&t=673s) | j8pmyCR-WmQ | 120 | 11:13 | 11:16 | it has cloned the repository, it's listing the files that are |
| [11:16](https://www.youtube.com/watch?v=j8pmyCR-WmQ&t=676s) | j8pmyCR-WmQ | 121 | 11:16 | 11:21 | inside of it. And it is kind of seemingly searching for specific |
| [11:21](https://www.youtube.com/watch?v=j8pmyCR-WmQ&t=681s) | j8pmyCR-WmQ | 122 | 11:21 | 11:27 | things here. So there was no agents markdown that they had |
| [11:27](https://www.youtube.com/watch?v=j8pmyCR-WmQ&t=687s) | j8pmyCR-WmQ | 123 | 11:27 | 11:29 | mentioned in the codex documentation there, which it |
| [11:29](https://www.youtube.com/watch?v=j8pmyCR-WmQ&t=689s) | j8pmyCR-WmQ | 124 | 11:29 | 11:32 | does did seem like was good practice to help guide this |
| [11:32](https://www.youtube.com/watch?v=j8pmyCR-WmQ&t=692s) | j8pmyCR-WmQ | 125 | 11:32 | 11:38 | agent in some of the ways it should or should not function. Okay, so it is currently removing all of |
| [11:38](https://www.youtube.com/watch?v=j8pmyCR-WmQ&t=698s) | j8pmyCR-WmQ | 126 | 11:38 | 11:43 | the macOS specific things right here. As we can see in the shell, the rm command is just to remove |
| [11:43](https://www.youtube.com/watch?v=j8pmyCR-WmQ&t=703s) | j8pmyCR-WmQ | 127 | 11:43 | 11:53 | in Linux. It's adding a git ignore to ensure unnecessary files are excluded. And it's cool |
| [11:53](https://www.youtube.com/watch?v=j8pmyCR-WmQ&t=713s) | j8pmyCR-WmQ | 128 | 11:53 | 12:00 | because this is just doing everything through like command line syntax instead of like a human |
| [12:00](https://www.youtube.com/watch?v=j8pmyCR-WmQ&t=720s) | j8pmyCR-WmQ | 129 | 12:00 | 12:04 | perhaps would maybe go through a graphical user interface to do some of these things at least. |
| [12:04](https://www.youtube.com/watch?v=j8pmyCR-WmQ&t=724s) | j8pmyCR-WmQ | 130 | 12:04 | 12:10 | um this is interesting and does kind of bring me to a place about thinking about some of the |
| [12:10](https://www.youtube.com/watch?v=j8pmyCR-WmQ&t=730s) | j8pmyCR-WmQ | 131 | 12:10 | 12:16 | like longer term future of ai and actually creating things or software development tasks where |
| [12:16](https://www.youtube.com/watch?v=j8pmyCR-WmQ&t=736s) | j8pmyCR-WmQ | 132 | 12:16 | 12:22 | i mean i suppose the argument could be made that like programming languages and things like that |
| [12:22](https://www.youtube.com/watch?v=j8pmyCR-WmQ&t=742s) | j8pmyCR-WmQ | 133 | 12:22 | 12:28 | are an abstraction layer to allow humans to better understand the code they're creating and what it |
| [12:28](https://www.youtube.com/watch?v=j8pmyCR-WmQ&t=748s) | j8pmyCR-WmQ | 134 | 12:28 | 12:34 | will do i do have to wonder if one day ais are just going to essentially be making things in |
| [12:34](https://www.youtube.com/watch?v=j8pmyCR-WmQ&t=754s) | j8pmyCR-WmQ | 135 | 12:34 | 12:40 | like assembly or machine code or whatever you want to call it, which is scary. So okay, we can see |
| [12:40](https://www.youtube.com/watch?v=j8pmyCR-WmQ&t=760s) | j8pmyCR-WmQ | 136 | 12:40 | 12:47 | right here, the changes that it has made right here. And it gives us a nice little kind of |
| [12:47](https://www.youtube.com/watch?v=j8pmyCR-WmQ&t=767s) | j8pmyCR-WmQ | 137 | 12:47 | 12:54 | aesthetically pleasing diagram for this. Okay, so basically, like, again, this is I want this to be |
| [12:54](https://www.youtube.com/watch?v=j8pmyCR-WmQ&t=774s) | j8pmyCR-WmQ | 138 | 12:54 | 12:59 | a quicker and simpler video. So basically, I'm going to just carelessly click push right here, |
| [12:59](https://www.youtube.com/watch?v=j8pmyCR-WmQ&t=779s) | j8pmyCR-WmQ | 139 | 12:59 | 13:05 | which do depending on, you know, the level of importance of your repository. |
| [13:06](https://www.youtube.com/watch?v=j8pmyCR-WmQ&t=786s) | j8pmyCR-WmQ | 140 | 13:06 | 13:09 | So I am going to create a new PR for it. |
| [13:09](https://www.youtube.com/watch?v=j8pmyCR-WmQ&t=789s) | j8pmyCR-WmQ | 141 | 13:09 | 13:16 | And then basically, and again, this is the first time I'm playing with this. |
| [13:16](https://www.youtube.com/watch?v=j8pmyCR-WmQ&t=796s) | j8pmyCR-WmQ | 142 | 13:16 | 13:18 | So, okay, I want to now view the pull request. |
| [13:19](https://www.youtube.com/watch?v=j8pmyCR-WmQ&t=799s) | j8pmyCR-WmQ | 143 | 13:19 | 13:21 | Maybe I should just open that in a new tab. |
| [13:21](https://www.youtube.com/watch?v=j8pmyCR-WmQ&t=801s) | j8pmyCR-WmQ | 144 | 13:21 | 13:27 | Cool. So then it shows right here as myself having created this new pull request. |
| [13:27](https://www.youtube.com/watch?v=j8pmyCR-WmQ&t=807s) | j8pmyCR-WmQ | 145 | 13:27 | 13:32 | So I could then basically go ahead and go in and merge this with the branch. |
| [13:32](https://www.youtube.com/watch?v=j8pmyCR-WmQ&t=812s) | j8pmyCR-WmQ | 146 | 13:32 | 13:38 | and it would essentially have just kind of taken everything that the autonomous software agent did |
| [13:38](https://www.youtube.com/watch?v=j8pmyCR-WmQ&t=818s) | j8pmyCR-WmQ | 147 | 13:38 | 13:45 | and implemented into the code base through just some human natural language prompting of OpenAI's codex. |
| [13:46](https://www.youtube.com/watch?v=j8pmyCR-WmQ&t=826s) | j8pmyCR-WmQ | 148 | 13:46 | 13:52 | So again, this is quite cool, and my intention in this video is not necessarily even to give my own opinion |
| [13:52](https://www.youtube.com/watch?v=j8pmyCR-WmQ&t=832s) | j8pmyCR-WmQ | 149 | 13:52 | 13:55 | or steer you towards a single conclusion about this program. |
| [13:55](https://www.youtube.com/watch?v=j8pmyCR-WmQ&t=835s) | j8pmyCR-WmQ | 150 | 13:55 | 14:05 | I just kind of wanted to give a general, like no hype demonstration of a rather simple example of this working and how it works. |
| [14:05](https://www.youtube.com/watch?v=j8pmyCR-WmQ&t=845s) | j8pmyCR-WmQ | 151 | 14:05 | 14:14 | And again, something that I think is very important to mention here, at least in terms of my level of interest with something like this, which is currently very expensive. |
| [14:14](https://www.youtube.com/watch?v=j8pmyCR-WmQ&t=854s) | j8pmyCR-WmQ | 152 | 14:14 | 14:18 | Apparently will be for plus users in the near future. |
| [14:18](https://www.youtube.com/watch?v=j8pmyCR-WmQ&t=858s) | j8pmyCR-WmQ | 153 | 14:18 | 14:28 | I think something like this is ripe for being turned into an open source analog of such functionality where this could work with a local LLM. |
| [14:29](https://www.youtube.com/watch?v=j8pmyCR-WmQ&t=869s) | j8pmyCR-WmQ | 154 | 14:29 | 14:34 | Obviously, the amount of tokens being used up for this, I think, would be quite vast. |
| [14:34](https://www.youtube.com/watch?v=j8pmyCR-WmQ&t=874s) | j8pmyCR-WmQ | 155 | 14:34 | 14:41 | So from an actual cost standpoint, I can't really speak to how much something like this would cost if you were just using API credits or something like that. |
| [14:41](https://www.youtube.com/watch?v=j8pmyCR-WmQ&t=881s) | j8pmyCR-WmQ | 156 | 14:41 | 14:43 | But it is really quite cool. |
| [14:43](https://www.youtube.com/watch?v=j8pmyCR-WmQ&t=883s) | j8pmyCR-WmQ | 157 | 14:43 | 14:47 | And from what I'm seeing here, it did a decent job in understanding my code base. |
| [14:47](https://www.youtube.com/watch?v=j8pmyCR-WmQ&t=887s) | j8pmyCR-WmQ | 158 | 14:47 | 14:54 | I can tell you that there's probably a lot of small inefficiencies in a lot of that code that |
| [14:54](https://www.youtube.com/watch?v=j8pmyCR-WmQ&t=894s) | j8pmyCR-WmQ | 159 | 14:54 | 14:58 | could likely also be cleaned up and I didn't actually try that with this as I kind of went |
| [14:58](https://www.youtube.com/watch?v=j8pmyCR-WmQ&t=898s) | j8pmyCR-WmQ | 160 | 14:58 | 15:04 | hands off with it and gave it more general and like generic prompts to see what it did but |
| [15:04](https://www.youtube.com/watch?v=j8pmyCR-WmQ&t=904s) | j8pmyCR-WmQ | 161 | 15:04 | 15:09 | my assessment would be that it would definitely be able to go through those scripts and actually |
| [15:09](https://www.youtube.com/watch?v=j8pmyCR-WmQ&t=909s) | j8pmyCR-WmQ | 162 | 15:09 | 15:15 | clean them up and make them more efficient as well but in the interest of time and being that |
| [15:15](https://www.youtube.com/watch?v=j8pmyCR-WmQ&t=915s) | j8pmyCR-WmQ | 163 | 15:15 | 15:20 | this isn't really a local solution. I'm not going to spend too much time kind of going hands-on and |
| [15:20](https://www.youtube.com/watch?v=j8pmyCR-WmQ&t=920s) | j8pmyCR-WmQ | 164 | 15:20 | 15:25 | covering it, but I did just want to kind of show this, and basically we do end up right here with |
| [15:25](https://www.youtube.com/watch?v=j8pmyCR-WmQ&t=925s) | j8pmyCR-WmQ | 165 | 15:25 | 15:34 | a pull request in the GitHub repository. So it is very cool, and I will say this is absolutely very |
| [15:34](https://www.youtube.com/watch?v=j8pmyCR-WmQ&t=934s) | j8pmyCR-WmQ | 166 | 15:34 | 15:40 | agentic software development-ish, if you will, and I know that's not really a term, but |
| [15:40](https://www.youtube.com/watch?v=j8pmyCR-WmQ&t=940s) | j8pmyCR-WmQ | 167 | 15:40 | 15:43 | Vibe coding wasn't either up until like a year ago. So I suppose |
| [15:45](https://www.youtube.com/watch?v=j8pmyCR-WmQ&t=945s) | j8pmyCR-WmQ | 168 | 15:45 | 15:50 | Things are changing one could say so that is probably going to conclude it |
| [15:50](https://www.youtube.com/watch?v=j8pmyCR-WmQ&t=950s) | j8pmyCR-WmQ | 169 | 15:50 | 15:57 | I will probably go and just merge that or accept that pull request from my computer that is logged into my github account |
| [15:58](https://www.youtube.com/watch?v=j8pmyCR-WmQ&t=958s) | j8pmyCR-WmQ | 170 | 15:58 | 16:03 | If you have any questions, please feel free to leave them in the comments and that's going to wrap today's video up |
| [16:03](https://www.youtube.com/watch?v=j8pmyCR-WmQ&t=963s) | j8pmyCR-WmQ | 171 | 16:03 | 16:05 | So thank you for watching |
