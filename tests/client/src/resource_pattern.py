
import requests
import time

class DataMismatch(Exception):
    def __init__(self, expected, received):
        self.expected = expected
        self.received = received
    
    def __str__(self):
        return (
            f"Expected: \033[1;32;40m{str(self.expected)}\n"
            f"Received: {str(self.received)}\n"
        )


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
            "first_cursor": None,
            "last_cursor": None,
            "has_next_page": True,
            "data": []
        }

        if received_data != expected_data:
            raise DataMismatch(received_data, expected_data)


    except DataMismatch as e:
        print(e)
        break

    except Exception as e:
        print('Unexpected Exception')
        break
