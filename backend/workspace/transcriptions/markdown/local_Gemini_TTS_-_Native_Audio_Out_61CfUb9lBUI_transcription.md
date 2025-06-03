# Transcription for Video: [61CfUb9lBUI](https://www.youtube.com/watch?v=61CfUb9lBUI)

| Timestamp Link | Video ID | Seg ID | Start | End | Text |
|---|---|---|---|---|---|
| [00:00](https://www.youtube.com/watch?v=61CfUb9lBUI&t=0s) | 61CfUb9lBUI | 0 | 00:00 | 00:05 | Okay, so one of the things that got released last week at Google I.O. was actually something |
| [00:05](https://www.youtube.com/watch?v=61CfUb9lBUI&t=5s) | 61CfUb9lBUI | 1 | 00:05 | 00:09 | that got announced back in December when they released Gemini 2.0. |
| [00:09](https://www.youtube.com/watch?v=61CfUb9lBUI&t=9s) | 61CfUb9lBUI | 2 | 00:09 | 00:12 | And this is the whole idea of native audio out. |
| [00:13](https://www.youtube.com/watch?v=61CfUb9lBUI&t=13s) | 61CfUb9lBUI | 3 | 00:13 | 00:18 | While a version of this was done for the Gemini 2.0 models, and I tested it back then, I think |
| [00:18](https://www.youtube.com/watch?v=61CfUb9lBUI&t=18s) | 61CfUb9lBUI | 4 | 00:18 | 00:24 | for various reasons, Google just felt that it wasn't right for prime time, perhaps in |
| [00:24](https://www.youtube.com/watch?v=61CfUb9lBUI&t=24s) | 61CfUb9lBUI | 5 | 00:24 | 00:27 | what you could do with it for controlling the speech generation, etc. |
| [00:27](https://www.youtube.com/watch?v=61CfUb9lBUI&t=27s) | 61CfUb9lBUI | 6 | 00:27 | 00:33 | trust. So last week they did release this. It's now in preview. Anyone can use it. In this video, |
| [00:33](https://www.youtube.com/watch?v=61CfUb9lBUI&t=33s) | 61CfUb9lBUI | 7 | 00:33 | 00:38 | I'm going to go through a notebook of code and show you actually how you can do it. But let's |
| [00:38](https://www.youtube.com/watch?v=61CfUb9lBUI&t=38s) | 61CfUb9lBUI | 8 | 00:38 | 00:44 | look at sort of just quickly what you can actually do. So you can do single speaker text to speech |
| [00:44](https://www.youtube.com/watch?v=61CfUb9lBUI&t=44s) | 61CfUb9lBUI | 9 | 00:44 | 00:52 | out with this. You can also do multi-speaker text to speech out. So one of the cool things with this |
| [00:52](https://www.youtube.com/watch?v=61CfUb9lBUI&t=52s) | 61CfUb9lBUI | 10 | 00:52 | 00:59 | is you can actually recreate the kind of podcasts that were done by Notebook LM, where you've got |
| [00:59](https://www.youtube.com/watch?v=61CfUb9lBUI&t=59s) | 61CfUb9lBUI | 11 | 00:59 | 01:05 | two people speaking to each other, even things like cutting each other off or being able to |
| [01:05](https://www.youtube.com/watch?v=61CfUb9lBUI&t=65s) | 61CfUb9lBUI | 12 | 01:05 | 01:10 | laugh at a joke. All of those things can actually be done with this. So being a little bit different |
| [01:10](https://www.youtube.com/watch?v=61CfUb9lBUI&t=70s) | 61CfUb9lBUI | 13 | 01:10 | 01:16 | than a normal TTS system here, not only can you tell it what you want it to say, you can actually |
| [01:16](https://www.youtube.com/watch?v=61CfUb9lBUI&t=76s) | 61CfUb9lBUI | 14 | 01:16 | 01:23 | give sort of descriptions of how you want it to be said. So if you want the model to be laughing, |
| [01:23](https://www.youtube.com/watch?v=61CfUb9lBUI&t=83s) | 61CfUb9lBUI | 15 | 01:23 | 01:30 | if you want the model to whisper or to speak in a certain way, we're able to do that by controlling |
| [01:30](https://www.youtube.com/watch?v=61CfUb9lBUI&t=90s) | 61CfUb9lBUI | 16 | 01:30 | 01:35 | the speech style with the prompts. And you can see that this is one of the key things about this. |
| [01:35](https://www.youtube.com/watch?v=61CfUb9lBUI&t=95s) | 61CfUb9lBUI | 17 | 01:35 | 01:40 | Now, like I said before, this is still in preview. It's not actually the Gemini 2 models anymore. |
| [01:40](https://www.youtube.com/watch?v=61CfUb9lBUI&t=100s) | 61CfUb9lBUI | 18 | 01:40 | 01:44 | This is a Gemini 2.5 TTS model. |
| [01:44](https://www.youtube.com/watch?v=61CfUb9lBUI&t=104s) | 61CfUb9lBUI | 19 | 01:44 | 01:49 | If we come across to the AI studio, we can actually come down to native speech generation |
| [01:49](https://www.youtube.com/watch?v=61CfUb9lBUI&t=109s) | 61CfUb9lBUI | 20 | 01:49 | 01:56 | and we're able to generate either single speaker audio here or the multi-speaker audio here. |
| [01:56](https://www.youtube.com/watch?v=61CfUb9lBUI&t=116s) | 61CfUb9lBUI | 21 | 01:56 | 02:00 | So if you want to do it via the UI, you can certainly come in and do this. |
| [02:00](https://www.youtube.com/watch?v=61CfUb9lBUI&t=120s) | 61CfUb9lBUI | 22 | 02:00 | 02:04 | If you see down here, we can actually also even listen to the different voices. |
| [02:05](https://www.youtube.com/watch?v=61CfUb9lBUI&t=125s) | 61CfUb9lBUI | 23 | 02:05 | 02:06 | Ready to build something awesome today? |
| [02:07](https://www.youtube.com/watch?v=61CfUb9lBUI&t=127s) | 61CfUb9lBUI | 24 | 02:07 | 02:08 | Got a project in mind? |
| [02:08](https://www.youtube.com/watch?v=61CfUb9lBUI&t=128s) | 61CfUb9lBUI | 25 | 02:08 | 02:09 | What do you want to explore? |
| [02:10](https://www.youtube.com/watch?v=61CfUb9lBUI&t=130s) | 61CfUb9lBUI | 26 | 02:10 | 02:11 | Ready to make something amazing? |
| [02:11](https://www.youtube.com/watch?v=61CfUb9lBUI&t=131s) | 61CfUb9lBUI | 27 | 02:11 | 02:16 | So while all of this can be done in the UI, I actually want to jump into the code and |
| [02:16](https://www.youtube.com/watch?v=61CfUb9lBUI&t=136s) | 61CfUb9lBUI | 28 | 02:16 | 02:22 | look at how we can actually do this via code for generating single speaker things. |
| [02:22](https://www.youtube.com/watch?v=61CfUb9lBUI&t=142s) | 61CfUb9lBUI | 29 | 02:22 | 02:26 | So if you wanted to do like an audio book reading or something like that, and also to |
| [02:26](https://www.youtube.com/watch?v=61CfUb9lBUI&t=146s) | 61CfUb9lBUI | 30 | 02:26 | 02:29 | be able to generate multi-speaker interactions. |
| [02:29](https://www.youtube.com/watch?v=61CfUb9lBUI&t=149s) | 61CfUb9lBUI | 31 | 02:29 | 02:33 | So if you wanted to do like the notebook LM kind of stuff, let's just jump straight into |
| [02:33](https://www.youtube.com/watch?v=61CfUb9lBUI&t=153s) | 61CfUb9lBUI | 32 | 02:33 | 02:36 | the code and have a play with what you can do with it there. |
| [02:36](https://www.youtube.com/watch?v=61CfUb9lBUI&t=156s) | 61CfUb9lBUI | 33 | 02:36 | 02:41 | Okay, so jumping into the code, the first thing you want to do is make sure you've got |
| [02:41](https://www.youtube.com/watch?v=61CfUb9lBUI&t=161s) | 61CfUb9lBUI | 34 | 02:41 | 02:44 | a recent version of the Gemini API. |
| [02:45](https://www.youtube.com/watch?v=61CfUb9lBUI&t=165s) | 61CfUb9lBUI | 35 | 02:45 | 02:49 | So there's Google Gen AI in there so that it will actually work. |
| [02:50](https://www.youtube.com/watch?v=61CfUb9lBUI&t=170s) | 61CfUb9lBUI | 36 | 02:50 | 02:51 | In this case, I'm using it in Google Colab. |
| [02:52](https://www.youtube.com/watch?v=61CfUb9lBUI&t=172s) | 61CfUb9lBUI | 37 | 02:52 | 02:55 | Over the weekend, I was actually doing stuff with scripts and stuff like that. |
| [02:55](https://www.youtube.com/watch?v=61CfUb9lBUI&t=175s) | 61CfUb9lBUI | 38 | 02:55 | 02:58 | I'll talk a little bit more about some of the things I noticed if you're doing scripts |
| [02:58](https://www.youtube.com/watch?v=61CfUb9lBUI&t=178s) | 61CfUb9lBUI | 39 | 02:58 | 02:59 | in there. |
| [02:59](https://www.youtube.com/watch?v=61CfUb9lBUI&t=179s) | 61CfUb9lBUI | 40 | 02:59 | 03:00 | You will need a key. |
| [03:00](https://www.youtube.com/watch?v=61CfUb9lBUI&t=180s) | 61CfUb9lBUI | 41 | 03:00 | 03:05 | So if you're doing Colab, this is probably the easiest way just to put the key in your |
| [03:05](https://www.youtube.com/watch?v=61CfUb9lBUI&t=185s) | 61CfUb9lBUI | 42 | 03:05 | 03:05 | secrets. |
| [03:05](https://www.youtube.com/watch?v=61CfUb9lBUI&t=185s) | 61CfUb9lBUI | 43 | 03:05 | 03:09 | initialize the SDK and we want to get a list of the models. |
| [03:10](https://www.youtube.com/watch?v=61CfUb9lBUI&t=190s) | 61CfUb9lBUI | 44 | 03:10 | 03:13 | So here I'm just looking for the actual models with the TTS. |
| [03:14](https://www.youtube.com/watch?v=61CfUb9lBUI&t=194s) | 61CfUb9lBUI | 45 | 03:14 | 03:16 | So there are two models currently available. |
| [03:16](https://www.youtube.com/watch?v=61CfUb9lBUI&t=196s) | 61CfUb9lBUI | 46 | 03:16 | 03:22 | Both of them are in preview, but we've got a 2.5 flash model and a 2.5 pro model. |
| [03:22](https://www.youtube.com/watch?v=61CfUb9lBUI&t=202s) | 61CfUb9lBUI | 47 | 03:22 | 03:24 | So experiment around. |
| [03:24](https://www.youtube.com/watch?v=61CfUb9lBUI&t=204s) | 61CfUb9lBUI | 48 | 03:24 | 03:27 | I actually find the voices on the flash one to work out really well. |
| [03:27](https://www.youtube.com/watch?v=61CfUb9lBUI&t=207s) | 61CfUb9lBUI | 49 | 03:27 | 03:33 | So honestly, I haven't been using the pro one that much, but you may find for sort of |
| [03:33](https://www.youtube.com/watch?v=61CfUb9lBUI&t=213s) | 61CfUb9lBUI | 50 | 03:33 | 03:39 | multi-speaker or things where you're describing the emotions more that maybe the 2.5 Pro works |
| [03:39](https://www.youtube.com/watch?v=61CfUb9lBUI&t=219s) | 61CfUb9lBUI | 51 | 03:39 | 03:44 | better for you. All right. Once we've got that going, so this would be a normal call just to |
| [03:44](https://www.youtube.com/watch?v=61CfUb9lBUI&t=224s) | 61CfUb9lBUI | 52 | 03:44 | 03:51 | generate some text, right? With Gemini. To do a call for the basic TTS, it's honestly not that |
| [03:51](https://www.youtube.com/watch?v=61CfUb9lBUI&t=231s) | 61CfUb9lBUI | 53 | 03:51 | 03:56 | much different. We've still got the same things we're bringing in. The key thing that we need to |
| [03:56](https://www.youtube.com/watch?v=61CfUb9lBUI&t=236s) | 61CfUb9lBUI | 54 | 03:56 | 04:04 | define is the prompt and the actual voice. Now the prompts, you tend to basically say up front |
| [04:04](https://www.youtube.com/watch?v=61CfUb9lBUI&t=244s) | 61CfUb9lBUI | 55 | 04:04 | 04:09 | how you want the thing to be said, and then actually what they're going to say. So in this |
| [04:09](https://www.youtube.com/watch?v=61CfUb9lBUI&t=249s) | 61CfUb9lBUI | 56 | 04:09 | 04:15 | case, I'm saying say excitedly, that's right, Gemini now has text to speech, right? Okay. So |
| [04:15](https://www.youtube.com/watch?v=61CfUb9lBUI&t=255s) | 61CfUb9lBUI | 57 | 04:15 | 04:21 | the actual call is pretty simple. We pass in the model, we pass in the prompt, and then we've got |
| [04:21](https://www.youtube.com/watch?v=61CfUb9lBUI&t=261s) | 61CfUb9lBUI | 58 | 04:21 | 04:25 | to configure the response modality is going to be audio. |
| [04:25](https://www.youtube.com/watch?v=61CfUb9lBUI&t=265s) | 61CfUb9lBUI | 59 | 04:25 | 04:29 | And we want to configure both the speech config and the voice config. |
| [04:29](https://www.youtube.com/watch?v=61CfUb9lBUI&t=269s) | 61CfUb9lBUI | 60 | 04:29 | 04:32 | So the voice config is actually in the speech config. |
| [04:32](https://www.youtube.com/watch?v=61CfUb9lBUI&t=272s) | 61CfUb9lBUI | 61 | 04:32 | 04:35 | And that's basically just how we pass in the voice. |
| [04:35](https://www.youtube.com/watch?v=61CfUb9lBUI&t=275s) | 61CfUb9lBUI | 62 | 04:35 | 04:36 | So you can see this in here. |
| [04:36](https://www.youtube.com/watch?v=61CfUb9lBUI&t=276s) | 61CfUb9lBUI | 63 | 04:36 | 04:39 | Now, there are other things that we could put in there about what |
| [04:39](https://www.youtube.com/watch?v=61CfUb9lBUI&t=279s) | 61CfUb9lBUI | 64 | 04:39 | 04:41 | language it is and stuff like that. |
| [04:41](https://www.youtube.com/watch?v=61CfUb9lBUI&t=281s) | 61CfUb9lBUI | 65 | 04:41 | 04:44 | If you do want to do something that's perhaps not English, go and have a |
| [04:44](https://www.youtube.com/watch?v=61CfUb9lBUI&t=284s) | 61CfUb9lBUI | 66 | 04:44 | 04:49 | look at how you would set that up with the actual speech and voice config in there. |
| [04:49](https://www.youtube.com/watch?v=61CfUb9lBUI&t=289s) | 61CfUb9lBUI | 67 | 04:49 | 04:55 | Once we've got that done, we can basically just trigger our call, get our response back. |
| [04:56](https://www.youtube.com/watch?v=61CfUb9lBUI&t=296s) | 61CfUb9lBUI | 68 | 04:56 | 05:00 | And you'll see that the data for this is actually in the candidates that come back in here. |
| [05:01](https://www.youtube.com/watch?v=61CfUb9lBUI&t=301s) | 61CfUb9lBUI | 69 | 05:01 | 05:12 | Now, one of the things that I found, I'm not sure why, but when I was doing this with scripts rather than in Colab, was that I needed to take this data and actually convert it to Base64. |
| [05:13](https://www.youtube.com/watch?v=61CfUb9lBUI&t=313s) | 61CfUb9lBUI | 70 | 05:13 | 05:15 | I don't seem to need to do that in the Colab. |
| [05:16](https://www.youtube.com/watch?v=61CfUb9lBUI&t=316s) | 61CfUb9lBUI | 71 | 05:16 | 05:17 | It's working fine here. |
| [05:17](https://www.youtube.com/watch?v=61CfUb9lBUI&t=317s) | 61CfUb9lBUI | 72 | 05:17 | 05:22 | with my scripts I was having issues and I tried that and that fixed it. The other thing is you'll |
| [05:22](https://www.youtube.com/watch?v=61CfUb9lBUI&t=322s) | 61CfUb9lBUI | 73 | 05:22 | 05:27 | see is once you get something back you're going to be able to look at the actual metadata so if |
| [05:27](https://www.youtube.com/watch?v=61CfUb9lBUI&t=327s) | 61CfUb9lBUI | 74 | 05:27 | 05:32 | you want to see how many tokens that it actually took and stuff like that I'm not sure exactly how |
| [05:32](https://www.youtube.com/watch?v=61CfUb9lBUI&t=332s) | 61CfUb9lBUI | 75 | 05:32 | 05:38 | they're going to charge for these tokens versus normal tokens whether the price is the same. |
| [05:38](https://www.youtube.com/watch?v=61CfUb9lBUI&t=338s) | 61CfUb9lBUI | 76 | 05:38 | 05:44 | I think while it's in preview perhaps that hasn't been sorted out and looking at it in AI studio I |
| [05:44](https://www.youtube.com/watch?v=61CfUb9lBUI&t=344s) | 61CfUb9lBUI | 77 | 05:44 | 05:46 | don't see any information about it there. |
| [05:47](https://www.youtube.com/watch?v=61CfUb9lBUI&t=347s) | 61CfUb9lBUI | 78 | 05:47 | 05:50 | Remember, AI Studio is really good if you want to actually audition the different voices. |
| [05:51](https://www.youtube.com/watch?v=61CfUb9lBUI&t=351s) | 61CfUb9lBUI | 79 | 05:51 | 05:52 | You can come in here. |
| [05:52](https://www.youtube.com/watch?v=61CfUb9lBUI&t=352s) | 61CfUb9lBUI | 80 | 05:52 | 05:56 | I can see there's a whole bunch of different voices in there that we can audition to work |
| [05:56](https://www.youtube.com/watch?v=61CfUb9lBUI&t=356s) | 61CfUb9lBUI | 81 | 05:56 | 05:59 | out, okay, what are the voices that we like the most for this? |
| [06:00](https://www.youtube.com/watch?v=61CfUb9lBUI&t=360s) | 61CfUb9lBUI | 82 | 06:00 | 06:04 | Now, once you basically got that data out, you want to save that. |
| [06:04](https://www.youtube.com/watch?v=61CfUb9lBUI&t=364s) | 61CfUb9lBUI | 83 | 06:04 | 06:08 | So that's what this function at the top is just for saving it to a web file for you. |
| [06:09](https://www.youtube.com/watch?v=61CfUb9lBUI&t=369s) | 61CfUb9lBUI | 84 | 06:09 | 06:11 | And you can see that the sample rate is 24K in there. |
| [06:12](https://www.youtube.com/watch?v=61CfUb9lBUI&t=372s) | 61CfUb9lBUI | 85 | 06:12 | 06:14 | Once we've got that, we can basically play this out. |
| [06:14](https://www.youtube.com/watch?v=61CfUb9lBUI&t=374s) | 61CfUb9lBUI | 86 | 06:14 | 06:18 | That's right. Gemini now has text-to-speech. |
| [06:18](https://www.youtube.com/watch?v=61CfUb9lBUI&t=378s) | 61CfUb9lBUI | 87 | 06:18 | 06:25 | So you notice there that she didn't say the say excitedly. She just started with that's right. |
| [06:25](https://www.youtube.com/watch?v=61CfUb9lBUI&t=385s) | 61CfUb9lBUI | 88 | 06:25 | 06:30 | Gemini now has text-to-speech. So you can sort of front load your description of how you want them |
| [06:30](https://www.youtube.com/watch?v=61CfUb9lBUI&t=390s) | 61CfUb9lBUI | 89 | 06:30 | 06:35 | to actually speak. And you can do it for each prompt that you're going to pass in there. |
| [06:36](https://www.youtube.com/watch?v=61CfUb9lBUI&t=396s) | 61CfUb9lBUI | 90 | 06:36 | 06:40 | And then it will be able to interpret that out. All right. Now what I did next was basically just |
| [06:40](https://www.youtube.com/watch?v=61CfUb9lBUI&t=400s) | 61CfUb9lBUI | 91 | 06:40 | 06:45 | put it together as a function and now we can reuse it for a bunch of different things. |
| [06:45](https://www.youtube.com/watch?v=61CfUb9lBUI&t=405s) | 61CfUb9lBUI | 92 | 06:45 | 06:49 | So just to show you some different examples of this, we're using different voice here. |
| [06:49](https://www.youtube.com/watch?v=61CfUb9lBUI&t=409s) | 61CfUb9lBUI | 93 | 06:49 | 06:53 | And I'm now just saying, whisper softly and passing it in. |
| [06:53](https://www.youtube.com/watch?v=61CfUb9lBUI&t=413s) | 61CfUb9lBUI | 94 | 06:53 | 06:55 | And we can see that's going to sound like. |
| [06:55](https://www.youtube.com/watch?v=61CfUb9lBUI&t=415s) | 61CfUb9lBUI | 95 | 06:55 | 06:56 | That's right. |
| [06:56](https://www.youtube.com/watch?v=61CfUb9lBUI&t=416s) | 61CfUb9lBUI | 96 | 06:56 | 07:00 | Gemini now has text to speech. |
| [07:00](https://www.youtube.com/watch?v=61CfUb9lBUI&t=420s) | 61CfUb9lBUI | 97 | 07:00 | 07:00 | Okay. |
| [07:00](https://www.youtube.com/watch?v=61CfUb9lBUI&t=420s) | 61CfUb9lBUI | 98 | 07:00 | 07:05 | That's they all come across, I think a little bit as overacting. |
| [07:05](https://www.youtube.com/watch?v=61CfUb9lBUI&t=425s) | 61CfUb9lBUI | 99 | 07:05 | 07:10 | Let me know in the comments, what you find to be the best prompts to get it to sound |
| [07:10](https://www.youtube.com/watch?v=61CfUb9lBUI&t=430s) | 61CfUb9lBUI | 100 | 07:10 | 07:15 | really good, but not sound like it's overacting at times, but it certainly was whispering softly. |
| [07:15](https://www.youtube.com/watch?v=61CfUb9lBUI&t=435s) | 61CfUb9lBUI | 101 | 07:15 | 07:20 | You could hear that in the way that it's going on there. Another one, laughing and giggling. |
| [07:21](https://www.youtube.com/watch?v=61CfUb9lBUI&t=441s) | 61CfUb9lBUI | 102 | 07:21 | 07:26 | Let's just take a listen to that. That's right. Gemini now has text to speech. |
| [07:28](https://www.youtube.com/watch?v=61CfUb9lBUI&t=448s) | 61CfUb9lBUI | 103 | 07:28 | 07:34 | So you can see that I didn't really need to signal the laughing and actually I don't get a lot of |
| [07:34](https://www.youtube.com/watch?v=61CfUb9lBUI&t=454s) | 61CfUb9lBUI | 104 | 07:34 | 07:39 | control over that laughing. So sometimes when I generated it, I would get laughing at the front |
| [07:39](https://www.youtube.com/watch?v=61CfUb9lBUI&t=459s) | 61CfUb9lBUI | 105 | 07:39 | 07:45 | and the end. Sometimes I would just get it at the end. You can still use the temperature for this |
| [07:45](https://www.youtube.com/watch?v=61CfUb9lBUI&t=465s) | 61CfUb9lBUI | 106 | 07:45 | 07:49 | and you can play around with it and stuff like that, but be aware it is a stochastic process, |
| [07:49](https://www.youtube.com/watch?v=61CfUb9lBUI&t=469s) | 61CfUb9lBUI | 107 | 07:49 | 07:55 | right? It's coming out of the Gemini model. Another one using the exact same voice is just, |
| [07:55](https://www.youtube.com/watch?v=61CfUb9lBUI&t=475s) | 61CfUb9lBUI | 108 | 07:55 | 08:00 | let's see. Okay. How does that same voice now sort of sound with something perhaps stern and more |
| [08:00](https://www.youtube.com/watch?v=61CfUb9lBUI&t=480s) | 61CfUb9lBUI | 109 | 08:00 | 08:10 | angry. No more excuses. You can now use Gemini TTS. Okay. So you can see, again, I kind of feel |
| [08:10](https://www.youtube.com/watch?v=61CfUb9lBUI&t=490s) | 61CfUb9lBUI | 110 | 08:10 | 08:16 | it's like a little bit overacting, but it's definitely taking the cues that I've given it |
| [08:16](https://www.youtube.com/watch?v=61CfUb9lBUI&t=496s) | 61CfUb9lBUI | 111 | 08:16 | 08:20 | there, the frunks. Now you can experiment with different ways of doing this. I find that the |
| [08:20](https://www.youtube.com/watch?v=61CfUb9lBUI&t=500s) | 61CfUb9lBUI | 112 | 08:20 | 08:26 | simplest way is just to put a colon there, but you could actually wrap these in quote marks and |
| [08:26](https://www.youtube.com/watch?v=61CfUb9lBUI&t=506s) | 61CfUb9lBUI | 113 | 08:26 | 08:30 | stuff like that as well. And then put your instructions in there as well. And I think |
| [08:30](https://www.youtube.com/watch?v=61CfUb9lBUI&t=510s) | 61CfUb9lBUI | 114 | 08:30 | 08:35 | you can do that sort of if you're doing sort of longer things in here. So if you wanted to make |
| [08:35](https://www.youtube.com/watch?v=61CfUb9lBUI&t=515s) | 61CfUb9lBUI | 115 | 08:35 | 08:41 | like an audio book reading kind of thing, you will still need to probably split it up into a certain |
| [08:41](https://www.youtube.com/watch?v=61CfUb9lBUI&t=521s) | 61CfUb9lBUI | 116 | 08:41 | 08:46 | number of paragraphs at a time, but you might be able to get away with it actually sort of taking |
| [08:46](https://www.youtube.com/watch?v=61CfUb9lBUI&t=526s) | 61CfUb9lBUI | 117 | 08:46 | 08:53 | some of this from the raw text and reading it in those sorts of ways. All right. So next up is the |
| [08:53](https://www.youtube.com/watch?v=61CfUb9lBUI&t=533s) | 61CfUb9lBUI | 118 | 08:53 | 09:00 | multi-speaker idea. And so this is really notebook LM, right? One of the things that people loved |
| [09:00](https://www.youtube.com/watch?v=61CfUb9lBUI&t=540s) | 61CfUb9lBUI | 119 | 09:00 | 09:05 | about Notebook LM, and I guess it's just over a year now that it was announced, was this idea of |
| [09:05](https://www.youtube.com/watch?v=61CfUb9lBUI&t=545s) | 61CfUb9lBUI | 120 | 09:05 | 09:09 | sort of putting a podcast sort of thing. And I think it really was only late last year that it |
| [09:09](https://www.youtube.com/watch?v=61CfUb9lBUI&t=549s) | 61CfUb9lBUI | 121 | 09:09 | 09:15 | actually came out publicly. The idea was that if you've got some kind of multi-speaker content, |
| [09:16](https://www.youtube.com/watch?v=61CfUb9lBUI&t=556s) | 61CfUb9lBUI | 122 | 09:16 | 09:22 | you really want something that's going to actually sound quite good going from one voice to the |
| [09:22](https://www.youtube.com/watch?v=61CfUb9lBUI&t=562s) | 61CfUb9lBUI | 123 | 09:22 | 09:27 | other. Now we looked at this with some of the open TTS systems that I looked at recently, |
| [09:27](https://www.youtube.com/watch?v=61CfUb9lBUI&t=567s) | 61CfUb9lBUI | 124 | 09:27 | 09:31 | But obviously the challenge with that one was that it kept speeding up, right? |
| [09:32](https://www.youtube.com/watch?v=61CfUb9lBUI&t=572s) | 61CfUb9lBUI | 125 | 09:32 | 09:36 | So while the Dyer model was really good at handling the multi-speaker thing, it perhaps |
| [09:36](https://www.youtube.com/watch?v=61CfUb9lBUI&t=576s) | 61CfUb9lBUI | 126 | 09:36 | 09:38 | still had parts of it that were not fully worked out. |
| [09:39](https://www.youtube.com/watch?v=61CfUb9lBUI&t=579s) | 61CfUb9lBUI | 127 | 09:39 | 09:43 | So here, what we're going to do is we want to generate a transcript. |
| [09:44](https://www.youtube.com/watch?v=61CfUb9lBUI&t=584s) | 61CfUb9lBUI | 128 | 09:44 | 09:49 | So you can see here, I've just got a simple call to the 2.0 flash model, basically saying |
| [09:49](https://www.youtube.com/watch?v=61CfUb9lBUI&t=589s) | 61CfUb9lBUI | 129 | 09:49 | 09:54 | generate a short transcript around 200 words that reads like it was taken from a podcast |
| [09:54](https://www.youtube.com/watch?v=61CfUb9lBUI&t=594s) | 61CfUb9lBUI | 130 | 09:54 | 09:56 | by an expert of bringing back extinct animals. |
| [09:56](https://www.youtube.com/watch?v=61CfUb9lBUI&t=596s) | 61CfUb9lBUI | 131 | 09:56 | 10:00 | Now that's going to be the character Jenny and the podcast host is going to be David. |
| [10:01](https://www.youtube.com/watch?v=61CfUb9lBUI&t=601s) | 61CfUb9lBUI | 132 | 10:01 | 10:04 | They're talking about Jenny's team bringing back the woolly mammoth. |
| [10:04](https://www.youtube.com/watch?v=61CfUb9lBUI&t=604s) | 61CfUb9lBUI | 133 | 10:04 | 10:08 | The presenters will occasionally interrupt each other with their passion. |
| [10:09](https://www.youtube.com/watch?v=61CfUb9lBUI&t=609s) | 61CfUb9lBUI | 134 | 10:09 | 10:14 | Now you can see that, sure enough, this generates out a nice formatted transcript where we can |
| [10:14](https://www.youtube.com/watch?v=61CfUb9lBUI&t=614s) | 61CfUb9lBUI | 135 | 10:14 | 10:16 | see like, okay, who's saying what. |
| [10:16](https://www.youtube.com/watch?v=61CfUb9lBUI&t=616s) | 61CfUb9lBUI | 136 | 10:16 | 10:21 | We can see that we start out with David, then going to Jenny, and we could customize this |
| [10:21](https://www.youtube.com/watch?v=61CfUb9lBUI&t=621s) | 61CfUb9lBUI | 137 | 10:21 | 10:22 | a lot more. |
| [10:22](https://www.youtube.com/watch?v=61CfUb9lBUI&t=622s) | 61CfUb9lBUI | 138 | 10:22 | 10:24 | This is a really sort of simple example. |
| [10:24](https://www.youtube.com/watch?v=61CfUb9lBUI&t=624s) | 61CfUb9lBUI | 139 | 10:24 | 10:32 | but obviously you could take in any sort of content or even do a google search and have it |
| [10:32](https://www.youtube.com/watch?v=61CfUb9lBUI&t=632s) | 61CfUb9lBUI | 140 | 10:32 | 10:38 | generate the podcast based on that google search so there's lots of ideas that you can do with this |
| [10:38](https://www.youtube.com/watch?v=61CfUb9lBUI&t=638s) | 61CfUb9lBUI | 141 | 10:38 | 10:44 | concept but once we've got something like this out we just pass it in now you'll see this is the |
| [10:44](https://www.youtube.com/watch?v=61CfUb9lBUI&t=644s) | 61CfUb9lBUI | 142 | 10:44 | 10:50 | same as what we were doing before the only thing now that's different in here is that we've got |
| [10:50](https://www.youtube.com/watch?v=61CfUb9lBUI&t=650s) | 61CfUb9lBUI | 143 | 10:50 | 10:56 | multi-speaker voice config. And so we're passing in the details for each speaker. So this is the |
| [10:56](https://www.youtube.com/watch?v=61CfUb9lBUI&t=656s) | 61CfUb9lBUI | 144 | 10:56 | 11:01 | speaker Jenny. She's going to use this voice. This is the speaker David. He's going to use this voice |
| [11:01](https://www.youtube.com/watch?v=61CfUb9lBUI&t=661s) | 61CfUb9lBUI | 145 | 11:01 | 11:06 | in here. Now we could change the voices. We could change those kinds of things. Obviously, like I |
| [11:06](https://www.youtube.com/watch?v=61CfUb9lBUI&t=666s) | 61CfUb9lBUI | 146 | 11:06 | 11:10 | talked about before, if you wanted to change the language, you could come in here and change that |
| [11:10](https://www.youtube.com/watch?v=61CfUb9lBUI&t=670s) | 61CfUb9lBUI | 147 | 11:10 | 11:15 | as well. We get the data out exactly the same way. We save it the exact same way as before. |
| [11:15](https://www.youtube.com/watch?v=61CfUb9lBUI&t=675s) | 61CfUb9lBUI | 148 | 11:15 | 11:17 | Now, if we come down and listen to this. |
| [11:45](https://www.youtube.com/watch?v=61CfUb9lBUI&t=705s) | 61CfUb9lBUI | 149 | 11:45 | 11:48 | And identifying key differences from modern elephants. |
| [11:49](https://www.youtube.com/watch?v=61CfUb9lBUI&t=709s) | 61CfUb9lBUI | 150 | 11:49 | 11:52 | Key differences that allow for, you know, surviving the ice age. |
| [11:53](https://www.youtube.com/watch?v=61CfUb9lBUI&t=713s) | 61CfUb9lBUI | 151 | 11:53 | 11:53 | Exactly. |
| [11:54](https://www.youtube.com/watch?v=61CfUb9lBUI&t=714s) | 61CfUb9lBUI | 152 | 11:54 | 11:58 | And with advancements in gene editing, we're working towards inserting... |
| [11:58](https://www.youtube.com/watch?v=61CfUb9lBUI&t=718s) | 61CfUb9lBUI | 153 | 11:58 | 12:00 | Okay, so you can listen to this and I'll give you the notebook. |
| [12:00](https://www.youtube.com/watch?v=61CfUb9lBUI&t=720s) | 61CfUb9lBUI | 154 | 12:00 | 12:03 | Of course, as always, you can go in and listen to the full thing. |
| [12:04](https://www.youtube.com/watch?v=61CfUb9lBUI&t=724s) | 61CfUb9lBUI | 155 | 12:04 | 12:05 | And you can play around with it. |
| [12:05](https://www.youtube.com/watch?v=61CfUb9lBUI&t=725s) | 61CfUb9lBUI | 156 | 12:05 | 12:11 | So you'll notice in here, I don't have a lot of guidance of how to actually speak each |
| [12:11](https://www.youtube.com/watch?v=61CfUb9lBUI&t=731s) | 61CfUb9lBUI | 157 | 12:11 | 12:12 | of the lines and stuff like that. |
| [12:12](https://www.youtube.com/watch?v=61CfUb9lBUI&t=732s) | 61CfUb9lBUI | 158 | 12:12 | 12:14 | You certainly can do that. |
| [12:14](https://www.youtube.com/watch?v=61CfUb9lBUI&t=734s) | 61CfUb9lBUI | 159 | 12:14 | 12:32 | You can certainly put that into your transcript. Before when I was playing around with it for sort of like an AI podcast, I had it doing it. Again, I kind of find that it's a little bit overacting, but I also find that a bit with the Notebook LM. So I guess it's just kind of the way these things are currently working. |
| [12:32](https://www.youtube.com/watch?v=61CfUb9lBUI&t=752s) | 61CfUb9lBUI | 160 | 12:32 | 12:37 | But it is pretty amazing that you can just very quickly pick a few different presenters, |
| [12:37](https://www.youtube.com/watch?v=61CfUb9lBUI&t=757s) | 61CfUb9lBUI | 161 | 12:37 | 12:43 | stick them in here, have Gemini generate the conversation based on some sort of context |
| [12:43](https://www.youtube.com/watch?v=61CfUb9lBUI&t=763s) | 61CfUb9lBUI | 162 | 12:43 | 12:48 | that you've got, and then convert it out, save it, and you've got your multi-speaker |
| [12:48](https://www.youtube.com/watch?v=61CfUb9lBUI&t=768s) | 61CfUb9lBUI | 163 | 12:48 | 12:50 | podcast going on here. |
| [12:50](https://www.youtube.com/watch?v=61CfUb9lBUI&t=770s) | 61CfUb9lBUI | 164 | 12:50 | 12:53 | So have a play with the notebook, see what you can do with it. |
| [12:53](https://www.youtube.com/watch?v=61CfUb9lBUI&t=773s) | 61CfUb9lBUI | 165 | 12:53 | 12:58 | I'm really curious to see what people can get in relation to any sort of effects on |
| [12:58](https://www.youtube.com/watch?v=61CfUb9lBUI&t=778s) | 61CfUb9lBUI | 166 | 12:58 | 13:00 | the voices and stuff like that. |
| [13:00](https://www.youtube.com/watch?v=61CfUb9lBUI&t=780s) | 61CfUb9lBUI | 167 | 13:00 | 13:06 | certainly google sort of lock this down for dialogue and for speech but you can get some |
| [13:06](https://www.youtube.com/watch?v=61CfUb9lBUI&t=786s) | 61CfUb9lBUI | 168 | 13:06 | 13:12 | really interesting effects just by guiding the voice to speak in a particular way etc |
| [13:12](https://www.youtube.com/watch?v=61CfUb9lBUI&t=792s) | 61CfUb9lBUI | 169 | 13:12 | 13:16 | so let me know in the comments what you think at the time of recording i don't know anything about |
| [13:16](https://www.youtube.com/watch?v=61CfUb9lBUI&t=796s) | 61CfUb9lBUI | 170 | 13:16 | 13:20 | the pricing and stuff like this so i'm not sure whether this is going to be quite cheap and |
| [13:20](https://www.youtube.com/watch?v=61CfUb9lBUI&t=800s) | 61CfUb9lBUI | 171 | 13:20 | 13:25 | effective for doing this kind of thing or is the cost going to make it prohibitive and we're still |
| [13:25](https://www.youtube.com/watch?v=61CfUb9lBUI&t=805s) | 61CfUb9lBUI | 172 | 13:25 | 13:29 | going to want those open models now of course those open models like kokoro etc are still really |
| [13:29](https://www.youtube.com/watch?v=61CfUb9lBUI&t=809s) | 61CfUb9lBUI | 173 | 13:29 | 13:34 | useful if we want to do anything sort of real time where we're not actually pinging a cloud, |
| [13:34](https://www.youtube.com/watch?v=61CfUb9lBUI&t=814s) | 61CfUb9lBUI | 174 | 13:34 | 13:39 | but we're running it something locally. That's going to have a massive advantage speed-wise |
| [13:39](https://www.youtube.com/watch?v=61CfUb9lBUI&t=819s) | 61CfUb9lBUI | 175 | 13:39 | 13:44 | over this where we're calling out to the cloud, et cetera. Anyway, as always, if you found the |
| [13:44](https://www.youtube.com/watch?v=61CfUb9lBUI&t=824s) | 61CfUb9lBUI | 176 | 13:44 | 13:48 | video useful, please click like and subscribe, and I will talk to you in the next video. Bye for now. |
