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

    # Add previous sent message's success info to dictionary for server replies
    if reply:
        if not msg_type:
            global sent_responses
            sent_responses[reply] = event
            print(sent_responses)
        return

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

    # Further parsing for actual messages (ignoring things like channel join msgs)
    if msg_type == 'message' and not event.get('subtype'):
        parse_message(websocket,
                      f"<@{event.get('user')}>",
                      event.get('text'))


def parse_message(websocket, user, text):
    """Parse messages to determine and send appropriate response"""

    potential_new_queue = get_queue_change_message(text)

    # If the message is to print or reform the queue
    if potential_new_queue is not None:
        # TODO: Restrict to staff
        print("I would change the queue now!")

        EVENT_LOOP.create_task(send_message(websocket,
                                            f"{str(potential_new_queue)}",
                                            event_id_global))

    # If the message indicates that they're on their way to someone:
    elif is_dequeue_message(text):
        # TODO: Restrict to staff or self

        # Find the user they're trying to pop
        user_to_pop = re.search('<@.+>', text)
        if user_to_pop:
            user_to_pop = user_to_pop.group()
            EVENT_LOOP.create_task(send_message(websocket,
                                                f"They're on their way {user_to_pop}",
                                                event_id_global))

    # If the message indicates they want to be added to the queue:
    elif is_enqueue_message(text):
        EVENT_LOOP.create_task(send_message(websocket,
                                            f"Adding to the queue {user}",
                                            event_id_global))

    # Return help message for calls to self and stop there
    elif is_help_message(text):
        EVENT_LOOP.create_task(send_message(websocket,
                                            f"Here's where a helpful message would go!",
                                            event_id_global))
        # Don't send the queue after this
        return

    # If no other conditons met, send confusion message and stop there
    else:
        EVENT_LOOP.create_task(send_message(websocket,
                                            f"Sorry {user}, I didn't understand that.\nType 'qbot help' to see a list of commands.",
                                            event_id_global))
        # Don't send the queue after this
        return

    # Print the actual queue here


def is_enqueue_message(text):
    """Return whether text is message to pop someone from queue"""

    plain_text = text.strip().lower()
    return (plain_text.startswith('omw')
            or plain_text.startswith('dequeue')
            or plain_text.startswith('dq')
            or plain_text.startswith('deq'))


def is_dequeue_message(text):
    """Return whether text is message to add self to queue"""

    plain_text = text.strip().lower()
    return (plain_text.startswith('enqueue')
            or plain_text.startswith('enq')
            or plain_text.startswith('nq'))


def get_queue_change_message(text):
    """Return whether text is trying to change the queue"""

    # Construct regex for things like: queue.empty(), q.clear(  ), queue=[],
    # QUEUE = [ <@User1234> <@U1234here>   ]
    re_queue_name_alt = '(q|queue)'
    re_clear_method_alt = '\.(clear|empty)\(\s*\)'
    re_usernames = '(<@\w*>\s*)*'
    re_list = f'\s*=\s*\[\s*({ re_usernames })\s*\]'

    search_str = f'{ re_queue_name_alt }({ re_clear_method_alt }|{ re_list })'
    match = re.search(search_str, text, flags=re.I)
    # For reference, here's the group order for this regex match
    # Group 1: 'q' or 'queue' to start (mandatory)
    # Group 2: '.a_method( )' or ' = [ a list ]' (mandatory)
    # Group 3: 'clear' or 'empty', if a method
    # Group 4: all usernames in the list, if a list
    # Group 5: last username (and whitespace) found, if a list

    if match:
        # If '.clear()' or '.empty()' was chosen, have an empty queue
        if match.group(3):
            new_queue = []
        # Otherwise find each username in the list
        else:
            new_queue = re.findall('<@\w*>', match.group(4))

    # If no match, then not changing the queue
    else:
        new_queue = None

    return new_queue


def is_help_message(text):
    """Return whether text is asking for a list of commands"""

    plain_text = text.strip().lower()
    return ((plain_text.startwith('qbot')
                or plain_text.startswith('queuebot'))
            and re.search('\bhelp\b', plain_text))


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
