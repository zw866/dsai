# 02_function_calling_activity.py
# Activity 1: Adding a multiply_two_numbers tool
# Based on 02_function_calling.py

# This script extends the basic function calling example by adding
# a new multiply_two_numbers function as a tool alongside add_two_numbers.

# 0. SETUP ###################################

## 0.1 Load Packages #################################

import requests  # for HTTP requests
import json      # for working with JSON

## 0.2 Configuration #################################

MODEL = "smollm2:1.7b"
PORT = 11434
OLLAMA_HOST = f"http://localhost:{PORT}"
CHAT_URL = f"{OLLAMA_HOST}/api/chat"

# 1. DEFINE FUNCTIONS TO BE USED AS TOOLS ###################################

# Existing function: add two numbers
def add_two_numbers(x, y):
    """
    Add two numbers together.

    Parameters:
    -----------
    x : float
        First number
    y : float
        Second number

    Returns:
    --------
    float
        Sum of x and y
    """
    return x + y

# New function: multiply two numbers
def multiply_two_numbers(x, y):
    """
    Multiply two numbers together.

    Parameters:
    -----------
    x : float
        First number
    y : float
        Second number

    Returns:
    --------
    float
        Product of x and y
    """
    return x * y

# 2. DEFINE TOOL METADATA ###################################

# Tool metadata for add_two_numbers (existing)
tool_add_two_numbers = {
    "type": "function",
    "function": {
        "name": "add_two_numbers",
        "description": "Add two numbers",
        "parameters": {
            "type": "object",
            "required": ["x", "y"],
            "properties": {
                "x": {
                    "type": "number",
                    "description": "first number"
                },
                "y": {
                    "type": "number",
                    "description": "second number"
                }
            }
        }
    }
}

# Tool metadata for multiply_two_numbers (new)
tool_multiply_two_numbers = {
    "type": "function",
    "function": {
        "name": "multiply_two_numbers",
        "description": "Multiply two numbers",
        "parameters": {
            "type": "object",
            "required": ["x", "y"],
            "properties": {
                "x": {
                    "type": "number",
                    "description": "first number"
                },
                "y": {
                    "type": "number",
                    "description": "second number"
                }
            }
        }
    }
}

# 3. CREATE CHAT REQUEST WITH TOOLS ###################################

# Ask a multiplication question to trigger the new tool
messages = [
    {"role": "user", "content": "What is 4 * 7?"}
]

# Build the request body with both tools available
body = {
    "model": MODEL,
    "messages": messages,
    "tools": [tool_add_two_numbers, tool_multiply_two_numbers],
    "stream": False
}

# Send the request
response = requests.post(CHAT_URL, json=body)
response.raise_for_status()
result = response.json()

# 4. EXECUTE THE TOOL CALL ###################################

# The LLM will return a tool_calls array with the function name and arguments
if "tool_calls" in result.get("message", {}):
    tool_calls = result["message"]["tool_calls"]

    # Execute each tool call
    for tool_call in tool_calls:
        func_name = tool_call["function"]["name"]
        raw_args = tool_call["function"].get("arguments", {})
        # Ollama may return tool arguments either as a JSON string or as an already-parsed dict.
        func_args = json.loads(raw_args) if isinstance(raw_args, str) else raw_args

        # Get the function from globals and execute it
        func = globals().get(func_name)
        if func:
            output = func(**func_args)
            print(f"Tool called: {func_name}({func_args})")
            print(f"Tool call result: {output}")
            tool_call["output"] = output
        else:
            print(f"Function '{func_name}' not found")
else:
    print("No tool calls in response")
    print("Raw response:", json.dumps(result.get("message", {}), indent=2))
