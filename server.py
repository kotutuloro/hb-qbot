import os
import requests
import asyncio
import websockets
import json

EVENT_LOOP = asyncio.get_event_loop()


def check_secrets_sourced():
    """Errors out if Slack API key not found"""

    token = os.getenv('SLACK_BOT_TOKEN')
    if token:
        return token
    else:
        raise ValueError("No API token found! Have you sourced your secrets?")


def connect(token):
    """Returns the WebSocket Message Server URL for this token's connection

    Connects to the Slack RTM API with the provided token and gets the WebSocket
    URL returned by the Slack API."""

    payload = {'token': token}
    response = requests.post('https://slack.com/api/rtm.connect', data=payload)
    if response.ok and response.json().get('ok'):
        return response.json().get('url')


async def receive_events(ws_url):
    """Connect to websocket URL and await received messages"""

    async with websockets.connect(ws_url) as websocket:
        # Set global event ID variable to 1
        global event_id_global
        event_id_global = 1

        # Continue waiting for event messages until websocket closes or errors
        while True:
            print("Waiting for events...")
            msg = await websocket.recv()
            print("Got a message!")

            # Parse the received event/message at the next opportunity
            EVENT_LOOP.call_soon(parse_message, websocket, msg)


def parse_message(websocket, msg):
    """Parse message type to determine and send appropriate response"""

    msg = json.loads(msg)
    print("Parsing message:", msg)

    # Use global event id to for the message ids
    global event_id_global

    # If the event message is initial hello, respond with connection message
    if msg.get('type') == 'hello':
        EVENT_LOOP.create_task(send_message(websocket,
                                            "QBot is connected!",
                                            event_id_global))
    if msg.get('type') == 'reconnect_url':
        EVENT_LOOP.create_task(send_message(websocket,
                                            "Lol chill tho",
                                            event_id_global))


async def send_message(websocket, msg, local_event_id, channel='C77DZM4F9'):
    """Send a message across the websocket to the specified channel

    Takes a websocket object, a message to send, an (local) event id to attach
    to the message, and an optional channel to send the message to. If a channel
    is not given, it will default to the qbtesting channel of the queuebottest
    Slack.
    """

    # Increment the global event id
    global event_id_global
    event_id_global += 1

    msg_json = json.dumps({'id': local_event_id,
                           'type': 'message',
                           'channel': channel,
                           'text': msg})
    print("Sending message {}...".format(local_event_id))
    await asyncio.sleep(5)
    await websocket.send(msg_json)
    print("Sent message {}!".format(local_event_id))


if __name__ == '__main__':
    token = check_secrets_sourced()
    websocket_url = connect(token)

    try:
        EVENT_LOOP.run_until_complete(receive_events(websocket_url))
    except KeyboardInterrupt:
        EVENT_LOOP.stop()
        print("\n*Stopped*")
