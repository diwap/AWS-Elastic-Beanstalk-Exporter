import os
import requests
import json


def send_message(message: str):
    try:
        url = os.getenv("SLACK_WEBHOOK_URL")
        if url:
            data = {
                'text': message
            }
            payload = json.dumps(data)

            headers = {
            'Content-Type': 'application/json'
            }

            return requests.request("POST", url, headers=headers, data = payload)

    except Exception as e:
        print(e)
        pass