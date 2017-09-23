"""Helper functions for determining the keyword/type of message request"""

import re


def is_enqueue_message(text):
    """Return whether text is message to add self to queue

    Check if the text starts with 'enq', 'nq', or 'enqueue'
    """

    plain_text = text.strip().lower()
    search_re = r'^(enqueue|enq|nq)\b'
    return bool(re.search(search_re, plain_text))


def is_dequeue_message(text):
    """Return whether text is message to pop someone from queue

    Check if the text starts with 'omw', deq', 'dq', or 'dequeue'.
    """

    plain_text = text.strip().lower()
    search_re = r'^(omw|dequeue|deq|dq)\b'
    return bool(re.search(search_re, plain_text))


def get_user_to_pop(text):
    """Return the requested user to dequeue, or None if no user"""

    match = re.search(r'<@\w+>', text)
    if match:
        return match.group()
    else:
        return None


def get_queue_change(text):
    """Return list of users to construct the queue, or None if no valid changes"""

    # Construct regex for things like: queue.empty(), q.clear(  ), queue=[],
    # QUEUE = [ <@User1234> <@U1234here>   ]
    re_queue_name_alt = r'(q|queue)'
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
    """

    plain_text = text.strip().lower()
    return bool(re.search(r'^(qbot|queuebot)\b.+\bhelp\b', plain_text))
