"""
The terminal interface is just a view. Just handles the very top layer.
If you were to build a frontend this would be a way to do it
"""

from .components.code_block import CodeBlock
from .components.message_block import MessageBlock
from .magic_commands import handle_magic_command
from ..utils.display_markdown_message import display_markdown_message
from ..utils.truncate_output import truncate_output

def terminal_interface(interpreter, message):
    if not interpreter.auto_run:
        display_markdown_message("""**Open Interpreter** will require approval before running code. Use `interpreter -y` to bypass this.

        Press `CTRL-C` to exit.
        """)
    
    active_block = None

    if message:
        interactive = False
    else:
        interactive = True

    i = 0

    while True:
        try:
            if interactive: #User-Message
                #message = input("> ").strip()
                if i == 0:
                    if interpreter.ip:
                            print(f"Using IP Address: {interpreter.ip}")
                            message = (f"I want you to solve a hack the box challenge for me, located at ip: {interpreter.ip}, "
                                    "start with writing a general step by step guide to reach the goal. "
                                    "fetching the website found on the ip might be a good start. "
                                    "The end goal of a hack the box challenge is to gain root user privileges and retrieve the flag. "
                                    "This usually takes a lot of steps in between, so don't try and solve this on the first go. "
                                    "In small steps, try to get closer towards the goal. "
                                    "Also, think of the fact that websites in hack the box always have to be redirected to the correct "
                                    "ip address of the machine before they can be accessed.")
                    else:
                        print("No ip specified. Use -i [ip-address] to specify an ip")
                        message = ("Do nothing")
                    i += 1
                else:
                    message = "Recap your plan to solve this from start to finish, really briefly, just keywords. Then just keep going autonomously with what you had in mind. Execute at least one step, before consulting me again."
                    #message = "Recap your plan to solve this from start to finish, and keep going autonomously with what you hav in mind and start executing your code. Think about runtimes and potential output size of every code execution. If it might exceed 16000 characters, adjust accordingly. For websites also think of dns resolution. If a keyboard interruption happened, try something else. A moved premanently means you have to redirect the web address to the ip address of the machine. Only use the ssh connection if you know an acutal username and password, found somewhere else on the machine. The website found on port 80 is already downloaded, by curling everything that is possible to find on it, and saving it in the website direcory in your working directory. Analyzing its content and its relevance to the ctf is still your responsebility."
                print(message)  # Optionally print the auto-input for user visibility
        except KeyboardInterrupt:
            # Exit gracefully
            interactive = False # mine
            break

        if message.startswith("%") and interactive:
            handle_magic_command(interpreter, message)
            continue

        # Many users do this
        if message.strip() == "interpreter --local":
            print("Please press CTRL-C then run `interpreter --local`.")
            continue

        # Track if we've ran a code block.
        # We'll use this to determine if we should render a new code block,
        # In the event we get code -> output -> code again
        ran_code_block = False
        render_cursor = False
            
        try:
            for chunk in interpreter.chat(message, display=False, stream=True):
                if interpreter.debug_mode:
                    print("Chunk in `terminal_interface`:", chunk)
                
                # Message
                if "message" in chunk:
                    if active_block is None:
                        active_block = MessageBlock()
                    if active_block.type != "message":
                        active_block.end()
                        active_block = MessageBlock()
                    active_block.message += chunk["message"]

                # Code
                if "code" in chunk or "language" in chunk:
                    if active_block is None:
                        active_block = CodeBlock()
                    if active_block.type != "code" or ran_code_block:
                        # If the last block wasn't a code block,
                        # or it was, but we already ran it:
                        active_block.end()
                        active_block = CodeBlock()
                    ran_code_block = False
                    render_cursor = True
                
                if "language" in chunk:
                    active_block.language = chunk["language"]
                if "code" in chunk:
                    active_block.code += chunk["code"]
                if "active_line" in chunk:
                    active_block.active_line = chunk["active_line"]

                # Execution notice
                if "executing" in chunk:
                    if not interpreter.auto_run:
                        # OI is about to execute code. The user wants to approve this

                        # End the active block so you can run input() below it
                        active_block.end()

                        response = input("  Would you like to run this code? (y/n)\n\n  ")
                        print("")  # <- Aesthetic choice

                        if response.strip().lower() == "y":
                            # Create a new, identical block where the code will actually be run
                            # Conveniently, the chunk includes everything we need to do this:
                            active_block = CodeBlock()
                            active_block.margin_top = False # <- Aesthetic choice
                            active_block.language = chunk["executing"]["language"]
                            active_block.code = chunk["executing"]["code"]
                        else:
                            # User declined to run code.
                            interpreter.messages.append({
                                "role": "user",
                                "message": "I have declined to run this code."
                            })
                            break

                # Output
                if "output" in chunk:
                    ran_code_block = True
                    render_cursor = False
                    active_block.output += "\n" + chunk["output"]
                    active_block.output = active_block.output.strip() # <- Aesthetic choice
                    
                    # Truncate output
                    active_block.output = truncate_output(active_block.output, interpreter.max_output)

                if active_block:
                    active_block.refresh(cursor=render_cursor)

                yield chunk

            # (Sometimes -- like if they CTRL-C quickly -- active_block is still None here)
            if active_block:
                active_block.end()
                active_block = None

            if not interactive:
                # Don't loop
                break

        except KeyboardInterrupt:
            # Exit gracefully (this cancels LLM, returns to the interactive "> " input)
            if active_block:
                active_block.end()
                active_block = None
            continue