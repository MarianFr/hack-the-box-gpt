import litellm
import json
from ..utils.merge_deltas import merge_deltas
from ..utils.parse_partial_json import parse_partial_json
from ..utils.convert_to_openai_messages import convert_to_openai_messages
from ..utils.display_markdown_message import display_markdown_message
import tokentrim as tt
from ..utils.website import fetch_website
import re


function_schema = {
  "name": "execute",
  "description":
  "Executes code on the user's machine, **in the users local environment**, and returns the output",
  "parameters": {
    "type": "object",
    "properties": {
      "language": {
        "type": "string",
        "description":
        "The programming language (required parameter to the `execute` function)",
        "enum": ["python", "R", "shell", "applescript", "javascript", "html"]
      },
      "code": {
        "type": "string",
        "description": "The code to execute (required)"
      }
    },
    "required": ["language", "code"]
  },
}


#Added Logic
new_function_schema = {
  "name": "fetch-website",
  "description": "Fetches all files from a given website",
  "parameters": {
    "type": "object",
    "properties": {
      "ip_address": {
        "type": "string",
        "description": "IP-Address of the website"
      },
    },
    "required": ["ip_address"]
  }
}



def setup_openai_coding_llm(interpreter):
    """
    Takes an Interpreter (which includes a ton of LLM settings),
    returns a OI Coding LLM (a generator that takes OI messages and streams deltas with `message`, `language`, and `code`).
    """

    def coding_llm(messages):
        
        # Convert messages
        messages = convert_to_openai_messages(messages)

        # Add OpenAI's recommended function message
        messages[0]["content"] += "\n\nOnly use the function you have been provided with."

        # Seperate out the system_message from messages
        # (We expect the first message to always be a system_message)
        system_message = messages[0]["content"]
        messages = messages[1:]

        # Trim messages, preserving the system_message
        try:
            messages = tt.trim(messages=messages, system_message=system_message, model=interpreter.model)
        except:
            if interpreter.context_window:
                messages = tt.trim(messages=messages, system_message=system_message, max_tokens=interpreter.context_window)
            else:
                display_markdown_message("""
                **We were unable to determine the context window of this model.** Defaulting to 3000.
                If your model can handle more, run `interpreter --context_window {token limit}` or `interpreter.context_window = {token limit}`.
                """)
                messages = tt.trim(messages=messages, system_message=system_message, max_tokens=3000)

        if interpreter.debug_mode:
            print("Sending this to the OpenAI LLM:", messages)

        params = {
            'model': interpreter.model,
            'messages': messages,
            'stream': True,
            'functions': [function_schema, new_function_schema],  #Added Logic
            #'function_call': "auto",
        }


        # Optional inputs
        if interpreter.api_base:
            params["api_base"] = interpreter.api_base
        if interpreter.api_key:
            params["api_key"] = interpreter.api_key
        if interpreter.max_tokens:
            params["max_tokens"] = interpreter.max_tokens
        if interpreter.temperature:
            params["temperature"] = interpreter.temperature
        
        # These are set directly on LiteLLM
        if interpreter.max_budget:
            litellm.max_budget = interpreter.max_budget
        if interpreter.debug_mode:
            litellm.set_verbose = True

        # Report what we're sending to LiteLLM
        if interpreter.debug_mode:
            print("Sending this to LiteLLM:", params)

        response = litellm.completion(**params)

        #print("\n response: ", response)

        accumulated_deltas = {}
        language = None
        code = ""
        last_ip_address = None #Edit

        for chunk in response:

            if ('choices' not in chunk or len(chunk['choices']) == 0):
                # This happens sometimes
                continue

            delta = chunk["choices"][0]["delta"]

            # Accumulate deltas
            accumulated_deltas = merge_deltas(accumulated_deltas, delta)
            #print("\n delta : ", accumulated_deltas)

            if "content" in delta and delta["content"]:
                yield {"message": delta["content"]}


            #print("Chunk:", chunk)
            #print("Accumulated Deltas:", accumulated_deltas)


            if ("function_call" in accumulated_deltas 
                and "arguments" in accumulated_deltas["function_call"]): #Added Logic

                arguments = accumulated_deltas["function_call"]["arguments"]
                arguments = parse_partial_json(arguments)

                # Extracting the function_call as a JSON string
                function_call_json = accumulated_deltas.get('function_call')

                # Parsing JSON string to Python Dictionary
                # This assumes that 'function_call' is a string formatted as valid JSON.
                function_call_data = json.loads(str(function_call_json))

                # Extracting the function name
                function_name = function_call_data.get("name")

                # if function_name != None:
                #     print(function_name)
                #     if arguments != None:
                #         print("arguments: ", arguments)
                # else:
                #     print("function_name is none")

                if function_name == "fetch-website":
                    #print("in fetch-website")
                    #print("arguments: ", arguments)


                    if arguments is not None and "ip_address" in arguments:
                        ip_address_candidate = arguments["ip_address"]

                        # Validate IP Address with regex
                        ip_pattern = re.compile(r'\b(?:\d{1,3}\.){3}\d{1,3}\b') #Ugly solution, but its just here for now testing the general idea
                        if ip_pattern.fullmatch(ip_address_candidate):
                            if ip_address_candidate == last_ip_address:
                                #print("error, IP address is the same as the last one processed")
                                pass
                            else:
                                ip_address = ip_address_candidate  # Only set IP when it is fully validated
                                last_ip_address = ip_address
                                url = f"http://{ip_address}"
                                print("fetching the following url: ", url)
                                yield {"ip_address": 1}
                                if interpreter.api_key != None:
                                    fetch_website(url, '/', interpreter.api_key)
                                else:
                                    print("\n\nFetching Failed, API key not propeerly defined")
                                    print(interpreter.api_base)
                                    print(interpreter.api_key)
                        else:
                            #print("error, IP address not complete or invalid")
                            pass
                    else:
                        #print("error, parameter missing")
                        pass

                else:
                    if arguments:
                        if (language is None
                            and "language" in arguments
                            and "code" in arguments # <- This ensures we're *finished* typing language, as opposed to partially done
                            and arguments["language"]):
                            language = arguments["language"]
                            yield {"language": language}
                        
                        if language is not None and "code" in arguments:
                            # Calculate the delta (new characters only)
                            code_delta = arguments["code"][len(code):]
                            # Update the code
                            code = arguments["code"]
                            # Yield the delta
                            if code_delta:
                                yield {"code": code_delta}
            
    return coding_llm