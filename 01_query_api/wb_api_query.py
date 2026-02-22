import requests

url = "https://api.worldbank.org/v2/country/USA/indicator/NY.GDP.MKTP.CD?format=json"

response = requests.get(url)

print(response.status_code)
print(response.json())
