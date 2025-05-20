# Transcription for Video: [LXk8nWwOPuY](https://www.youtube.com/watch?v=LXk8nWwOPuY)

| Timestamp Link | Video ID | Seg ID | Start | End | Text |
|---|---|---|---|---|---|
| [00:00](https://www.youtube.com/watch?v=LXk8nWwOPuY&t=0s) | LXk8nWwOPuY | 0 | 00:00 | 00:06 | Cursor has become incredibly popular for its AI agent, which lets you use powerful models to write code. |
| [00:06](https://www.youtube.com/watch?v=LXk8nWwOPuY&t=6s) | LXk8nWwOPuY | 1 | 00:06 | 00:12 | The agent takes your prompt, understands the context, and starts building by creating files and implementing features automatically. |
| [00:13](https://www.youtube.com/watch?v=LXk8nWwOPuY&t=13s) | LXk8nWwOPuY | 2 | 00:13 | 00:16 | However, with that much auto-generated code, errors are inevitable. |
| [00:16](https://www.youtube.com/watch?v=LXk8nWwOPuY&t=16s) | LXk8nWwOPuY | 3 | 00:16 | 00:22 | Cursor often throws random errors, and you either have to prompt it again or wait for it to recover and fix them. |
| [00:22](https://www.youtube.com/watch?v=LXk8nWwOPuY&t=22s) | LXk8nWwOPuY | 4 | 00:22 | 00:30 | Now imagine if after each segment of code it generates, you could run a review that checks for issues such as security leaks or flawed integrations. |
| [00:30](https://www.youtube.com/watch?v=LXk8nWwOPuY&t=30s) | LXk8nWwOPuY | 5 | 00:30 | 00:37 | This is especially important because AI agents often leave major vulnerabilities behind, and catching them early is absolutely critical. |
| [00:38](https://www.youtube.com/watch?v=LXk8nWwOPuY&t=38s) | LXk8nWwOPuY | 6 | 00:38 | 00:40 | That is exactly where CodeRabbit comes in. |
| [00:40](https://www.youtube.com/watch?v=LXk8nWwOPuY&t=40s) | LXk8nWwOPuY | 7 | 00:40 | 00:47 | CodeRabbit was originally built to review pull requests and GitHub commits by offering suggestions based on what you pushed. |
| [00:47](https://www.youtube.com/watch?v=LXk8nWwOPuY&t=47s) | LXk8nWwOPuY | 8 | 00:47 | 00:51 | But now they have launched a powerful extension for VS Code, Cursor, and Windsurf. |
| [00:51](https://www.youtube.com/watch?v=LXk8nWwOPuY&t=51s) | LXk8nWwOPuY | 9 | 00:51 | 00:56 | You simply plug it in and after every implementation step from cursor, you run the extension. |
| [00:56](https://www.youtube.com/watch?v=LXk8nWwOPuY&t=56s) | LXk8nWwOPuY | 10 | 00:56 | 01:03 | It analyzes the changes, identifies important refactors, highlights security concerns, and suggests improvements. |
| [01:03](https://www.youtube.com/watch?v=LXk8nWwOPuY&t=63s) | LXk8nWwOPuY | 11 | 01:03 | 01:06 | Then you feed those suggestions back to the agent and it handles the fixes. |
| [01:07](https://www.youtube.com/watch?v=LXk8nWwOPuY&t=67s) | LXk8nWwOPuY | 12 | 01:07 | 01:14 | This significantly tightens up your workflow, improves your application security, and helps you reach a stable final product with fewer bugs. |
| [01:14](https://www.youtube.com/watch?v=LXk8nWwOPuY&t=74s) | LXk8nWwOPuY | 13 | 01:14 | 01:19 | Stick around because I am going to walk you through how I use CodeRabbit in my own workflow, |
| [01:19](https://www.youtube.com/watch?v=LXk8nWwOPuY&t=79s) | LXk8nWwOPuY | 14 | 01:19 | 01:23 | starting from an implementation plan, breaking it into manageable chunks, |
| [01:23](https://www.youtube.com/watch?v=LXk8nWwOPuY&t=83s) | LXk8nWwOPuY | 15 | 01:23 | 01:28 | reviewing after each one, and repeating the process to build better and build faster. |
| [01:28](https://www.youtube.com/watch?v=LXk8nWwOPuY&t=88s) | LXk8nWwOPuY | 16 | 01:28 | 01:29 | Installation is simple. |
| [01:29](https://www.youtube.com/watch?v=LXk8nWwOPuY&t=89s) | LXk8nWwOPuY | 17 | 01:29 | 01:33 | In Cursor, open your side panel and then go to Extensions. |
| [01:33](https://www.youtube.com/watch?v=LXk8nWwOPuY&t=93s) | LXk8nWwOPuY | 18 | 01:33 | 01:37 | Search for CodeRabbit, locate the extension, and install it. |
| [01:37](https://www.youtube.com/watch?v=LXk8nWwOPuY&t=97s) | LXk8nWwOPuY | 19 | 01:37 | 01:39 | When you launch it, you will be prompted to sign in. |
| [01:40](https://www.youtube.com/watch?v=LXk8nWwOPuY&t=100s) | LXk8nWwOPuY | 20 | 01:40 | 01:44 | Click to sign in, complete the GitHub authentication in your browser, and you are all set. |
| [01:44](https://www.youtube.com/watch?v=LXk8nWwOPuY&t=104s) | LXk8nWwOPuY | 21 | 01:44 | 01:47 | The entire process is straightforward and has no complications. |
| [01:48](https://www.youtube.com/watch?v=LXk8nWwOPuY&t=108s) | LXk8nWwOPuY | 22 | 01:48 | 01:51 | Okay, so just to show you a live demo of how this actually works, |
| [01:51](https://www.youtube.com/watch?v=LXk8nWwOPuY&t=111s) | LXk8nWwOPuY | 23 | 01:51 | 01:54 | I am currently building an e-commerce store, |
| [01:54](https://www.youtube.com/watch?v=LXk8nWwOPuY&t=114s) | LXk8nWwOPuY | 24 | 01:54 | 01:57 | a full e-commerce store with the admin panel and everything included. |
| [01:57](https://www.youtube.com/watch?v=LXk8nWwOPuY&t=117s) | LXk8nWwOPuY | 25 | 01:57 | 02:01 | I am not exactly sure how much of it I have built in this video, |
| [02:01](https://www.youtube.com/watch?v=LXk8nWwOPuY&t=121s) | LXk8nWwOPuY | 26 | 02:01 | 02:05 | but you will get a pretty clear idea of the workflow we are trying to achieve |
| [02:05](https://www.youtube.com/watch?v=LXk8nWwOPuY&t=125s) | LXk8nWwOPuY | 27 | 02:05 | 02:09 | with this tool and how it is going to assist us throughout the process. |
| [02:09](https://www.youtube.com/watch?v=LXk8nWwOPuY&t=129s) | LXk8nWwOPuY | 28 | 02:09 | 02:13 | Now, what actually happens with this tool is that it reads the changes you have made through GitHub. |
| [02:13](https://www.youtube.com/watch?v=LXk8nWwOPuY&t=133s) | LXk8nWwOPuY | 29 | 02:13 | 02:17 | So first of all, you need to initialize git in the directory you are working in. |
| [02:17](https://www.youtube.com/watch?v=LXk8nWwOPuY&t=137s) | LXk8nWwOPuY | 30 | 02:17 | 02:21 | As you commit those changes, which means saving them, whenever you save anything, |
| [02:22](https://www.youtube.com/watch?v=LXk8nWwOPuY&t=142s) | LXk8nWwOPuY | 31 | 02:22 | 02:27 | CodeRabbit will step in and say that it has detected changes and ask if you want those to be reviewed. |
| [02:27](https://www.youtube.com/watch?v=LXk8nWwOPuY&t=147s) | LXk8nWwOPuY | 32 | 02:27 | 02:31 | You simply click on yes and it will begin reviewing them and providing suggestions. |
| [02:31](https://www.youtube.com/watch?v=LXk8nWwOPuY&t=151s) | LXk8nWwOPuY | 33 | 02:31 | 02:38 | If you want, you can copy those suggestions back into cursor and both tools continue working together seamlessly. |
| [02:38](https://www.youtube.com/watch?v=LXk8nWwOPuY&t=158s) | LXk8nWwOPuY | 34 | 02:38 | 02:41 | This is essentially what the entire workflow is evolving towards. |
| [02:41](https://www.youtube.com/watch?v=LXk8nWwOPuY&t=161s) | LXk8nWwOPuY | 35 | 02:41 | 02:46 | You can see right here that these are the changes I have made that have not yet been committed. |
| [02:46](https://www.youtube.com/watch?v=LXk8nWwOPuY&t=166s) | LXk8nWwOPuY | 36 | 02:46 | 02:49 | But before we go into that, let me show you how to initialize this setup. |
| [02:50](https://www.youtube.com/watch?v=LXk8nWwOPuY&t=170s) | LXk8nWwOPuY | 37 | 02:50 | 02:55 | So first of all, in a new directory, for instance the project directory where you have not started anything yet, |
| [02:55](https://www.youtube.com/watch?v=LXk8nWwOPuY&t=175s) | LXk8nWwOPuY | 38 | 02:55 | 02:57 | you simply type git init. |
| [02:57](https://www.youtube.com/watch?v=LXk8nWwOPuY&t=177s) | LXk8nWwOPuY | 39 | 02:57 | 02:59 | This initializes the git repository. |
| [02:59](https://www.youtube.com/watch?v=LXk8nWwOPuY&t=179s) | LXk8nWwOPuY | 40 | 02:59 | 03:05 | After that, you add your changes using the git add command and the dot signifies that you are adding the entire repository. |
| [03:05](https://www.youtube.com/watch?v=LXk8nWwOPuY&t=185s) | LXk8nWwOPuY | 41 | 03:05 | 03:12 | Once that is done, you use git commit and make sure to include a message with the commit describing what it is about. |
| [03:12](https://www.youtube.com/watch?v=LXk8nWwOPuY&t=192s) | LXk8nWwOPuY | 42 | 03:12 | 03:13 | This is the standard format. |
| [03:13](https://www.youtube.com/watch?v=LXk8nWwOPuY&t=193s) | LXk8nWwOPuY | 43 | 03:13 | 03:18 | You do not need to worry because there are also ways to automate this which I will be showing you |
| [03:18](https://www.youtube.com/watch?v=LXk8nWwOPuY&t=198s) | LXk8nWwOPuY | 44 | 03:18 | 03:20 | but it is important that you go through these initial steps. |
| [03:20](https://www.youtube.com/watch?v=LXk8nWwOPuY&t=200s) | LXk8nWwOPuY | 45 | 03:20 | 03:26 | For example, you can simply write a message like initial commit and this will commit everything in the repository. |
| [03:26](https://www.youtube.com/watch?v=LXk8nWwOPuY&t=206s) | LXk8nWwOPuY | 46 | 03:26 | 03:29 | Once you do this, CodeRabbit will activate and do its part. |
| [03:29](https://www.youtube.com/watch?v=LXk8nWwOPuY&t=209s) | LXk8nWwOPuY | 47 | 03:29 | 03:34 | Every time you make a change, you will need to use git add followed by git commit |
| [03:34](https://www.youtube.com/watch?v=LXk8nWwOPuY&t=214s) | LXk8nWwOPuY | 48 | 03:34 | 03:38 | and this process will save the changes. Each saved change will be detected by CodeRabbit, |
| [03:38](https://www.youtube.com/watch?v=LXk8nWwOPuY&t=218s) | LXk8nWwOPuY | 49 | 03:38 | 03:43 | it will run a review and you can then pass those results over to Cursor to continue your |
| [03:43](https://www.youtube.com/watch?v=LXk8nWwOPuY&t=223s) | LXk8nWwOPuY | 50 | 03:43 | 03:49 | development process smoothly. So while testing it out, I did encounter a big issue. I spent a lot |
| [03:49](https://www.youtube.com/watch?v=LXk8nWwOPuY&t=229s) | LXk8nWwOPuY | 51 | 03:49 | 03:53 | of time trying to fix it and in the end, I went into their Discord server. Someone had actually |
| [03:53](https://www.youtube.com/watch?v=LXk8nWwOPuY&t=233s) | LXk8nWwOPuY | 52 | 03:53 | 03:58 | posted a solution there because many people were facing the same issue and it seems that this is |
| [03:58](https://www.youtube.com/watch?v=LXk8nWwOPuY&t=238s) | LXk8nWwOPuY | 53 | 03:58 | 04:03 | currently a known bug. Apparently, you are supposed to have your branch visible right here where all |
| [04:03](https://www.youtube.com/watch?v=LXk8nWwOPuY&t=243s) | LXk8nWwOPuY | 54 | 04:03 | 04:07 | your branches are listed. Once that is done, you can commit locally and continue working as needed. |
| [04:07](https://www.youtube.com/watch?v=LXk8nWwOPuY&t=247s) | LXk8nWwOPuY | 55 | 04:07 | 04:11 | The tool will focus on the selected branch and every time you commit to that branch, |
| [04:11](https://www.youtube.com/watch?v=LXk8nWwOPuY&t=251s) | LXk8nWwOPuY | 56 | 04:11 | 04:17 | it will be able to review those changes. This is the solution I ended up using. You go to this area |
| [04:17](https://www.youtube.com/watch?v=LXk8nWwOPuY&t=257s) | LXk8nWwOPuY | 57 | 04:17 | 04:22 | and you will see the top menu appear. You simply select the option to create a new branch. Since I |
| [04:22](https://www.youtube.com/watch?v=LXk8nWwOPuY&t=262s) | LXk8nWwOPuY | 58 | 04:22 | 04:26 | have already made a lot of progress, I want to create a copy of the main branch. So I create a |
| [04:26](https://www.youtube.com/watch?v=LXk8nWwOPuY&t=266s) | LXk8nWwOPuY | 59 | 04:26 | 04:31 | new one and name it the test branch. Now you can see that the menu appears and any changes I make |
| [04:31](https://www.youtube.com/watch?v=LXk8nWwOPuY&t=271s) | LXk8nWwOPuY | 60 | 04:31 | 04:36 | will be shown right here. For example, in this file, I just add a comment that says this is a |
| [04:36](https://www.youtube.com/watch?v=LXk8nWwOPuY&t=276s) | LXk8nWwOPuY | 61 | 04:36 | 04:42 | test. I add the comment and save the file. Next, I open the terminal and I am going to add this file |
| [04:42](https://www.youtube.com/watch?v=LXk8nWwOPuY&t=282s) | LXk8nWwOPuY | 62 | 04:42 | 04:47 | to the branch and commit it with the message test. That is done. We now have a commit message labeled |
| [04:47](https://www.youtube.com/watch?v=LXk8nWwOPuY&t=287s) | LXk8nWwOPuY | 63 | 04:47 | 04:52 | test and we want to test how this behaves. So we proceed and now you can see that the review has |
| [04:52](https://www.youtube.com/watch?v=LXk8nWwOPuY&t=292s) | LXk8nWwOPuY | 64 | 04:52 | 04:58 | started. This is the file we committed. The review has been completed and I believe it has generated |
| [04:58](https://www.youtube.com/watch?v=LXk8nWwOPuY&t=298s) | LXk8nWwOPuY | 65 | 04:58 | 05:03 | a few comments. Yes, it added a comment that says remove stray test comment. It recognizes that this |
| [05:03](https://www.youtube.com/watch?v=LXk8nWwOPuY&t=303s) | LXk8nWwOPuY | 66 | 05:03 | 05:08 | is just a test comment and not something important. I just wanted to walk you through this fix so you |
| [05:08](https://www.youtube.com/watch?v=LXk8nWwOPuY&t=308s) | LXk8nWwOPuY | 67 | 05:08 | 05:13 | can understand it clearly. Now let us go back to the project and I will show you how the rest of |
| [05:13](https://www.youtube.com/watch?v=LXk8nWwOPuY&t=313s) | LXk8nWwOPuY | 68 | 05:13 | 05:18 | the workflow plays out. Okay, so I just implemented several other features from my implementation |
| [05:18](https://www.youtube.com/watch?v=LXk8nWwOPuY&t=318s) | LXk8nWwOPuY | 69 | 05:18 | 05:23 | plan. First of all, let me try to open the project to see if it actually runs properly. You can see |
| [05:23](https://www.youtube.com/watch?v=LXk8nWwOPuY&t=323s) | LXk8nWwOPuY | 70 | 05:23 | 05:27 | that there are some errors and now I want to check whether the tool can actually detect and |
| [05:27](https://www.youtube.com/watch?v=LXk8nWwOPuY&t=327s) | LXk8nWwOPuY | 71 | 05:27 | 05:33 | address these errors during its review process. I believe this part of the work falls under phase |
| [05:33](https://www.youtube.com/watch?v=LXk8nWwOPuY&t=333s) | LXk8nWwOPuY | 72 | 05:33 | 05:38 | four of the implementation plan. We can now see the recent changes that were made so let us proceed |
| [05:38](https://www.youtube.com/watch?v=LXk8nWwOPuY&t=338s) | LXk8nWwOPuY | 73 | 05:38 | 05:42 | with the review. You can observe that I am now setting everything up, analyzing all the changes |
| [05:42](https://www.youtube.com/watch?v=LXk8nWwOPuY&t=342s) | LXk8nWwOPuY | 74 | 05:42 | 05:47 | and reviewing the modified files. The files that were changed are listed here at the bottom. Let |
| [05:47](https://www.youtube.com/watch?v=LXk8nWwOPuY&t=347s) | LXk8nWwOPuY | 75 | 05:47 | 05:52 | us take a look at what it finds and whether its review can help resolve the existing errors. We |
| [05:52](https://www.youtube.com/watch?v=LXk8nWwOPuY&t=352s) | LXk8nWwOPuY | 76 | 05:52 | 05:57 | are now ready to run the review. You can now see the list of files that were reviewed. When we open |
| [05:57](https://www.youtube.com/watch?v=LXk8nWwOPuY&t=357s) | LXk8nWwOPuY | 77 | 05:57 | 06:02 | any of these, we can see that it has provided suggestions for each one. Clicking on a suggestion |
| [06:02](https://www.youtube.com/watch?v=LXk8nWwOPuY&t=362s) | LXk8nWwOPuY | 78 | 06:02 | 06:08 | opens it in detail and shows us exactly what the tool recommends. The next step in this workflow |
| [06:08](https://www.youtube.com/watch?v=LXk8nWwOPuY&t=368s) | LXk8nWwOPuY | 79 | 06:08 | 06:13 | is to hand these suggestions over to the Cursor AI agent. If you're enjoying the video, I'd really |
| [06:13](https://www.youtube.com/watch?v=LXk8nWwOPuY&t=373s) | LXk8nWwOPuY | 80 | 06:13 | 06:18 | appreciate it if you could subscribe to the channel. We're aiming to reach 25,000 subscribers |
| [06:18](https://www.youtube.com/watch?v=LXk8nWwOPuY&t=378s) | LXk8nWwOPuY | 81 | 06:18 | 06:22 | by the end of this month and your support genuinely helps. We share videos like this |
| [06:22](https://www.youtube.com/watch?v=LXk8nWwOPuY&t=382s) | LXk8nWwOPuY | 82 | 06:22 | 06:28 | three times a week so there is always something new and useful for you to explore. Now the next |
| [06:28](https://www.youtube.com/watch?v=LXk8nWwOPuY&t=388s) | LXk8nWwOPuY | 83 | 06:28 | 06:32 | step to getting those comments applied is that after you have opened them up you are going to |
| [06:32](https://www.youtube.com/watch?v=LXk8nWwOPuY&t=392s) | LXk8nWwOPuY | 84 | 06:32 | 06:37 | click on the fix with AI button. What this does is copy a set of instructions and if you look at |
| [06:37](https://www.youtube.com/watch?v=LXk8nWwOPuY&t=397s) | LXk8nWwOPuY | 85 | 06:37 | 06:41 | the bottom you will see them labeled as code gen instructions which are then copied to your |
| [06:41](https://www.youtube.com/watch?v=LXk8nWwOPuY&t=401s) | LXk8nWwOPuY | 86 | 06:41 | 06:46 | clipboard. After that you simply paste those instructions into the cursor agent. The tedious |
| [06:46](https://www.youtube.com/watch?v=LXk8nWwOPuY&t=406s) | LXk8nWwOPuY | 87 | 06:46 | 06:51 | part of this process is that you have to do it one by one for each individual comment. You need |
| [06:51](https://www.youtube.com/watch?v=LXk8nWwOPuY&t=411s) | LXk8nWwOPuY | 88 | 06:51 | 06:56 | to provide each comment separately and as you already know, these AI models generally do not |
| [06:56](https://www.youtube.com/watch?v=LXk8nWwOPuY&t=416s) | LXk8nWwOPuY | 89 | 06:56 | 07:01 | perform well when they are asked to handle multiple tasks at the same time. One thing I highly |
| [07:01](https://www.youtube.com/watch?v=LXk8nWwOPuY&t=421s) | LXk8nWwOPuY | 90 | 07:01 | 07:06 | recommend is switching to the Gemini 2.5 Pro model because in my experience that is the only model |
| [07:06](https://www.youtube.com/watch?v=LXk8nWwOPuY&t=426s) | LXk8nWwOPuY | 91 | 07:06 | 07:11 | that can reliably handle multiple instructions at once. This allows you to go ahead and give it as |
| [07:11](https://www.youtube.com/watch?v=LXk8nWwOPuY&t=431s) | LXk8nWwOPuY | 92 | 07:11 | 07:16 | many comments as you like. I have now given it three comments from the address form and at this |
| [07:16](https://www.youtube.com/watch?v=LXk8nWwOPuY&t=436s) | LXk8nWwOPuY | 93 | 07:16 | 07:20 | point I am just going to paste the CodeGen instructions into Cursor and see what it |
| [07:20](https://www.youtube.com/watch?v=LXk8nWwOPuY&t=440s) | LXk8nWwOPuY | 94 | 07:20 | 07:25 | generates and how it fixes the issues. Okay, so this is the store that was finally built. There |
| [07:25](https://www.youtube.com/watch?v=LXk8nWwOPuY&t=445s) | LXk8nWwOPuY | 95 | 07:25 | 07:30 | was an issue with components not rendering properly on the client side but that has been |
| [07:30](https://www.youtube.com/watch?v=LXk8nWwOPuY&t=450s) | LXk8nWwOPuY | 96 | 07:30 | 07:35 | resolved. The review process also played a key role in tightening up the site's security, especially |
| [07:35](https://www.youtube.com/watch?v=LXk8nWwOPuY&t=455s) | LXk8nWwOPuY | 97 | 07:35 | 07:40 | in the area of password storage which was being handled incorrectly earlier. Overall, the site is |
| [07:40](https://www.youtube.com/watch?v=LXk8nWwOPuY&t=460s) | LXk8nWwOPuY | 98 | 07:40 | 07:45 | now fully functional. All the animations are working exactly as expected. One thing I do regret |
| [07:45](https://www.youtube.com/watch?v=LXk8nWwOPuY&t=465s) | LXk8nWwOPuY | 99 | 07:45 | 07:50 | is not using ShadCN components. I had instructed the agent to manually create all the components |
| [07:50](https://www.youtube.com/watch?v=LXk8nWwOPuY&t=470s) | LXk8nWwOPuY | 100 | 07:50 | 07:55 | which in hindsight was not the best decision. That aside everything looks good and is functioning |
| [07:55](https://www.youtube.com/watch?v=LXk8nWwOPuY&t=475s) | LXk8nWwOPuY | 101 | 07:55 | 08:00 | well. There are still a few features left to implement. As I mentioned earlier I am currently |
| [08:00](https://www.youtube.com/watch?v=LXk8nWwOPuY&t=480s) | LXk8nWwOPuY | 102 | 08:00 | 08:05 | at phase 4 of the implementation plan so the final styling and polish will likely be completed in the |
| [08:05](https://www.youtube.com/watch?v=LXk8nWwOPuY&t=485s) | LXk8nWwOPuY | 103 | 08:05 | 08:11 | upcoming phases. So at the start of the video, I mentioned that I would show you how to apply my |
| [08:11](https://www.youtube.com/watch?v=LXk8nWwOPuY&t=491s) | LXk8nWwOPuY | 104 | 08:11 | 08:16 | implementation plan approach to your own projects by breaking them into small and manageable chunks. |
| [08:16](https://www.youtube.com/watch?v=LXk8nWwOPuY&t=496s) | LXk8nWwOPuY | 105 | 08:16 | 08:21 | This is exactly what I meant. You begin by briefly describing your project and defining its |
| [08:21](https://www.youtube.com/watch?v=LXk8nWwOPuY&t=501s) | LXk8nWwOPuY | 106 | 08:21 | 08:26 | specifications. In my case, I was building a Next.js front-end application that would eventually be |
| [08:26](https://www.youtube.com/watch?v=LXk8nWwOPuY&t=506s) | LXk8nWwOPuY | 107 | 08:26 | 08:31 | integrated with a fast API backend. Your project might be different, but the core idea remains the |
| [08:31](https://www.youtube.com/watch?v=LXk8nWwOPuY&t=511s) | LXk8nWwOPuY | 108 | 08:31 | 08:36 | same. You describe what you are building and which tech stack you are using. Since I was focused on |
| [08:36](https://www.youtube.com/watch?v=LXk8nWwOPuY&t=516s) | LXk8nWwOPuY | 109 | 08:36 | 08:42 | building just the Next.js front end, I instructed the agent to list all the required pages and |
| [08:42](https://www.youtube.com/watch?v=LXk8nWwOPuY&t=522s) | LXk8nWwOPuY | 110 | 08:42 | 08:48 | modules inside a structure.md file that I had already prepared. After that, I asked it to |
| [08:48](https://www.youtube.com/watch?v=LXk8nWwOPuY&t=528s) | LXk8nWwOPuY | 111 | 08:48 | 08:53 | generate a 10-phase implementation plan based on that structure. To make the workflow more autonomous |
| [08:53](https://www.youtube.com/watch?v=LXk8nWwOPuY&t=533s) | LXk8nWwOPuY | 112 | 08:53 | 08:59 | and avoid repeating instructions every time, you add a rule inside your project's cursor settings |
| [08:59](https://www.youtube.com/watch?v=LXk8nWwOPuY&t=539s) | LXk8nWwOPuY | 113 | 08:59 | 09:02 | and configure it to always keep the agent attached. |
| [09:02](https://www.youtube.com/watch?v=LXk8nWwOPuY&t=542s) | LXk8nWwOPuY | 114 | 09:02 | 09:05 | From there, the agent follows the implementation plan step by step. |
| [09:05](https://www.youtube.com/watch?v=LXk8nWwOPuY&t=545s) | LXk8nWwOPuY | 115 | 09:05 | 09:09 | If it needs any clarification, it is expected to ask before proceeding. |
| [09:09](https://www.youtube.com/watch?v=LXk8nWwOPuY&t=549s) | LXk8nWwOPuY | 116 | 09:09 | 09:12 | Once a phase begins, it marks that phase as in progress, |
| [09:13](https://www.youtube.com/watch?v=LXk8nWwOPuY&t=553s) | LXk8nWwOPuY | 117 | 09:13 | 09:16 | completes the implementation, and then commits the changes to Git locally. |
| [09:16](https://www.youtube.com/watch?v=LXk8nWwOPuY&t=556s) | LXk8nWwOPuY | 118 | 09:16 | 09:19 | At that point, you receive a prompt from CodeRabbit |
| [09:19](https://www.youtube.com/watch?v=LXk8nWwOPuY&t=559s) | LXk8nWwOPuY | 119 | 09:19 | 09:22 | indicating that it is time to start the review process. |
| [09:22](https://www.youtube.com/watch?v=LXk8nWwOPuY&t=562s) | LXk8nWwOPuY | 120 | 09:22 | 09:24 | You run the review, collect the suggestions, |
| [09:25](https://www.youtube.com/watch?v=LXk8nWwOPuY&t=565s) | LXk8nWwOPuY | 121 | 09:25 | 09:27 | and paste those suggestions back as feedback. |
| [09:27](https://www.youtube.com/watch?v=LXk8nWwOPuY&t=567s) | LXk8nWwOPuY | 122 | 09:27 | 09:30 | These suggestions now act as the user's input. |
| [09:30](https://www.youtube.com/watch?v=LXk8nWwOPuY&t=570s) | LXk8nWwOPuY | 123 | 09:30 | 09:34 | After that, you instruct Cursor to continue and it returns to the implementation plan, |
| [09:35](https://www.youtube.com/watch?v=LXk8nWwOPuY&t=575s) | LXk8nWwOPuY | 124 | 09:35 | 09:38 | marks the current phase as complete and proceeds to the next one. |
| [09:38](https://www.youtube.com/watch?v=LXk8nWwOPuY&t=578s) | LXk8nWwOPuY | 125 | 09:38 | 09:44 | This creates a smooth and structured workflow that progresses phase by phase with integrated review cycles at every step. |
| [09:44](https://www.youtube.com/watch?v=LXk8nWwOPuY&t=584s) | LXk8nWwOPuY | 126 | 09:44 | 09:49 | One improvement that could really enhance this process in my opinion is better retrieval of the review comments. |
| [09:50](https://www.youtube.com/watch?v=LXk8nWwOPuY&t=590s) | LXk8nWwOPuY | 127 | 09:50 | 09:53 | At the moment, there is a comments tab that displays everything, |
| [09:53](https://www.youtube.com/watch?v=LXk8nWwOPuY&t=593s) | LXk8nWwOPuY | 128 | 09:53 | 09:58 | but if there were a way to automatically extract and paste those comments directly into cursor, |
| [09:58](https://www.youtube.com/watch?v=LXk8nWwOPuY&t=598s) | LXk8nWwOPuY | 129 | 09:58 | 10:01 | the entire process would become much more efficient. |
| [10:01](https://www.youtube.com/watch?v=LXk8nWwOPuY&t=601s) | LXk8nWwOPuY | 130 | 10:01 | 10:03 | That brings us to the end of this video. |
| [10:03](https://www.youtube.com/watch?v=LXk8nWwOPuY&t=603s) | LXk8nWwOPuY | 131 | 10:03 | 10:07 | If you'd like to support the channel and help us keep making tutorials like this, |
| [10:07](https://www.youtube.com/watch?v=LXk8nWwOPuY&t=607s) | LXk8nWwOPuY | 132 | 10:07 | 10:09 | you can do so by using the super thanks button below. |
| [10:09](https://www.youtube.com/watch?v=LXk8nWwOPuY&t=609s) | LXk8nWwOPuY | 133 | 10:09 | 10:13 | As always, thank you for watching and I'll see you in the next one. |
