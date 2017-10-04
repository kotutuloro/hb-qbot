"""Helper functions for determining the keyword/type of message request"""

import re


def is_enqueue_message(text):
    """Return whether text is message to add self to queue

    Check if the text starts with 'enq', 'nq', 'enqueue', or 'nqueue'

    >>> is_enqueue_message("Enqueue")
    True
    >>> is_enqueue_message("ENQ!!")
    True
    >>> is_enqueue_message("nq please thanks")
    True

    >>> is_enqueue_message("I am want to be enqueue")
    False
    >>> is_enqueue_message("nqqqqqqq")
    False
    """

    plain_text = text.strip().lower()
    search_re = r'^e?nq(ueue)?\b'
    return bool(re.search(search_re, plain_text))


def is_dequeue_message(text):
    """Return whether text is message to pop someone from queue

    Check if the text starts with 'omw', deq', 'dq', 'dequeue', or 'dqueue'.

    >>> is_dequeue_message("omw <@U12345678>!")
    True
    >>> is_dequeue_message("Dequeue")
    True
    >>> is_dequeue_message("DEQ!!")
    True
    >>> is_dequeue_message("dq me pls & ty")
    True

    >>> is_dequeue_message("I am want to be dequeue")
    False
    >>> is_dequeue_message("dqqqqqqq")
    False
    """

    plain_text = text.strip().lower()
    search_re = r'^(omw|de?q(ueue)?)\b'
    return bool(re.search(search_re, plain_text))


def get_user_to_pop(text):
    """Return the first user mentioned, or None if no user

    >>> get_user_to_pop("give me <@User1234>")
    '<@User1234>'
    >>> get_user_to_pop("no user here")
    >>> get_user_to_pop("none here either <@  >")
    """

    match = re.search(r'<@\w+>', text)
    if match:
        return match.group()
    else:
        return None


def get_queue_change(text):
    """Return list of users to construct the queue, or None if no valid changes

    >>> get_queue_change("QUEUE.empty()")
    []
    >>> get_queue_change("q = [ <@U1234> <@xyz123> ]")
    ['<@U1234>', '<@xyz123>']
    >>> get_queue_change("This isn't a real queue change")
    """

    # Construct regex for things like: queue.empty(), q.clear(  ), queue=[],
    # QUEUE = [ <@User1234> <@U1234here>   ]
    re_queue_name_alt = r'q(ueue)?'
    re_clear_method_alt = r'\.(clear|empty)\(\s*\)'
    re_usernames = r'(<@\w+>\s*)*'
    re_list = rf'\s*=\s*\[\s*({ re_usernames })\s*\]'

    search_re = rf'{ re_queue_name_alt }({ re_clear_method_alt }|{ re_list })'
    match = re.search(search_re, text, flags=re.I)
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
            new_queue = re.findall(r'<@\w+>', match.group(4))

    # If no match, then not changing the queue
    else:
        new_queue = None

    return new_queue


def is_help_message(text):
    """Return whether text is asking for a list of commands

    Check if the text starts with qbot or queuebot and has the word 'help'

    >>> is_help_message("qbot help please")
    True
    >>> is_help_message("queuebot come help me thx")
    True
    >>> is_help_message("queuebot to the rescue")
    False
    >>> is_help_message("hey qbot help me out")
    False
    """

    plain_text = text.strip().lower()
    return bool(re.search(r'^q(ueue)?bot\b.+\bhelp\b', plain_text))


def is_status_message(text):
    """Return whether text is asking for a status update

    Check if the text starts with q or queue (bot) and has the word 'status'

    >>> is_status_message("queue status update please")
    True
    >>> is_status_message("qbot, what's your status?")
    True
    >>> is_status_message("status of the queue")
    False
    """

    plain_text = text.strip().lower()
    return bool(re.search(r'^q(ueue)?(bot)?\b.+\bstatus\b', plain_text))
