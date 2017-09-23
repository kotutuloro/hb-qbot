import os
import requests
import asyncio
import websockets
import json

import parsing

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

    payload = {'token': token,
               'presence_sub': True}
    response = requests.post('https://slack.com/api/rtm.connect', data=payload)
    if response.ok and response.json().get('ok'):
        return response.json().get('url')


async def receive_events(ws_url):
    """Connect to websocket URL and await received messages"""

    async with websockets.connect(ws_url) as websocket:
        # Set global event ID variable to 1
        global event_id_global
        event_id_global = 1

        # Create global dictionary to track message statuses
        global sent_responses
        sent_responses = {}

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

    # Add previous sent message's success info to dictionary for server replies
    if reply:
        if not msg_type:
            global sent_responses
            sent_responses[reply] = event
            # print(sent_responses)
        return

    def add_message_task(msg):
        """Add a coro to the event loop to send message through the websocket"""

        # Use global event id to for the message ids
        global event_id_global
        EVENT_LOOP.create_task(send_message(websocket,
                                            msg,
                                            event_id_global))
        event_id_global += 1

    # If the event is initial hello, respond with connection message
    if msg_type == 'hello':
        add_message_task("QBot is connected!")

    # If the event is connection closing goodbye, respond with goodbye
    if msg_type == 'goodbye':
        add_message_task("QBot: Out!")

    # Further parsing for actual messages (ignoring things like channel join msgs)
    if msg_type == 'message' and not event.get('subtype'):
        response_msg = respond_to_message(f"<@{event.get('user')}>",
                                          event.get('text'))
        if response_msg:
            add_message_task(response_msg)


def respond_to_message(user, text):
    """Parse messages to determine and return appropriate response"""

    potential_new_queue = parsing.get_queue_change(text)

    # If the message is to recreate/override the queue
    if potential_new_queue is not None:
        print("I would change the queue now!")
        response_msg = f"{str(potential_new_queue)}"

    # If the message indicates that they're on their way to someone:
    elif parsing.is_dequeue_message(text):

        # Find the user they're trying to pop
        user_to_pop = parsing.get_user_to_pop(text)
        if user_to_pop:
            response_msg = f"They're on their way {user_to_pop}"
        else:
            response_msg = "Lol who you even tryna pop?"

    # If the message indicates they want to be added to the queue:
    elif parsing.is_enqueue_message(text):
        response_msg = f"Adding to the queue {user}"

    # Return help message for calls to self and stop there
    elif parsing.is_help_message(text):
        response_msg = f"Here's where a helpful message would go!"

    # If no other conditons met, send confusion message and stop there
    else:
        response_msg = f"Sorry {user}, I didn't understand that.\nType 'qbot help' to see a list of commands."

    return response_msg


async def send_message(websocket, msg, local_event_id, channel='C77DZM4F9'):
    """Send a message across the websocket to the specified channel

    Takes a websocket object, a message to send, an (local) event id to attach
    to the message, and an optional channel to send the message to. If a channel
    is not given, it will default to the qbtesting channel of the queuebottest
    Slack.
    """

    # Send the message to Slack
    msg_json = json.dumps({'id': local_event_id,
                           'type': 'message',
                           'channel': channel,
                           'text': msg})
    print(f"Sending message {local_event_id}: {msg}...")
    # await asyncio.sleep(5)
    await websocket.send(msg_json)
    print(f"Sent message {local_event_id}!")

    # Add the sent message to global sent_responses dict
    global sent_responses
    sent_responses[local_event_id] = None


if __name__ == '__main__':
    token = check_secrets_sourced()
    websocket_url = connect(token)

    try:
        EVENT_LOOP.run_until_complete(receive_events(websocket_url))
    except KeyboardInterrupt:
        EVENT_LOOP.stop()
        print("\n*Stopped*")
