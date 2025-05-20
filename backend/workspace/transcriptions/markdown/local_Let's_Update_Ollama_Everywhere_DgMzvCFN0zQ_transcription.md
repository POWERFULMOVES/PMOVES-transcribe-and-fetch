# Transcription for Video: [DgMzvCFN0zQ](https://www.youtube.com/watch?v=DgMzvCFN0zQ)

| Timestamp Link | Video ID | Seg ID | Start | End | Text |
|---|---|---|---|---|---|
| [00:00](https://www.youtube.com/watch?v=DgMzvCFN0zQ&t=0s) | DgMzvCFN0zQ | 0 | 00:00 | 00:05 | Ollama is an amazing tool to run AI models locally on your laptop. |
| [00:05](https://www.youtube.com/watch?v=DgMzvCFN0zQ&t=5s) | DgMzvCFN0zQ | 1 | 00:05 | 00:12 | On Mac, Windows, and Linux, it's so incredibly easy to install and get up and running. |
| [00:12](https://www.youtube.com/watch?v=DgMzvCFN0zQ&t=12s) | DgMzvCFN0zQ | 2 | 00:12 | 00:16 | Far easier than any other tool for this purpose. |
| [00:16](https://www.youtube.com/watch?v=DgMzvCFN0zQ&t=16s) | DgMzvCFN0zQ | 3 | 00:16 | 00:21 | But often in the Discord, we see folks ask how to update their Ollama installation. |
| [00:21](https://www.youtube.com/watch?v=DgMzvCFN0zQ&t=21s) | DgMzvCFN0zQ | 4 | 00:21 | 00:24 | So in this video, I just wanted to show you everything you need to know to update your |
| [00:24](https://www.youtube.com/watch?v=DgMzvCFN0zQ&t=24s) | DgMzvCFN0zQ | 5 | 00:24 | 00:31 | Ollama instances to both the current version, as well as a pre-release or any past releases, |
| [00:31](https://www.youtube.com/watch?v=DgMzvCFN0zQ&t=31s) | DgMzvCFN0zQ | 6 | 00:31 | 00:33 | since that's the same process. |
| [00:33](https://www.youtube.com/watch?v=DgMzvCFN0zQ&t=33s) | DgMzvCFN0zQ | 7 | 00:33 | 00:38 | When we first started building Ollama, the install was a little bit rough, but we got |
| [00:38](https://www.youtube.com/watch?v=DgMzvCFN0zQ&t=38s) | DgMzvCFN0zQ | 8 | 00:38 | 00:42 | it in line within a couple of weeks and it's been great ever since. |
| [00:42](https://www.youtube.com/watch?v=DgMzvCFN0zQ&t=42s) | DgMzvCFN0zQ | 9 | 00:42 | 00:47 | I say we because I was on the Ollama team when we started working on it. |
| [00:47](https://www.youtube.com/watch?v=DgMzvCFN0zQ&t=47s) | DgMzvCFN0zQ | 10 | 00:47 | 00:52 | I'm no longer on the team, instead focusing on building out this YouTube channel, but |
| [00:52](https://www.youtube.com/watch?v=DgMzvCFN0zQ&t=52s) | DgMzvCFN0zQ | 11 | 00:52 | 00:56 | We're still good friends and I still talk to the team regularly. |
| [00:56](https://www.youtube.com/watch?v=DgMzvCFN0zQ&t=56s) | DgMzvCFN0zQ | 12 | 00:56 | 01:00 | This video is part of my weekly series called the Ollama Course. |
| [01:00](https://www.youtube.com/watch?v=DgMzvCFN0zQ&t=60s) | DgMzvCFN0zQ | 13 | 01:00 | 01:04 | If it's the first video you've seen, take a look at the playlist to see the rest of |
| [01:04](https://www.youtube.com/watch?v=DgMzvCFN0zQ&t=64s) | DgMzvCFN0zQ | 14 | 01:04 | 01:05 | the videos in this course. |
| [01:05](https://www.youtube.com/watch?v=DgMzvCFN0zQ&t=65s) | DgMzvCFN0zQ | 15 | 01:05 | 01:11 | I'll look at this update process from the perspective of a Mac user, a Windows user, |
| [01:11](https://www.youtube.com/watch?v=DgMzvCFN0zQ&t=71s) | DgMzvCFN0zQ | 16 | 01:11 | 01:17 | and a Linux user, as well as Docker users on Windows and Linux, in that order. |
| [01:17](https://www.youtube.com/watch?v=DgMzvCFN0zQ&t=77s) | DgMzvCFN0zQ | 17 | 01:17 | 01:23 | If you're using Ollama via WSL on Windows, you really should transition to using the |
| [01:23](https://www.youtube.com/watch?v=DgMzvCFN0zQ&t=83s) | DgMzvCFN0zQ | 18 | 01:23 | 01:28 | native Windows install since it's so much faster. |
| [01:28](https://www.youtube.com/watch?v=DgMzvCFN0zQ&t=88s) | DgMzvCFN0zQ | 19 | 01:28 | 01:34 | And if you're using Docker on Mac, then you should also switch to the native install since |
| [01:34](https://www.youtube.com/watch?v=DgMzvCFN0zQ&t=94s) | DgMzvCFN0zQ | 20 | 01:34 | 01:37 | Docker on Mac has no access to the GPU. |
| [01:37](https://www.youtube.com/watch?v=DgMzvCFN0zQ&t=97s) | DgMzvCFN0zQ | 21 | 01:37 | 01:43 | If you only care about one of those platforms, the timestamps to zoom ahead to that platform |
| [01:43](https://www.youtube.com/watch?v=DgMzvCFN0zQ&t=103s) | DgMzvCFN0zQ | 22 | 01:43 | 01:46 | should be on screen right now. |
| [01:46](https://www.youtube.com/watch?v=DgMzvCFN0zQ&t=106s) | DgMzvCFN0zQ | 23 | 01:46 | 01:48 | So Mac first. |
| [01:48](https://www.youtube.com/watch?v=DgMzvCFN0zQ&t=108s) | DgMzvCFN0zQ | 24 | 01:48 | 01:53 | There are a number of ways to install Ollama, but only one way that is recommended by the |
| [01:53](https://www.youtube.com/watch?v=DgMzvCFN0zQ&t=113s) | DgMzvCFN0zQ | 25 | 01:53 | 01:54 | team. |
| [01:54](https://www.youtube.com/watch?v=DgMzvCFN0zQ&t=114s) | DgMzvCFN0zQ | 26 | 01:54 | 01:57 | And that is the official installer on the Ollama homepage. |
| [01:57](https://www.youtube.com/watch?v=DgMzvCFN0zQ&t=117s) | DgMzvCFN0zQ | 27 | 01:57 | 02:03 | Some folks like to install with brew, but there really isn't any benefit to doing so. |
| [02:03](https://www.youtube.com/watch?v=DgMzvCFN0zQ&t=123s) | DgMzvCFN0zQ | 28 | 02:03 | 02:07 | The brew package is not maintained by the authors of Ollama. |
| [02:07](https://www.youtube.com/watch?v=DgMzvCFN0zQ&t=127s) | DgMzvCFN0zQ | 29 | 02:07 | 02:12 | Some say it's easier to upgrade, and I think that may have been true for about two weeks |
| [02:12](https://www.youtube.com/watch?v=DgMzvCFN0zQ&t=132s) | DgMzvCFN0zQ | 30 | 02:12 | 02:14 | or so back in June of 2023. |
| [02:14](https://www.youtube.com/watch?v=DgMzvCFN0zQ&t=134s) | DgMzvCFN0zQ | 31 | 02:14 | 02:19 | But since then, it's just easier to use the official installer, which is also the most |
| [02:19](https://www.youtube.com/watch?v=DgMzvCFN0zQ&t=139s) | DgMzvCFN0zQ | 32 | 02:19 | 02:22 | stable way to install Ollama. |
| [02:22](https://www.youtube.com/watch?v=DgMzvCFN0zQ&t=142s) | DgMzvCFN0zQ | 33 | 02:22 | 02:24 | So I'm assuming that you've already done that. |
| [02:24](https://www.youtube.com/watch?v=DgMzvCFN0zQ&t=144s) | DgMzvCFN0zQ | 34 | 02:24 | 02:29 | Now when there's an update to Ollama, you'll see the menu bar icon changed to show a little |
| [02:29](https://www.youtube.com/watch?v=DgMzvCFN0zQ&t=149s) | DgMzvCFN0zQ | 35 | 02:29 | 02:31 | arrow on it. |
| [02:31](https://www.youtube.com/watch?v=DgMzvCFN0zQ&t=151s) | DgMzvCFN0zQ | 36 | 02:31 | 02:34 | Click the icon and choose restart to update. |
| [02:34](https://www.youtube.com/watch?v=DgMzvCFN0zQ&t=154s) | DgMzvCFN0zQ | 37 | 02:34 | 02:39 | It's possible that the text shown will change at some point in the future, but it should |
| [02:39](https://www.youtube.com/watch?v=DgMzvCFN0zQ&t=159s) | DgMzvCFN0zQ | 38 | 02:39 | 02:41 | be something like that. |
| [02:41](https://www.youtube.com/watch?v=DgMzvCFN0zQ&t=161s) | DgMzvCFN0zQ | 39 | 02:41 | 02:45 | Ollama will update itself and be back up and running for you to use. |
| [02:45](https://www.youtube.com/watch?v=DgMzvCFN0zQ&t=165s) | DgMzvCFN0zQ | 40 | 02:45 | 02:46 | And that's it. |
| [02:46](https://www.youtube.com/watch?v=DgMzvCFN0zQ&t=166s) | DgMzvCFN0zQ | 41 | 02:46 | 02:52 | nothing else for you to do. How about if you want to update to a new pre-release version? Well, |
| [02:52](https://www.youtube.com/watch?v=DgMzvCFN0zQ&t=172s) | DgMzvCFN0zQ | 42 | 02:52 | 02:57 | just go to the Olamo homepage and then click on the link to GitHub. Then on the right side, |
| [02:57](https://www.youtube.com/watch?v=DgMzvCFN0zQ&t=177s) | DgMzvCFN0zQ | 43 | 02:57 | 03:03 | click on releases. Way at the top, there's the latest version. If there's a pre-release, |
| [03:03](https://www.youtube.com/watch?v=DgMzvCFN0zQ&t=183s) | DgMzvCFN0zQ | 44 | 03:03 | 03:08 | then that's going to be at the top. Otherwise, it's the latest full release. A pre-release is |
| [03:08](https://www.youtube.com/watch?v=DgMzvCFN0zQ&t=188s) | DgMzvCFN0zQ | 45 | 03:08 | 03:14 | just a version that's still not fully fleshed out and may have some issues. You shouldn't update to |
| [03:14](https://www.youtube.com/watch?v=DgMzvCFN0zQ&t=194s) | DgMzvCFN0zQ | 46 | 03:14 | 03:19 | this version unless you need a specific feature it promises to solve. If you want to go back to |
| [03:19](https://www.youtube.com/watch?v=DgMzvCFN0zQ&t=199s) | DgMzvCFN0zQ | 47 | 03:19 | 03:25 | an earlier version, then scroll down on the releases page to find whichever version you want. |
| [03:25](https://www.youtube.com/watch?v=DgMzvCFN0zQ&t=205s) | DgMzvCFN0zQ | 48 | 03:25 | 03:32 | Expand assets and then you'll want to download the file called olamadarwin.zip. This is the |
| [03:32](https://www.youtube.com/watch?v=DgMzvCFN0zQ&t=212s) | DgMzvCFN0zQ | 49 | 03:32 | 03:38 | full installer and is the file you most probably want. Make sure you click the olama icon in the |
| [03:38](https://www.youtube.com/watch?v=DgMzvCFN0zQ&t=218s) | DgMzvCFN0zQ | 50 | 03:38 | 03:45 | the menu bar and choose Quit. Then unzip Ollama Darwin and run the Ollama app that's extracted. |
| [03:45](https://www.youtube.com/watch?v=DgMzvCFN0zQ&t=225s) | DgMzvCFN0zQ | 51 | 03:45 | 03:49 | Since the app is probably not in the correct directory, it'll prompt to move it to the |
| [03:49](https://www.youtube.com/watch?v=DgMzvCFN0zQ&t=229s) | DgMzvCFN0zQ | 52 | 03:49 | 03:53 | right place. After that's happened, you should be all set. |
| [03:53](https://www.youtube.com/watch?v=DgMzvCFN0zQ&t=233s) | DgMzvCFN0zQ | 53 | 03:53 | 04:00 | So that was pretty easy. You know, it's almost as easy as giving a like and subscribe to |
| [04:00](https://www.youtube.com/watch?v=DgMzvCFN0zQ&t=240s) | DgMzvCFN0zQ | 54 | 04:00 | 04:05 | this video. That makes such a huge difference to the channel and I greatly appreciate everyone |
| [04:05](https://www.youtube.com/watch?v=DgMzvCFN0zQ&t=245s) | DgMzvCFN0zQ | 55 | 04:05 | 04:08 | who does it. Thanks so much for being here. |
| [04:08](https://www.youtube.com/watch?v=DgMzvCFN0zQ&t=248s) | DgMzvCFN0zQ | 56 | 04:08 | 04:10 | Now let's move on to Windows. |
| [04:10](https://www.youtube.com/watch?v=DgMzvCFN0zQ&t=250s) | DgMzvCFN0zQ | 57 | 04:10 | 04:15 | As with the Mac, there are different alternate ways to install Ollama, but most of the time |
| [04:15](https://www.youtube.com/watch?v=DgMzvCFN0zQ&t=255s) | DgMzvCFN0zQ | 58 | 04:15 | 04:21 | you really should be using the default installer which you can find on the Ollama homepage. |
| [04:21](https://www.youtube.com/watch?v=DgMzvCFN0zQ&t=261s) | DgMzvCFN0zQ | 59 | 04:21 | 04:26 | Once Ollama is installed, it'll alert you when there's a new version to install. |
| [04:26](https://www.youtube.com/watch?v=DgMzvCFN0zQ&t=266s) | DgMzvCFN0zQ | 60 | 04:26 | 04:30 | So click the Ollama icon on the taskbar, then click Restart to update. |
| [04:30](https://www.youtube.com/watch?v=DgMzvCFN0zQ&t=270s) | DgMzvCFN0zQ | 61 | 04:30 | 04:34 | Ollama will download the latest version and update itself for you. |
| [04:34](https://www.youtube.com/watch?v=DgMzvCFN0zQ&t=274s) | DgMzvCFN0zQ | 62 | 04:34 | 04:39 | How about if you want to install something other than the latest released version? |
| [04:39](https://www.youtube.com/watch?v=DgMzvCFN0zQ&t=279s) | DgMzvCFN0zQ | 63 | 04:39 | 04:41 | Maybe it's a pre-release or even an earlier version. |
| [04:42](https://www.youtube.com/watch?v=DgMzvCFN0zQ&t=282s) | DgMzvCFN0zQ | 64 | 04:42 | 04:44 | Well, go to olama.com and then click on GitHub. |
| [04:45](https://www.youtube.com/watch?v=DgMzvCFN0zQ&t=285s) | DgMzvCFN0zQ | 65 | 04:45 | 04:48 | On the right is releases and you can see a list of all the available releases. |
| [04:49](https://www.youtube.com/watch?v=DgMzvCFN0zQ&t=289s) | DgMzvCFN0zQ | 66 | 04:49 | 04:51 | With the latest one up at the top. |
| [04:51](https://www.youtube.com/watch?v=DgMzvCFN0zQ&t=291s) | DgMzvCFN0zQ | 67 | 04:51 | 04:55 | Scroll up or down to find the pre-release you want or an older version. |
| [04:56](https://www.youtube.com/watch?v=DgMzvCFN0zQ&t=296s) | DgMzvCFN0zQ | 68 | 04:56 | 04:59 | Expand assets and find olamasetup.exe. |
| [04:59](https://www.youtube.com/watch?v=DgMzvCFN0zQ&t=299s) | DgMzvCFN0zQ | 69 | 04:59 | 05:01 | Download that. |
| [05:01](https://www.youtube.com/watch?v=DgMzvCFN0zQ&t=301s) | DgMzvCFN0zQ | 70 | 05:01 | 05:05 | Then make sure to quit your running olama if it's running right now. |
| [05:05](https://www.youtube.com/watch?v=DgMzvCFN0zQ&t=305s) | DgMzvCFN0zQ | 71 | 05:05 | 05:08 | Run olamasetup and walk through the prompts. |
| [05:08](https://www.youtube.com/watch?v=DgMzvCFN0zQ&t=308s) | DgMzvCFN0zQ | 72 | 05:08 | 05:12 | And you are now all set on your chosen version of Ollama on Windows. |
| [05:13](https://www.youtube.com/watch?v=DgMzvCFN0zQ&t=313s) | DgMzvCFN0zQ | 73 | 05:13 | 05:14 | Okay, on to Linux. |
| [05:15](https://www.youtube.com/watch?v=DgMzvCFN0zQ&t=315s) | DgMzvCFN0zQ | 74 | 05:15 | 05:20 | Just like we saw with Mac and Windows, there are a few different ways to install Ollama on Linux. |
| [05:20](https://www.youtube.com/watch?v=DgMzvCFN0zQ&t=320s) | DgMzvCFN0zQ | 75 | 05:20 | 05:23 | The best is the official install script. |
| [05:24](https://www.youtube.com/watch?v=DgMzvCFN0zQ&t=324s) | DgMzvCFN0zQ | 76 | 05:24 | 05:29 | There are other install packages available, but they sometimes default to pre-releases and cause problems. |
| [05:29](https://www.youtube.com/watch?v=DgMzvCFN0zQ&t=329s) | DgMzvCFN0zQ | 77 | 05:29 | 05:36 | To update Ollama to the latest version on Linux, you need to do a different process than on the other platforms. |
| [05:36](https://www.youtube.com/watch?v=DgMzvCFN0zQ&t=336s) | DgMzvCFN0zQ | 78 | 05:36 | 05:41 | Since there is no menu bar or taskbar icon to click, you need to simply run the install script again. |
| [05:42](https://www.youtube.com/watch?v=DgMzvCFN0zQ&t=342s) | DgMzvCFN0zQ | 79 | 05:42 | 05:49 | So that's curl-fssl https://olama.com install.sh |
| [05:49](https://www.youtube.com/watch?v=DgMzvCFN0zQ&t=349s) | DgMzvCFN0zQ | 80 | 05:49 | 05:51 | And then you pipe that to sh. |
| [05:52](https://www.youtube.com/watch?v=DgMzvCFN0zQ&t=352s) | DgMzvCFN0zQ | 81 | 05:52 | 05:54 | It'll get up and running super quickly. |
| [05:54](https://www.youtube.com/watch?v=DgMzvCFN0zQ&t=354s) | DgMzvCFN0zQ | 82 | 05:54 | 06:00 | If you want to see what that script is doing, simply take a look at the script at the URL, and you can see it's pretty simple. |
| [06:00](https://www.youtube.com/watch?v=DgMzvCFN0zQ&t=360s) | DgMzvCFN0zQ | 83 | 06:00 | 06:04 | If you want to install a different version, such as a pre-release or older version, |
| [06:05](https://www.youtube.com/watch?v=DgMzvCFN0zQ&t=365s) | DgMzvCFN0zQ | 84 | 06:05 | 06:10 | just set the olama version environment variable at the command line before running the shell. |
| [06:10](https://www.youtube.com/watch?v=DgMzvCFN0zQ&t=370s) | DgMzvCFN0zQ | 85 | 06:10 | 06:17 | So curl-fssl htps://olama.com install.sh |
| [06:17](https://www.youtube.com/watch?v=DgMzvCFN0zQ&t=377s) | DgMzvCFN0zQ | 86 | 06:17 | 06:25 | Then pipe that to olama version equals 0.4.0 or whatever version you like, then sh. |
| [06:25](https://www.youtube.com/watch?v=DgMzvCFN0zQ&t=385s) | DgMzvCFN0zQ | 87 | 06:25 | 06:28 | It really is that easy. |
| [06:28](https://www.youtube.com/watch?v=DgMzvCFN0zQ&t=388s) | DgMzvCFN0zQ | 88 | 06:28 | 06:32 | The final platform to look at is Docker. |
| [06:32](https://www.youtube.com/watch?v=DgMzvCFN0zQ&t=392s) | DgMzvCFN0zQ | 89 | 06:32 | 06:37 | There's nothing specific about Ollama when updating it using Docker. |
| [06:37](https://www.youtube.com/watch?v=DgMzvCFN0zQ&t=397s) | DgMzvCFN0zQ | 90 | 06:37 | 06:42 | It's the same process for any Docker-based application. |
| [06:43](https://www.youtube.com/watch?v=DgMzvCFN0zQ&t=403s) | DgMzvCFN0zQ | 91 | 06:43 | 06:47 | Stop the container, remove the image, pull the latest version from Docker Hub, |
| [06:47](https://www.youtube.com/watch?v=DgMzvCFN0zQ&t=407s) | DgMzvCFN0zQ | 92 | 06:47 | 06:50 | then run it again using the same command you did before. |
| [06:51](https://www.youtube.com/watch?v=DgMzvCFN0zQ&t=411s) | DgMzvCFN0zQ | 93 | 06:51 | 06:54 | Because you mounted a volume for the models, |
| [06:54](https://www.youtube.com/watch?v=DgMzvCFN0zQ&t=414s) | DgMzvCFN0zQ | 94 | 06:54 | 06:57 | they're intact when deleting the image and starting again. |
| [06:57](https://www.youtube.com/watch?v=DgMzvCFN0zQ&t=417s) | DgMzvCFN0zQ | 95 | 06:57 | 07:03 | So that's easy, but even easier is to use a second container called Watchtower. |
| [07:04](https://www.youtube.com/watch?v=DgMzvCFN0zQ&t=424s) | DgMzvCFN0zQ | 96 | 07:04 | 07:09 | Watchtower runs at a regular interval and will then update all the containers you want to update. |
| [07:10](https://www.youtube.com/watch?v=DgMzvCFN0zQ&t=430s) | DgMzvCFN0zQ | 97 | 07:10 | 07:12 | Here's the Docker Compose file I use for Watchtower. |
| [07:13](https://www.youtube.com/watch?v=DgMzvCFN0zQ&t=433s) | DgMzvCFN0zQ | 98 | 07:13 | 07:16 | It runs every few hours and keeps things up to date. |
| [07:16](https://www.youtube.com/watch?v=DgMzvCFN0zQ&t=436s) | DgMzvCFN0zQ | 99 | 07:16 | 07:20 | I do this on a server on which I run N8n and searching and no code to be, |
| [07:21](https://www.youtube.com/watch?v=DgMzvCFN0zQ&t=441s) | DgMzvCFN0zQ | 100 | 07:21 | 07:22 | and I never have to think about updating. |
| [07:23](https://www.youtube.com/watch?v=DgMzvCFN0zQ&t=443s) | DgMzvCFN0zQ | 101 | 07:23 | 07:24 | It's pretty amazing. |
| [07:24](https://www.youtube.com/watch?v=DgMzvCFN0zQ&t=444s) | DgMzvCFN0zQ | 102 | 07:24 | 07:33 | And that is pretty much everything you need to know about updating Ollama on every single supported platform. |
| [07:34](https://www.youtube.com/watch?v=DgMzvCFN0zQ&t=454s) | DgMzvCFN0zQ | 103 | 07:34 | 07:37 | It's pretty painless regardless of the platform you use. |
| [07:38](https://www.youtube.com/watch?v=DgMzvCFN0zQ&t=458s) | DgMzvCFN0zQ | 104 | 07:38 | 07:41 | I hope this was useful to you and that you enjoyed this video. |
| [07:42](https://www.youtube.com/watch?v=DgMzvCFN0zQ&t=462s) | DgMzvCFN0zQ | 105 | 07:42 | 07:43 | Thanks so much for watching. Goodbye. |
