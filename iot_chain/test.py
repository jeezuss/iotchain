import requests

url = "http://192.168.1.4:8123/api/services/light/turn_on"


headers = {
  'Conten': 'application/json',
  'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiIxY2QwOGY2NjIwODM0NTk5YjFlNzZmZTdjZTA4MzU1NCIsImlhdCI6MTU5MDUyNTg2NiwiZXhwIjoxOTA1ODg1ODY2fQ.m271KEiFzAEULkMrKAg86prnGZqre2sIrkEP8EZUZMA'
}

response = requests.request("GET", url, headers=headers)

print(response.text.encode('utf8'))