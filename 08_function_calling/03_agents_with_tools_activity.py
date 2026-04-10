# 03_agents_with_tools_activity.py
# Activity 2: Adding a New Tool Function
# Demonstrates creating a custom tool and testing it with the agent() wrapper.

# 0. SETUP ###################################

import json
import functions
from functions import agent

# Select model
MODEL = "smollm2:1.7b"

# 1. DEFINE THE NEW TOOL FUNCTION ###################################

def calculate_average(numbers):
    """Calculate the average of a list of numbers."""
    return sum(numbers) / len(numbers)

# Register the function in the functions module's global scope
# so that agent() can find it via globals().get(func_name)
functions.calculate_average = calculate_average

# 2. DEFINE TOOL METADATA ###################################

tool_calculate_average = {
    "type": "function",
    "function": {
        "name": "calculate_average",
        "description": "Calculate the average of a list of numbers",
        "parameters": {
            "type": "object",
            "required": ["numbers"],
            "properties": {
                "numbers": {
                    "type": "array",
                    "items": {"type": "number"},
                    "description": "A list of numbers to average"
                }
            }
        }
    }
}

# 3. TEST THE TOOL WITH AGENT ###################################

messages = [
    {"role": "user", "content": "What is the average of 10, 20, 30, 40, 50?"}
]

resp = agent(messages=messages, model=MODEL, output="tools", tools=[tool_calculate_average])
print("Tool Call Result:")
print(resp)
