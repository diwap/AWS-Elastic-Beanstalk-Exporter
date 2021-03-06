import os
import requests
import json


def send_message(message: str, **kwargs):
    slack_url = kwargs.get('slack_url')
    try:
        url = os.getenv("SLACK_WEBHOOK_URL", slack_url)
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