import os
import requests
import asyncio
import websockets


def check_secrets_sourced():
    """Errors out if Slack API key not found"""

    token = os.getenv('SLACK_BOT_TOKEN')
    if token:
        return token
    else:
        raise ValueError("No API token found! Have you sourced your secrets?")


def connect(token):
    """Connect to the Slack RTM API"""

    payload = {'token': token}
    response = requests.post('https://slack.com/api/rtm.connect', data=payload)
    if response.ok and response.json().get('ok'):
        return response.json().get('url')


async def receive_events(ws_url):
    async with websockets.connect(ws_url) as websocket:
        while True:
            print("Waiting...")
            msg = await websocket.recv()
            print(msg)


if __name__ == '__main__':
    token = check_secrets_sourced()
    websocket_url = connect(token)
    print(websocket_url)

    asyncio.get_event_loop().run_until_complete(receive_events(websocket_url))
