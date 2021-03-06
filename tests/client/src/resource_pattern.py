
import requests
import time

while True:
    time.sleep(3)

    try:
        url = "http://server:4000/authors"
        payload={}
        headers = {}
        response = requests.request("GET", url, headers=headers, data=payload)
        received_data = response.json()

        print(received_data)

        expected_data = {
            "first_cursor": null,
            "last_cursor": null,
            "has_next_page": True,
            "data": []
        }

        if received_data != expected_data:
            print('The test failed!')


    except:
        print("Failed to connect!")
