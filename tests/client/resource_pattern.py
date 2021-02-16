
import requests
import time

while True:
    time.sleep(3)

    try:
        url = "http://server:4000/authors"
        payload={}
        headers = {}
        response = requests.request("GET", url, headers=headers, data=payload)
        print(response.text)

    except:
        print("Failed to connect!")
