import os
import requests
import asyncio
import websockets
import json
import re

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

        # TODO: Create a ping coro to ping every x seconds and add to event loop

        # Continue waiting for event messages until websocket closes or errors
        while True:
            print("Waiting for events...")
            msg = await websocket.recv()
            print("Got an event!")

            # Parse the received event at the next opportunity
            EVENT_LOOP.call_soon(parse_event, websocket, msg)


def parse_event(websocket, event):
    """Parse event type to determine and send appropriate response"""

    event = json.loads(event)
    print("Parsing event:", event)
    msg_type = event.get('type')
    reply = event.get('reply_to')

    if reply:
        return
        # TODO: Add to dictionary whether previous sent message was successful or not

    # Use global event id to for the message ids
    global event_id_global

    # If the event is initial hello, respond with connection message
    if msg_type == 'hello':
        EVENT_LOOP.create_task(send_message(websocket,
                                            "QBot is connected!",
                                            event_id_global))
    # If the event is connection closing goodbye, respond with goodbye
    if msg_type == 'goodbye':
        EVENT_LOOP.create_task(send_message(websocket,
                                            "QBot: Out!",
                                            event_id_global))

    # Further parsing for actual messages
    if msg_type == 'message' and not event.get('subtype'):
        parse_message(websocket,
                      event.get('user'),
                      event.get('text'))


def parse_message(websocket, user, text):
    """Parse messages to determine and send appropriate response"""

    plain_text = text.strip().lower()

    # If the message indicates that they're on their way to someone:
    if is_dequeue_message(text):
        # TODO: Restrict to staff

        # Find the user they're trying to pop
        user_to_pop = re.search('<@.+>', text)
        if user_to_pop:
            user_to_pop = user_to_pop.group(0)
            EVENT_LOOP.create_task(send_message(websocket,
                                                "They're on their way {}".format(user_to_pop),
                                                event_id_global))

    # If the message indicates they want to be added to the queue:
    elif is_enqueue_message(text):
        EVENT_LOOP.create_task(send_message(websocket,
                                            "Adding to the queue <@{}>".format(user),
                                            event_id_global))

    # If no other conditons met
    else:
        EVENT_LOOP.create_task(send_message(websocket,
                                            "Sorry <@{}>, I didn't understand that!".format(user),
                                            event_id_global))


def is_enqueue_message(text):
    """Return whether text is message to pop someone from queue"""

    plain_text = text.strip().lower()
    return (plain_text.startswith('omw')
            or plain_text.startswith('dequeue')
            or plain_text.startswith('dq')
            or plain_text.startswith('deq'))


def is_dequeue_message(text):
    """Return where text is message to add self to queue"""

    plain_text = text.strip().lower()
    return (plain_text.startswith('enqueue')
            or plain_text.startswith('enq')
            or plain_text.startswith('nq'))



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

    # Send the message to Slack
    msg_json = json.dumps({'id': local_event_id,
                           'type': 'message',
                           'channel': channel,
                           'text': msg})
    print("Sending message {}: {}...".format(local_event_id, msg))
    # await asyncio.sleep(5)
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
