Title: GitHub - danielmiessler/fabric: fabric is an open-source framework for augmenting humans using AI. It provides a modular framework for solving specific problems using a crowdsourced set of AI prompts that can be used anywhere.

URL Source: https://github.com/danielmiessler/fabric

Markdown Content:
[![Image 42: fabriclogo](https://github.com/danielmiessler/fabric/raw/main/images/fabric-logo-gif.gif)](https://github.com/danielmiessler/fabric/blob/main/images/fabric-logo-gif.gif)

`fabric`
--------

[](https://github.com/danielmiessler/fabric#fabric)

[![Image 43: Static Badge](https://camo.githubusercontent.com/f022dc8d1303fe26ee78cd88e60920ef2d1baf96c629d782e8117faa8899e319/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f6d697373696f6e2d68756d616e5f666c6f7572697368696e675f7669615f41495f6175676d656e746174696f6e2d707572706c65)](https://camo.githubusercontent.com/f022dc8d1303fe26ee78cd88e60920ef2d1baf96c629d782e8117faa8899e319/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f6d697373696f6e2d68756d616e5f666c6f7572697368696e675f7669615f41495f6175676d656e746174696f6e2d707572706c65)  
[![Image 44: GitHub top language](https://camo.githubusercontent.com/5ebdbd74bb4ac3d78b0970aad6fde0e7ab273c96e28180744b16fc28a1ef109c/68747470733a2f2f696d672e736869656c64732e696f2f6769746875622f6c616e6775616765732f746f702f64616e69656c6d696573736c65722f666162726963)](https://camo.githubusercontent.com/5ebdbd74bb4ac3d78b0970aad6fde0e7ab273c96e28180744b16fc28a1ef109c/68747470733a2f2f696d672e736869656c64732e696f2f6769746875622f6c616e6775616765732f746f702f64616e69656c6d696573736c65722f666162726963) [![Image 45: GitHub last commit](https://camo.githubusercontent.com/a5f1f93e3ce4592ed5c1ceec7e552729cc451a843598c6f76e85c4610863fc4d/68747470733a2f2f696d672e736869656c64732e696f2f6769746875622f6c6173742d636f6d6d69742f64616e69656c6d696573736c65722f666162726963)](https://camo.githubusercontent.com/a5f1f93e3ce4592ed5c1ceec7e552729cc451a843598c6f76e85c4610863fc4d/68747470733a2f2f696d672e736869656c64732e696f2f6769746875622f6c6173742d636f6d6d69742f64616e69656c6d696573736c65722f666162726963) [![Image 46: License: MIT](https://camo.githubusercontent.com/28f4d479bf0a9b033b3a3b95ab2adc343da448a025b01aefdc0fbc7f0e169eb8/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f4c6963656e73652d4d49542d677265656e2e737667)](https://opensource.org/licenses/MIT)

#### `fabric` is an open-source framework for augmenting humans using AI.

[](https://github.com/danielmiessler/fabric#fabric-is-an-open-source-framework-for-augmenting-humans-using-ai)

[Updates](https://github.com/danielmiessler/fabric#updates) • [What and Why](https://github.com/danielmiessler/fabric#whatandwhy) • [Philosophy](https://github.com/danielmiessler/fabric#philosophy) • [Installation](https://github.com/danielmiessler/fabric#Installation) • [Usage](https://github.com/danielmiessler/fabric#Usage) • [Examples](https://github.com/danielmiessler/fabric#examples) • [Just Use the Patterns](https://github.com/danielmiessler/fabric#just-use-the-patterns) • [Custom Patterns](https://github.com/danielmiessler/fabric#custom-patterns) • [Helper Apps](https://github.com/danielmiessler/fabric#helper-apps) • [Meta](https://github.com/danielmiessler/fabric#meta)

[![Image 47: Screenshot of fabric](https://github.com/danielmiessler/fabric/raw/main/images/fabric-summarize.png)](https://github.com/danielmiessler/fabric/blob/main/images/fabric-summarize.png)

Navigation
----------

[](https://github.com/danielmiessler/fabric#navigation)

*   [`fabric`](https://github.com/danielmiessler/fabric#fabric)
    *   [Navigation](https://github.com/danielmiessler/fabric#navigation)
    *   [Updates](https://github.com/danielmiessler/fabric#updates)
    *   [Intro videos](https://github.com/danielmiessler/fabric#intro-videos)
    *   [What and why](https://github.com/danielmiessler/fabric#what-and-why)
    *   [Philosophy](https://github.com/danielmiessler/fabric#philosophy)
        *   [Breaking problems into components](https://github.com/danielmiessler/fabric#breaking-problems-into-components)
        *   [Too many prompts](https://github.com/danielmiessler/fabric#too-many-prompts)
    *   [Installation](https://github.com/danielmiessler/fabric#installation)
        *   [Get Latest Release Binaries](https://github.com/danielmiessler/fabric#get-latest-release-binaries)
        *   [From Source](https://github.com/danielmiessler/fabric#from-source)
        *   [Environment Variables](https://github.com/danielmiessler/fabric#environment-variables)
        *   [Setup](https://github.com/danielmiessler/fabric#setup)
        *   [Add aliases for all patterns](https://github.com/danielmiessler/fabric#add-aliases-for-all-patterns)
            *   [Save your files in markdown using aliases](https://github.com/danielmiessler/fabric#save-your-files-in-markdown-using-aliases)
        *   [Migration](https://github.com/danielmiessler/fabric#migration)
        *   [Upgrading](https://github.com/danielmiessler/fabric#upgrading)
    *   [Usage](https://github.com/danielmiessler/fabric#usage)
    *   [Our approach to prompting](https://github.com/danielmiessler/fabric#our-approach-to-prompting)
    *   [Examples](https://github.com/danielmiessler/fabric#examples)
    *   [Just use the Patterns](https://github.com/danielmiessler/fabric#just-use-the-patterns)
    *   [Custom Patterns](https://github.com/danielmiessler/fabric#custom-patterns)
    *   [Helper Apps](https://github.com/danielmiessler/fabric#helper-apps)
        *   [`to_pdf`](https://github.com/danielmiessler/fabric#to_pdf)
        *   [`to_pdf` Installation](https://github.com/danielmiessler/fabric#to_pdf-installation)
    *   [pbpaste](https://github.com/danielmiessler/fabric#pbpaste)
    *   [Meta](https://github.com/danielmiessler/fabric#meta)
        *   [Primary contributors](https://github.com/danielmiessler/fabric#primary-contributors)

Updates
-------

[](https://github.com/danielmiessler/fabric#updates)

Note

November 8, 2024

*   **Multimodal Support**: You can now us `-a` (attachment) for Multimodal submissions to OpenAI models that support it. Example: `fabric -a https://path/to/image "Give me a description of this image."`

What and why
------------

[](https://github.com/danielmiessler/fabric#what-and-why)

Since the start of 2023 and GenAI we've seen a massive number of AI applications for accomplishing tasks. It's powerful, but _it's not easy to integrate this functionality into our lives._

#### In other words, AI doesn't have a capabilities problem—it has an _integration_ problem.

[](https://github.com/danielmiessler/fabric#in-other-words-ai-doesnt-have-a-capabilities-problemit-has-an-integration-problem)

Fabric was created to address this by enabling everyone to granularly apply AI to everyday challenges.

Intro videos
------------

[](https://github.com/danielmiessler/fabric#intro-videos)

Keep in mind that many of these were recorded when Fabric was Python-based, so remember to use the current [install instructions](https://github.com/danielmiessler/fabric#Installation) below.

*   [Network Chuck](https://www.youtube.com/watch?v=UbDyjIIGaxQ)
*   [David Bombal](https://www.youtube.com/watch?v=vF-MQmVxnCs)
*   [My Own Intro to the Tool](https://www.youtube.com/watch?v=wPEyyigh10g)
*   [More Fabric YouTube Videos](https://www.youtube.com/results?search_query=fabric+ai)

Philosophy
----------

[](https://github.com/danielmiessler/fabric#philosophy)

> AI isn't a thing; it's a _magnifier_ of a thing. And that thing is **human creativity**.

We believe the purpose of technology is to help humans flourish, so when we talk about AI we start with the **human** problems we want to solve.

### Breaking problems into components

[](https://github.com/danielmiessler/fabric#breaking-problems-into-components)

Our approach is to break problems into individual pieces (see below) and then apply AI to them one at a time. See below for some examples.

[![Image 48: augmented_challenges](https://private-user-images.githubusercontent.com/50654/302028537-31997394-85a9-40c2-879b-b347e4701f06.png?jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3MzI1ODc2MzYsIm5iZiI6MTczMjU4NzMzNiwicGF0aCI6Ii81MDY1NC8zMDIwMjg1MzctMzE5OTczOTQtODVhOS00MGMyLTg3OWItYjM0N2U0NzAxZjA2LnBuZz9YLUFtei1BbGdvcml0aG09QVdTNC1ITUFDLVNIQTI1NiZYLUFtei1DcmVkZW50aWFsPUFLSUFWQ09EWUxTQTUzUFFLNFpBJTJGMjAyNDExMjYlMkZ1cy1lYXN0LTElMkZzMyUyRmF3czRfcmVxdWVzdCZYLUFtei1EYXRlPTIwMjQxMTI2VDAyMTUzNlomWC1BbXotRXhwaXJlcz0zMDAmWC1BbXotU2lnbmF0dXJlPWJlNTliMTNiNTM5MmFmNTYyYTRmYTU5YjYwNzNkNTIzOWYwOTFhMjk5MGM2ZTk5MTM0NGZlY2FjNzM5MWJiZTgmWC1BbXotU2lnbmVkSGVhZGVycz1ob3N0In0.EotZ63SR8pkaWOaqfKCSgoyKIvftsPAt2E2n_iuh6UE)](https://private-user-images.githubusercontent.com/50654/302028537-31997394-85a9-40c2-879b-b347e4701f06.png?jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3MzI1ODc2MzYsIm5iZiI6MTczMjU4NzMzNiwicGF0aCI6Ii81MDY1NC8zMDIwMjg1MzctMzE5OTczOTQtODVhOS00MGMyLTg3OWItYjM0N2U0NzAxZjA2LnBuZz9YLUFtei1BbGdvcml0aG09QVdTNC1ITUFDLVNIQTI1NiZYLUFtei1DcmVkZW50aWFsPUFLSUFWQ09EWUxTQTUzUFFLNFpBJTJGMjAyNDExMjYlMkZ1cy1lYXN0LTElMkZzMyUyRmF3czRfcmVxdWVzdCZYLUFtei1EYXRlPTIwMjQxMTI2VDAyMTUzNlomWC1BbXotRXhwaXJlcz0zMDAmWC1BbXotU2lnbmF0dXJlPWJlNTliMTNiNTM5MmFmNTYyYTRmYTU5YjYwNzNkNTIzOWYwOTFhMjk5MGM2ZTk5MTM0NGZlY2FjNzM5MWJiZTgmWC1BbXotU2lnbmVkSGVhZGVycz1ob3N0In0.EotZ63SR8pkaWOaqfKCSgoyKIvftsPAt2E2n_iuh6UE)

### Too many prompts

[](https://github.com/danielmiessler/fabric#too-many-prompts)

Prompts are good for this, but the biggest challenge I faced in 2023——which still exists today—is **the sheer number of AI prompts out there**. We all have prompts that are useful, but it's hard to discover new ones, know if they are good or not, _and manage different versions of the ones we like_.

One of `fabric`'s primary features is helping people collect and integrate prompts, which we call _Patterns_, into various parts of their lives.

Fabric has Patterns for all sorts of life and work activities, including:

*   Extracting the most interesting parts of YouTube videos and podcasts
*   Writing an essay in your own voice with just an idea as an input
*   Summarizing opaque academic papers
*   Creating perfectly matched AI art prompts for a piece of writing
*   Rating the quality of content to see if you want to read/watch the whole thing
*   Getting summaries of long, boring content
*   Explaining code to you
*   Turning bad documentation into usable documentation
*   Creating social media posts from any content input
*   And a million more…

Installation
------------

[](https://github.com/danielmiessler/fabric#installation)

To install Fabric, you can use the latest release binaries or install it from the source.

### Get Latest Release Binaries

[](https://github.com/danielmiessler/fabric#get-latest-release-binaries)

# Windows:
curl -L https://github.com/danielmiessler/fabric/releases/latest/download/fabric-windows-amd64.exe \> fabric.exe && fabric.exe --version

# MacOS (arm64):
curl -L https://github.com/danielmiessler/fabric/releases/latest/download/fabric-darwin-arm64 \> fabric && chmod +x fabric && ./fabric --version

# MacOS (amd64):
curl -L https://github.com/danielmiessler/fabric/releases/latest/download/fabric-darwin-amd64 \> fabric && chmod +x fabric && ./fabric --version

# Linux (amd64):
curl -L https://github.com/danielmiessler/fabric/releases/latest/download/fabric-linux-amd64 \> fabric && chmod +x fabric && ./fabric --version

# Linux (arm64):
curl -L https://github.com/danielmiessler/fabric/releases/latest/download/fabric-linux-arm64 \> fabric && chmod +x fabric && ./fabric --version

### From Source

[](https://github.com/danielmiessler/fabric#from-source)

To install Fabric, [make sure Go is installed](https://go.dev/doc/install), and then run the following command.

# Install Fabric directly from the repo
go install github.com/danielmiessler/fabric@latest

### Environment Variables

[](https://github.com/danielmiessler/fabric#environment-variables)

You may need to set some environment variables in your `~/.bashrc` on linux or `~/.zshrc` file on mac to be able to run the `fabric` command. Here is an example of what you can add:

For Intel based macs or linux

# Golang environment variables
export GOROOT=/usr/local/go
export GOPATH=$HOME/go

# Update PATH to include GOPATH and GOROOT binaries
export PATH=$GOPATH/bin:$GOROOT/bin:$HOME/.local/bin:$PATH

for Apple Silicon based macs

# Golang environment variables
export GOROOT=$(brew --prefix go)/libexec
export GOPATH=$HOME/go
export PATH=$GOPATH/bin:$GOROOT/bin:$HOME/.local/bin:$PATH

### Setup

[](https://github.com/danielmiessler/fabric#setup)

Now run the following command

# Run the setup to set up your directories and keys
fabric --setup

If everything works you are good to go.

### Add aliases for all patterns

[](https://github.com/danielmiessler/fabric#add-aliases-for-all-patterns)

In order to add aliases for all your patterns and use them directly as commands ie. `summarize` instead of `fabric --pattern summarize` You can add the following to your `.zshrc` or `.bashrc` file.

# Loop through all files in the ~/.config/fabric/patterns directory
for pattern\_file in $HOME/.config/fabric/patterns/\*; do
    # Get the base name of the file (i.e., remove the directory path)
    pattern\_name=$(basename "$pattern\_file")
    
    # Create an alias in the form: alias pattern\_name="fabric --pattern pattern\_name"
    alias\_command="alias $pattern\_name\='fabric --pattern $pattern\_name'"
    
    # Evaluate the alias command to add it to the current shell
    eval "$alias\_command"
done

yt() {
    local video\_link="$1"
    fabric -y "$video\_link" --transcript
}

This also creates a `yt` alias that allows you to use `yt https://www.youtube.com/watch?v=4b0iet22VIk` to get your transcripts.

#### Save your files in markdown using aliases

[](https://github.com/danielmiessler/fabric#save-your-files-in-markdown-using-aliases)

If in addition to the above aliases you would like to have the option to save the output to your favourite markdown note vault like Obsidian then instead of the above add the following to your `.zshrc` or `.bashrc` file:

# Define the base directory for Obsidian notes
obsidian\_base="/path/to/obsidian"

# Loop through all files in the ~/.config/fabric/patterns directory
for pattern\_file in ~/.config/fabric/patterns/\*; do
    # Get the base name of the file (i.e., remove the directory path)
    pattern\_name=$(basename "$pattern\_file")

    # Unalias any existing alias with the same name
    unalias "$pattern\_name" 2\>/dev/null

    # Define a function dynamically for each pattern
    eval "
    $pattern\_name() {
        local title=\\$1
        local date\_stamp=\\$(date +'%Y-%m-%d')
        local output\_path=\\"\\$obsidian\_base/\\${date\_stamp}-\\${title}.md\\"
        # Check if a title was provided
        if \[ -n \\"\\$title\\" \]; then
            # If a title is provided, use the output path
            fabric --pattern \\"$pattern\_name\\" -o \\"\\$output\_path\\"
        else
            # If no title is provided, use --stream
            fabric --pattern \\"$pattern\_name\\" --stream
        fi
    }
    "
done

yt() {
    local video\_link="$1"
    fabric -y "$video\_link" --transcript
}

This will allow you to use the patterns as aliases like in the above for example `summarize` instead of `fabric --pattern summarize --stream`, however if you pass in an extra argument like this `summarize "my_article_title"` your output will be saved in the destination that you set in `obsidian_base="/path/to/obsidian"` in the following format `YYYY-MM-DD-my_article_title.md` where the date gets autogenerated for you. You can tweak the date format by tweaking the `date_stamp` format.

### Migration

[](https://github.com/danielmiessler/fabric#migration)

If you have the Legacy (Python) version installed and want to migrate to the Go version, here's how you do it. It's basically two steps: 1) uninstall the Python version, and 2) install the Go version.

# Uninstall Legacy Fabric
pipx uninstall fabric

# Clear any old Fabric aliases
(check your .bashrc, .zshrc, etc.)
# Install the Go version
go install github.com/danielmiessler/fabric@latest
# Run setup for the new version. Important because things have changed
fabric --setup

Then [set your environmental variables](https://github.com/danielmiessler/fabric#environmental-variables) as shown above.

### Upgrading

[](https://github.com/danielmiessler/fabric#upgrading)

The great thing about Go is that it's super easy to upgrade. Just run the same command you used to install it in the first place and you'll always get the latest version.

go install github.com/danielmiessler/fabric@latest

Usage
-----

[](https://github.com/danielmiessler/fabric#usage)

Once you have it all set up, here's how to use it.

Usage:
  fabric \[OPTIONS\]

Application Options:
  -p, --pattern=             Choose a pattern from the available patterns
  -v, --variable=            Values for pattern variables, e.g. -v=#role:expert -v=#points:30"
  -C, --context=             Choose a context from the available contexts
      --session=             Choose a session from the available sessions
  -a, --attachment=          Attachment path or URL (e.g. for OpenAI image recognition messages)
  -S, --setup                Run setup for all reconfigurable parts of fabric
  -t, --temperature=         Set temperature (default: 0.7)
  -T, --topp=                Set top P (default: 0.9)
  -s, --stream               Stream
  -P, --presencepenalty=     Set presence penalty (default: 0.0)
  -r, --raw                  Use the defaults of the model without sending chat options (like temperature etc.) and use the user role instead of the system role for patterns.
  -F, --frequencypenalty=    Set frequency penalty (default: 0.0)
  -l, --listpatterns         List all patterns
  -L, --listmodels           List all available models
  -x, --listcontexts         List all contexts
  -X, --listsessions         List all sessions
  -U, --updatepatterns       Update patterns
  -c, --copy                 Copy to clipboard
  -m, --model=               Choose model
  -o, --output=              Output to file
      --output-session       Output the entire session (also a temporary one) to the output file
  -n, --latest=              Number of latest patterns to list (default: 0)
  -d, --changeDefaultModel   Change default model
  -y, --youtube=             YouTube video "URL" to grab transcript, comments from it and send to chat
      --transcript           Grab transcript from YouTube video and send to chat (it used per default).
      --comments             Grab comments from YouTube video and send to chat
  -g, --language=            Specify the Language Code for the chat, e.g. -g=en -g=zh
  -u, --scrape\_url=          Scrape website URL to markdown using Jina AI
  -q, --scrape\_question=     Search question using Jina AI
  -e, --seed=                Seed to be used for LMM generation
  -w, --wipecontext=         Wipe context
  -W, --wipesession=         Wipe session
      --printcontext=        Print context
      --printsession=        Print session
      --readability          Convert HTML input into a clean, readable view
      --dry-run              Show what would be sent to the model without actually sending it
      --version              Print current version

Help Options:
  -h, --help                 Show this help message

Our approach to prompting
-------------------------

[](https://github.com/danielmiessler/fabric#our-approach-to-prompting)

Fabric _Patterns_ are different than most prompts you'll see.

*   **First, we use `Markdown` to help ensure maximum readability and editability**. This not only helps the creator make a good one, but also anyone who wants to deeply understand what it does. _Importantly, this also includes the AI you're sending it to!_

Here's an example of a Fabric Pattern.

https://github.com/danielmiessler/fabric/blob/main/patterns/extract\_wisdom/system.md

[![Image 49: pattern-example](https://private-user-images.githubusercontent.com/50654/302031520-b910c551-9263-405f-9735-71ca69bbab6d.png?jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3MzI1ODc2MzYsIm5iZiI6MTczMjU4NzMzNiwicGF0aCI6Ii81MDY1NC8zMDIwMzE1MjAtYjkxMGM1NTEtOTI2My00MDVmLTk3MzUtNzFjYTY5YmJhYjZkLnBuZz9YLUFtei1BbGdvcml0aG09QVdTNC1ITUFDLVNIQTI1NiZYLUFtei1DcmVkZW50aWFsPUFLSUFWQ09EWUxTQTUzUFFLNFpBJTJGMjAyNDExMjYlMkZ1cy1lYXN0LTElMkZzMyUyRmF3czRfcmVxdWVzdCZYLUFtei1EYXRlPTIwMjQxMTI2VDAyMTUzNlomWC1BbXotRXhwaXJlcz0zMDAmWC1BbXotU2lnbmF0dXJlPTU4NTFiNDRjMWE1M2Y2NThjMDM0NWZkZmI3NTU1MDY5OTQ3MTg3MDFkZDM0MjYwODA0NjFmYjQ0MzhhNGZjYmEmWC1BbXotU2lnbmVkSGVhZGVycz1ob3N0In0.Q6gRLIkA2WmA-7xK8RuKJ9AXH8vgm_aZR6LviZcyYBY)](https://private-user-images.githubusercontent.com/50654/302031520-b910c551-9263-405f-9735-71ca69bbab6d.png?jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3MzI1ODc2MzYsIm5iZiI6MTczMjU4NzMzNiwicGF0aCI6Ii81MDY1NC8zMDIwMzE1MjAtYjkxMGM1NTEtOTI2My00MDVmLTk3MzUtNzFjYTY5YmJhYjZkLnBuZz9YLUFtei1BbGdvcml0aG09QVdTNC1ITUFDLVNIQTI1NiZYLUFtei1DcmVkZW50aWFsPUFLSUFWQ09EWUxTQTUzUFFLNFpBJTJGMjAyNDExMjYlMkZ1cy1lYXN0LTElMkZzMyUyRmF3czRfcmVxdWVzdCZYLUFtei1EYXRlPTIwMjQxMTI2VDAyMTUzNlomWC1BbXotRXhwaXJlcz0zMDAmWC1BbXotU2lnbmF0dXJlPTU4NTFiNDRjMWE1M2Y2NThjMDM0NWZkZmI3NTU1MDY5OTQ3MTg3MDFkZDM0MjYwODA0NjFmYjQ0MzhhNGZjYmEmWC1BbXotU2lnbmVkSGVhZGVycz1ob3N0In0.Q6gRLIkA2WmA-7xK8RuKJ9AXH8vgm_aZR6LviZcyYBY)

*   **Next, we are extremely clear in our instructions**, and we use the Markdown structure to emphasize what we want the AI to do, and in what order.
    
*   **And finally, we tend to use the System section of the prompt almost exclusively**. In over a year of being heads-down with this stuff, we've just seen more efficacy from doing that. If that changes, or we're shown data that says otherwise, we will adjust.
    

Examples
--------

[](https://github.com/danielmiessler/fabric#examples)

> The following examples use the macOS `pbpaste` to paste from the clipboard. See the [pbpaste](https://github.com/danielmiessler/fabric#pbpaste) section below for Windows and Linux alternatives.

Now let's look at some things you can do with Fabric.

1.  Run the `summarize` Pattern based on input from `stdin`. In this case, the body of an article.

pbpaste | fabric --pattern summarize

2.  Run the `analyze_claims` Pattern with the `--stream` option to get immediate and streaming results.

pbpaste | fabric --stream --pattern analyze\_claims

3.  Run the `extract_wisdom` Pattern with the `--stream` option to get immediate and streaming results from any Youtube video (much like in the original introduction video).

fabric -y "https://youtube.com/watch?v=uXs-zPc63kM" --stream --pattern extract\_wisdom

4.  Create patterns- you must create a .md file with the pattern and save it to ~/.config/fabric/patterns/\[yourpatternname\].

Just use the Patterns
---------------------

[](https://github.com/danielmiessler/fabric#just-use-the-patterns)

[![Image 50: fabric-patterns-screenshot](https://private-user-images.githubusercontent.com/50654/301807224-9186a044-652b-4673-89f7-71cf066f32d8.png?jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3MzI1ODc2MzYsIm5iZiI6MTczMjU4NzMzNiwicGF0aCI6Ii81MDY1NC8zMDE4MDcyMjQtOTE4NmEwNDQtNjUyYi00NjczLTg5ZjctNzFjZjA2NmYzMmQ4LnBuZz9YLUFtei1BbGdvcml0aG09QVdTNC1ITUFDLVNIQTI1NiZYLUFtei1DcmVkZW50aWFsPUFLSUFWQ09EWUxTQTUzUFFLNFpBJTJGMjAyNDExMjYlMkZ1cy1lYXN0LTElMkZzMyUyRmF3czRfcmVxdWVzdCZYLUFtei1EYXRlPTIwMjQxMTI2VDAyMTUzNlomWC1BbXotRXhwaXJlcz0zMDAmWC1BbXotU2lnbmF0dXJlPTA4NjhiMjMwN2VjOWNmMjhlOWYwYzVjZjViNGFkMTk3MDk3YzY1YTVmMWFhNjBhNDVjMmFiN2E0MjgyNDkxMDgmWC1BbXotU2lnbmVkSGVhZGVycz1ob3N0In0.nj-LE27h6jUnhltfQRw5DhPR9bXirT8Ea06ssFVXQnI)](https://private-user-images.githubusercontent.com/50654/301807224-9186a044-652b-4673-89f7-71cf066f32d8.png?jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3MzI1ODc2MzYsIm5iZiI6MTczMjU4NzMzNiwicGF0aCI6Ii81MDY1NC8zMDE4MDcyMjQtOTE4NmEwNDQtNjUyYi00NjczLTg5ZjctNzFjZjA2NmYzMmQ4LnBuZz9YLUFtei1BbGdvcml0aG09QVdTNC1ITUFDLVNIQTI1NiZYLUFtei1DcmVkZW50aWFsPUFLSUFWQ09EWUxTQTUzUFFLNFpBJTJGMjAyNDExMjYlMkZ1cy1lYXN0LTElMkZzMyUyRmF3czRfcmVxdWVzdCZYLUFtei1EYXRlPTIwMjQxMTI2VDAyMTUzNlomWC1BbXotRXhwaXJlcz0zMDAmWC1BbXotU2lnbmF0dXJlPTA4NjhiMjMwN2VjOWNmMjhlOWYwYzVjZjViNGFkMTk3MDk3YzY1YTVmMWFhNjBhNDVjMmFiN2E0MjgyNDkxMDgmWC1BbXotU2lnbmVkSGVhZGVycz1ob3N0In0.nj-LE27h6jUnhltfQRw5DhPR9bXirT8Ea06ssFVXQnI)If you're not looking to do anything fancy, and you just want a lot of great prompts, you can navigate to the [`/patterns`](https://github.com/danielmiessler/fabric/tree/main/patterns) directory and start exploring!

We hope that if you used nothing else from Fabric, the Patterns by themselves will make the project useful.

You can use any of the Patterns you see there in any AI application that you have, whether that's ChatGPT or some other app or website. Our plan and prediction is that people will soon be sharing many more than those we've published, and they will be way better than ours.

The wisdom of crowds for the win.

Custom Patterns
---------------

[](https://github.com/danielmiessler/fabric#custom-patterns)

You may want to use Fabric to create your own custom Patterns—but not share them with others. No problem!

Just make a directory in `~/.config/custompatterns/` (or wherever) and put your `.md` files in there.

When you're ready to use them, copy them into:

```
~/.config/fabric/patterns/
```

You can then use them like any other Patterns, but they won't be public unless you explicitly submit them as Pull Requests to the Fabric project. So don't worry—they're private to you.

This feature works with all openai and ollama models but does NOT work with claude. You can specify your model with the -m flag

Helper Apps
-----------

[](https://github.com/danielmiessler/fabric#helper-apps)

Fabric also makes use of some core helper apps (tools) to make it easier to integrate with your various workflows. Here are some examples:

### `to_pdf`

[](https://github.com/danielmiessler/fabric#to_pdf)

`to_pdf` is a helper command that converts LaTeX files to PDF format. You can use it like this:

This will create a PDF file from the input LaTeX file in the same directory.

You can also use it with stdin which works perfectly with the `write_latex` pattern:

echo "ai security primer" | fabric --pattern write\_latex | to\_pdf

This will create a PDF file named `output.pdf` in the current directory.

### `to_pdf` Installation

[](https://github.com/danielmiessler/fabric#to_pdf-installation)

To install `to_pdf`, install it the same way as you install Fabric, just with a different repo name.

go install github.com/danielmiessler/fabric/plugins/tools/to\_pdf@latest

Make sure you have a LaTeX distribution (like TeX Live or MiKTeX) installed on your system, as `to_pdf` requires `pdflatex` to be available in your system's PATH.

pbpaste
-------

[](https://github.com/danielmiessler/fabric#pbpaste)

The [examples](https://github.com/danielmiessler/fabric#examples) use the macOS program `pbpaste` to paste content from the clipboard to pipe into `fabric` as the input. `pbpaste` is not available on Windows or Linux, but there are alternatives.

On Windows, you can use the PowerShell command `Get-Clipboard` from a PowerShell command prompt. If you like, you can also alias it to `pbpaste`. If you are using classic PowerShell, edit the file `~\Documents\WindowsPowerShell\.profile.ps1`, or if you are using PowerShell Core, edit `~\Documents\PowerShell\.profile.ps1` and add the alias,

Set-Alias pbpaste Get-Clipboard

On Linux, you can use `xclip -selection clipboard -o` to paste from the clipboard. You will likely need to install `xclip` with your package manager. For Debian based systems including Ubuntu,

sudo apt update
sudo apt install xclip -y

You can also create an alias by editing `~/.bashrc` or `~/.zshrc` and adding the alias,

alias pbpaste='xclip -selection clipboard -o'

Meta
----

[](https://github.com/danielmiessler/fabric#meta)

Note

Special thanks to the following people for their inspiration and contributions!

*   _Jonathan Dunn_ for being the absolute MVP dev on the project, including spearheading the new Go version, as well as the GUI! All this while also being a full-time medical doctor!
*   _Caleb Sima_ for pushing me over the edge of whether to make this a public project or not.
*   _Eugen Eisler_ and _Frederick Ros_ for their invaluable contributions to the Go version
*   _Joel Parish_ for super useful input on the project's Github directory structure..
*   _Joseph Thacker_ for the idea of a `-c` context flag that adds pre-created context in the `./config/fabric/` directory to all Pattern queries.
*   _Jason Haddix_ for the idea of a stitch (chained Pattern) to filter content using a local model before sending on to a cloud model, i.e., cleaning customer data using `llama2` before sending on to `gpt-4` for analysis.
*   _Andre Guerra_ for assisting with numerous components to make things simpler and more maintainable.

### Primary contributors

[](https://github.com/danielmiessler/fabric#primary-contributors)

[![Image 51](https://avatars.githubusercontent.com/u/50654?v=4)](https://github.com/danielmiessler) [![Image 52](https://avatars.githubusercontent.com/u/9218431?v=4)](https://github.com/xssdoctor) [![Image 53](https://avatars.githubusercontent.com/u/688589?v=4)](https://github.com/sbehrens) [![Image 54](https://avatars.githubusercontent.com/u/10410523?v=4)](https://github.com/agu3rra)
