# test_requests.py
# Make a POST request with JSON data
# Pairs with ACTIVITY_add_documentation_to_cursor.md
# Tim Fraser

# Demonstrates how to send JSON in the request body using requests.
# The json= parameter automatically serializes the dict and sets Content-Type.

# 0. Setup #################################

import requests

# 1. POST request with JSON body ###############################

url = "https://httpbin.org/post"
data = {"name": "test"}

# json= serializes data to JSON and sets Content-Type: application/json
response = requests.post(url, json=data)

# Inspect the response
print(response.status_code)
print(response.json())
