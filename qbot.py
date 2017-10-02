import os
import requests
import asyncio
import websockets
import json

import parsing
from myqueue import Queue

EVENT_LOOP = asyncio.get_event_loop()
HB_QUEUE = Queue()

# qbtesting channel of the queuebottest Slack
CHANNEL_ID = 'C77DZM4F9'


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
        print("Opened connection!")

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
    if msg_type == 'message' and event.get('channel') == CHANNEL_ID and not event.get('subtype'):
        response_msg = respond_to_message(f"<@{event.get('user')}>",
                                          event.get('text'))
        if response_msg:
            add_message_task(response_msg)


def respond_to_message(user, text):
    """Parse messages to determine and return appropriate response"""

    potential_new_queue = parsing.get_queue_change(text)
    response_msg = ''

    # If the message is to recreate/override the queue
    if potential_new_queue is not None:
        HB_QUEUE.override(potential_new_queue)

    # If the message indicates that they're on their way to someone:
    elif parsing.is_dequeue_message(text):

        # Find the user they're trying to pop
        user_to_pop = parsing.get_user_to_pop(text)
        if user_to_pop:
            if user_to_pop == HB_QUEUE.peek():
                HB_QUEUE.pop()
            elif user_to_pop == user:
                HB_QUEUE.remove(user)
            else:
                response_msg = f"First in, first out! You can't dequeue that person yet {user}.\n"
        else:
            response_msg = f"Please specify who you want to dequeue {user}.\n"

    # If the message indicates they want to be added to the queue:
    elif parsing.is_enqueue_message(text):
        if HB_QUEUE.has_user(user):
            response_msg = f"You're already in the queue {user}.\n"
        else:
            HB_QUEUE.push(user)

    # Return help message
    elif parsing.is_help_message(text):
        response_msg = f"Here's where a helpful message would go!\n"

    # Return a status update
    elif parsing.is_status_message(text):
        response_msg = "Qbot is up and running!\nType 'qbot help' to see a list of commands.\n"

    # If none of the conditions are met, return None
    else:
        return

    # Return the specified message (if any) and the queue
    return response_msg + str(HB_QUEUE)


async def send_message(websocket, msg, local_event_id, channel=CHANNEL_ID):
    """Send a message across the websocket to the specified channel

    Takes a websocket object, a message to send, an (local) event id to attach
    to the message, and an optional channel to send the message to. If a channel
    is not given, it will default to the global variable specified.
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


def main():
    """Recursive main function to maintain continuous qbot connection"""

    token = check_secrets_sourced()
    websocket_url = connect(token)

    try:
        EVENT_LOOP.run_until_complete(receive_events(websocket_url))
    except websockets.exceptions.ConnectionClosed:
        print("Connection closed :(")
        print("Restarting...")
        main()
    except KeyboardInterrupt:
        EVENT_LOOP.stop()
        print("\n*Stopped*")


if __name__ == '__main__':
    main()
