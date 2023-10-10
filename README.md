Modified Version of the Code Interpreter, to autonomously solve hack-the-box ctf challenges.

[![Example_Video](https://img.youtube.com/vi/watch?v=5tQ9wEdutAE&ab_channel=Marian/0.jpg)](https://www.youtube.com/watch?v=5tQ9wEdutAE&ab_channel=Marian)  Here an exaple of how it usually looks like in this stage of development. Starts off quite good, but then eventually gets stuck because it misses the key part of the solution, due to an error in the code it tries to execute and thus discards the correct approach.


The Base of open-interpreter enables Chat-GPT or local LLM's to take over the local terminal on a machine, and thus execute shell commands or execute code (python, java...).


An adjusted version of this, in combination with running on a kali linux machine, chat-gpt has the ability to auntonomously connect to a hack-the-box machine, perform reconnaissance using the known preinstalled tools and also try and exploit vulnerabilities.  


Via "export OPENAI_API_KEY=[api-key]" the api key can be set


And via e.g. "interpreter --model gpt-3.5-turbo -y -i 10.10.11.221" The Machine on ip-address 10.10.11.221 can be targeted using the gpt-3.5.-turbo model. Not defining the model, defaults to chat-gpt4, which is a lot more powerful, but also costly.


Chat-GPT is also enhanced in this configuration via a custom function called "fetch-website". 
It fetches, saves, and analyzes the content of a website and its associated assets (like CSS and JS files), while also generating reports about the potential security relevance of the content based on hypothetical hack-the-box Capture The Flag (CTF) challenges, via another independent chat-gpt api call for each file that needs to be analyzed. This allows the operating LLM, to focus on the most relevant data and assuring it keeps track of its main goal.



I am still working on fixing the installing process. 

The easies way right now is to install open-interpreter how it is intended, via pip install open-interpreter, and then exchanging the interpreter folder in it with the one from this repository. But thats not really pretty and shouldn't stay that way.



General Open-Interpreter ReadMe:


<h1 align="center">● Open Interpreter</h1>

<p align="center">
    <a href="https://discord.gg/6p3fD6rBVm">
        <img alt="Discord" src="https://img.shields.io/discord/1146610656779440188?logo=discord&style=flat&logoColor=white"/>
    </a>
    <a href="README_JA.md"><img src="https://img.shields.io/badge/ドキュメント-日本語-white.svg" alt="JA doc"/></a>
    <a href="README_ZH.md"><img src="https://img.shields.io/badge/文档-中文版-white.svg" alt="ZH doc"/></a>
    <a href="README_IN.md"><img src="https://img.shields.io/badge/Hindi-white.svg" alt="IN doc"/></a>
    <img src="https://img.shields.io/static/v1?label=license&message=MIT&color=white&style=flat" alt="License"/>
    <br>
    <br>
    <b>Let language models run code on your computer.</b><br>
    An open-source, locally running implementation of OpenAI's Code Interpreter.<br>
    <br><a href="https://openinterpreter.com">Get early access to the desktop app</a>‎ ‎ |‎ ‎ <b><a href="https://docs.openinterpreter.com/">Read our new docs</a></b><br>
</p>

<br>

![poster](https://github.com/KillianLucas/open-interpreter/assets/63927363/08f0d493-956b-4d49-982e-67d4b20c4b56)

<br>

```shell
pip install open-interpreter
```

```shell
interpreter
```

<br>

**Open Interpreter** lets LLMs run code (Python, Javascript, Shell, and more) locally. You can chat with Open Interpreter through a ChatGPT-like interface in your terminal by running `$ interpreter` after installing.

This provides a natural-language interface to your computer's general-purpose capabilities:

- Create and edit photos, videos, PDFs, etc.
- Control a Chrome browser to perform research
- Plot, clean, and analyze large datasets
- ...etc.

**⚠️ Note: You'll be asked to approve code before it's run.**

<br>

## Demo

https://github.com/KillianLucas/open-interpreter/assets/63927363/37152071-680d-4423-9af3-64836a6f7b60

#### An interactive demo is also available on Google Colab:

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1WKmRXZgsErej2xUriKzxrEAXdxMSgWbb?usp=sharing)

#### Along with an example implementation of a voice interface (inspired by _Her_):

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1NojYGHDgxH6Y1G1oxThEBBb2AtyODBIK)

## Quick Start

```shell
pip install open-interpreter
```

### Terminal

After installation, simply run `interpreter`:

```shell
interpreter
```

### Python

```python
import interpreter

interpreter.chat("Plot AAPL and META's normalized stock prices") # Executes a single command
interpreter.chat() # Starts an interactive chat
```

## Comparison to ChatGPT's Code Interpreter

OpenAI's release of [Code Interpreter](https://openai.com/blog/chatgpt-plugins#code-interpreter) with GPT-4 presents a fantastic opportunity to accomplish real-world tasks with ChatGPT.

However, OpenAI's service is hosted, closed-source, and heavily restricted:

- No internet access.
- [Limited set of pre-installed packages](https://wfhbrian.com/mastering-chatgpts-code-interpreter-list-of-python-packages/).
- 100 MB maximum upload, 120.0 second runtime limit.
- State is cleared (along with any generated files or links) when the environment dies.

---

Open Interpreter overcomes these limitations by running on your local environment. It has full access to the internet, isn't restricted by time or file size, and can utilize any package or library.

This combines the power of GPT-4's Code Interpreter with the flexibility of your local development environment.

## Commands

**Update:** The Generator Update (0.1.5) introduced streaming:

```python
message = "What operating system are we on?"

for chunk in interpreter.chat(message, display=False, stream=True):
  print(chunk)
```

### Interactive Chat

To start an interactive chat in your terminal, either run `interpreter` from the command line:

```shell
interpreter
```

Or `interpreter.chat()` from a .py file:

```python
interpreter.chat()
```

**You can also stream each chunk:**

```python
message = "What operating system are we on?"

for chunk in interpreter.chat(message, display=False, stream=True):
  print(chunk)
```

### Programmatic Chat

For more precise control, you can pass messages directly to `.chat(message)`:

```python
interpreter.chat("Add subtitles to all videos in /videos.")

# ... Streams output to your terminal, completes task ...

interpreter.chat("These look great but can you make the subtitles bigger?")

# ...
```

### Start a New Chat

In Python, Open Interpreter remembers conversation history. If you want to start fresh, you can reset it:

```python
interpreter.reset()
```

### Save and Restore Chats

`interpreter.chat()` returns a List of messages, which can be used to resume a conversation with `interpreter.messages = messages`:

```python
messages = interpreter.chat("My name is Killian.") # Save messages to 'messages'
interpreter.reset() # Reset interpreter ("Killian" will be forgotten)

interpreter.messages = messages # Resume chat from 'messages' ("Killian" will be remembered)
```

### Customize System Message

You can inspect and configure Open Interpreter's system message to extend its functionality, modify permissions, or give it more context.

```python
interpreter.system_message += """
Run shell commands with -y so the user doesn't have to confirm them.
"""
print(interpreter.system_message)
```

### Change your Language Model

Open Interpreter uses [LiteLLM](https://docs.litellm.ai/docs/providers/) to connect to language models.

You can change the model by setting the model parameter:

```shell
interpreter --model gpt-3.5-turbo
interpreter --model claude-2
interpreter --model command-nightly
```

In Python, set the model on the object:

```python
interpreter.model = "gpt-3.5-turbo"
```

[Find the appropriate "model" string for your language model here.](https://docs.litellm.ai/docs/providers/)

### Running Open Interpreter locally

ⓘ **Issues running locally?** Read our new [GPU setup guide](./docs/GPU.md) and [Windows setup guide](./docs/WINDOWS.md).

You can run `interpreter` in local mode from the command line to use `Code Llama`:

```shell
interpreter --local
```

Or run any Hugging Face model **locally** by running `--local` in conjunction with a repo ID (e.g. "tiiuae/falcon-180B"):

```shell
interpreter --local --model tiiuae/falcon-180B
```

#### Local model params

You can easily modify the `max_tokens` and `context_window` (in tokens) of locally running models.

Smaller context windows will use less RAM, so we recommend trying a shorter window if GPU is failing.

```shell
interpreter --max_tokens 2000 --context_window 16000
```

### Debug mode

To help contributors inspect Open Interpreter, `--debug` mode is highly verbose.

You can activate debug mode by using it's flag (`interpreter --debug`), or mid-chat:

```shell
$ interpreter
...
> %debug true <- Turns on debug mode

> %debug false <- Turns off debug mode
```

### Interactive Mode Commands

In the interactive mode, you can use the below commands to enhance your experience. Here's a list of available commands:

**Available Commands:**  
 • `%debug [true/false]`: Toggle debug mode. Without arguments or with 'true', it
enters debug mode. With 'false', it exits debug mode.
 • `%reset`: Resets the current session.
 • `%undo`: Remove previous messages and its response from the message history.
 • `%save_message [path]`: Saves messages to a specified JSON path. If no path is
provided, it defaults to 'messages.json'.
 • `%load_message [path]`: Loads messages from a specified JSON path. If no path  
 is provided, it defaults to 'messages.json'.
 • `%tokens`: Counts the number of tokens used by the current conversation's messages and displays a cost estimate via [LiteLLM's `cost_per_token()` method](https://docs.litellm.ai/docs/completion/token_usage#2-cost_per_token). **Note**: This only accounts for messages currently in the conversation, not messages that have been sent or received and then removed via `%undo`.
 • `%help`: Show the help message.

### Configuration

Open Interpreter allows you to set default behaviors using a `config.yaml` file.

This provides a flexible way to configure the interpreter without changing command-line arguments every time.

Run the following command to open the configuration file:

```
interpreter --config
```

## Safety Notice

Since generated code is executed in your local environment, it can interact with your files and system settings, potentially leading to unexpected outcomes like data loss or security risks.

**⚠️ Open Interpreter will ask for user confirmation before executing code.**

You can run `interpreter -y` or set `interpreter.auto_run = True` to bypass this confirmation, in which case:

- Be cautious when requesting commands that modify files or system settings.
- Watch Open Interpreter like a self-driving car, and be prepared to end the process by closing your terminal.
- Consider running Open Interpreter in a restricted environment like Google Colab or Replit. These environments are more isolated, reducing the risks associated with executing arbitrary code.

## How Does it Work?

Open Interpreter equips a [function-calling language model](https://platform.openai.com/docs/guides/gpt/function-calling) with an `exec()` function, which accepts a `language` (like "Python" or "JavaScript") and `code` to run.

We then stream the model's messages, code, and your system's outputs to the terminal as Markdown.

# Contributing

Thank you for your interest in contributing! We welcome involvement from the community.

Please see our [Contributing Guidelines](./CONTRIBUTING.md) for more details on how to get involved.

## License

Open Interpreter is licensed under the MIT License. You are permitted to use, copy, modify, distribute, sublicense and sell copies of the software.

**Note**: This software is not affiliated with OpenAI.

> Having access to a junior programmer working at the speed of your fingertips ... can make new workflows effortless and efficient, as well as open the benefits of programming to new audiences.
>
> — _OpenAI's Code Interpreter Release_

<br>
