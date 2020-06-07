import json
import requests
reply = requests.get('http://192.168.1.9:5001/give_command')
print(reply.json()['2']['com'])