import requests

url = "http://127.0.0.1:5000/app/login"
resp = requests.get(url)
print(resp.content.decode())
