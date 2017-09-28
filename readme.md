# QBot

**This is a work in progress.**

QBot is a Slackbot for the Hackbright Queue.
While running, this bot analyzes messages from students on the Slack channels it is a part of.
It creates and updates a queue that keeps track of students that are asking for help on their projects so that the education staff can help them in FIFO fashion.

This bot was also an excuse for me to mess around with Python 3, asyncio, and websockets (and also regex accidentally).

### Upcoming Features:
- [x] Reopen connection on connection close
- [ ] Commands to open and close the queue
- [ ] Staff restrictions for certain commands (dequeueing and overriding)
- [ ] Restrict to one QBot instance
- [ ] Save queue state on program shutdown
