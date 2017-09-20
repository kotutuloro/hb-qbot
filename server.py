import websocket
import requests
import os


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


if __name__ == '__main__':
    token = check_secrets_sourced()
    websocket_url = connect(token)
