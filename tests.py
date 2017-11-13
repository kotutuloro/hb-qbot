import unittest
import requests

import qbot
import myqueue
import parsing

import mocks


class TestQbot(unittest.TestCase):
    """Tests for the QBot"""

    def setUp(self):
        requests.post = mocks.post_request
        # Probably something with resetting qbot.EVENT_LOOP & qbot.HB_QUEUE
        # Also setting up a websocket?

    def test_secrets_sourced(self):
        import os

        os.environ['SLACK_BOT_TOKEN'] = 'abc123xyz'
        self.assertEqual('abc123xyz', qbot.check_secrets_sourced())

        os.environ.pop('SLACK_BOT_TOKEN', None)
        self.assertRaises(ValueError, qbot.check_secrets_sourced)

    def test_connect(self):
        good_url = qbot.connect('good-token')
        self.assertEqual(good_url, 'websock.et/url')

        no_url = qbot.connect('bad-token')
        self.assertIsNone(no_url)

    def test_receive_events(self):
        pass

    def test_parse_event(self):
        pass

    def test_response_to_message(self):
        pass

    def test_sent_message(self):
        pass


class TestQueue(unittest.TestCase):
    """Tests for the Queue class"""

    def setUp(self):
        self.q = myqueue.Queue()
        self.q.push('first')
        self.q.push('second')
        self.q.push('last')

        self.empty_q = myqueue.Queue()

    def test_queue(self):
        self.assertIsInstance(self.q._list, myqueue.LinkedList)
        self.assertIsInstance(self.q.emoji, set)

    def test_queue_push(self):
        self.q.push('another last')
        self.assertEqual(self.q._list.head.data, 'first')
        self.assertEqual(self.q._list.tail.data, 'another last')

    def test_queue_remove(self):
        self.q.remove('none')
        self.assertEqual(self.q._list.head.data, 'first')
        self.assertEqual(self.q._list.tail.data, 'last')

        self.q.remove('first')
        self.assertEqual(self.q._list.head.data, 'second')
        self.assertEqual(self.q._list.tail.data, 'last')

    def test_queue_pop(self):
        self.assertEqual(self.q._list.head.data, 'first')
        self.q.pop()
        self.assertEqual(self.q._list.head.data, 'second')

        self.assertIsNone(self.empty_q._list.head)
        self.empty_q.pop()
        self.assertIsNone(self.empty_q._list.head)

    def test_queue_peek(self):
        self.assertIsNone(self.empty_q.peek())
        self.assertEqual(self.q.peek(), 'first')

    def test_queue_has_user(self):
        found_none = self.q.has_user('none')
        self.assertFalse(found_none)

        found_second = self.q.has_user('second')
        self.assertTrue(found_second)

    def test_queue_is_empty(self):
        self.assertTrue(self.empty_q.is_empty())
        self.assertFalse(self.q.is_empty())

    def test_queue_empty(self):
        self.assertIsNotNone(self.q._list.head)

        self.q.empty()
        self.assertIsNone(self.q._list.head)

    def test_queue_override(self):
        self.q.override(['a', 'b', 'c'])
        self.assertEqual(self.q._list.head.data, 'a')
        self.assertEqual(self.q._list.tail.data, 'c')

        self.q.override([])
        self.assertTrue(self.q.is_empty())

    def test_queue_str(self):
        str_q = str(self.q)
        self.assertEqual(str_q, "QUEUE = [ first second last ]")

        self.empty_q.emoji = ['only']
        empty_str_q = str(self.empty_q)
        self.assertEqual(empty_str_q, "QUEUE = [ :only: ]")


class TestLinkedList(unittest.TestCase):
    """Tests for the Linked List (and Node) class"""

    def setUp(self):
        self.ll = myqueue.LinkedList()
        self.ll.append('a')
        self.ll.append('b')
        self.ll.append('c')
        self.ll.append('d')

        self.empty_ll = myqueue.LinkedList()

    def test_node(self):
        berry_node = myqueue.Node("berry")
        apple_node = myqueue.Node("apple", berry_node)
        self.assertEqual(apple_node.data, "apple")
        self.assertEqual(berry_node.data, "berry")

        self.assertIs(apple_node.next, berry_node)
        self.assertIsNone(berry_node.next)

    def test_linked_list(self):
        self.assertIsInstance(self.ll.head, myqueue.Node)

        self.assertIsNone(self.empty_ll.head)
        self.assertIsNone(self.empty_ll.tail)

    def test_ll_append(self):
        self.empty_ll.append('a')
        self.assertIs(self.empty_ll.head, self.empty_ll.tail)
        self.assertEqual(self.empty_ll.head.data, 'a')

        self.empty_ll.append('b')
        self.assertIsNot(self.empty_ll.head, self.empty_ll.tail)
        self.assertEqual(self.empty_ll.tail.data, 'b')

    def test_ll_remove(self):
        found_none = self.ll.remove('empty')
        # a -> b -> c -> d
        self.assertIsNone(found_none)

        found_mid = self.ll.remove('b')
        # a -> c -> d
        self.assertEqual(found_mid.data, 'b')
        self.assertEqual(self.ll.head.data, 'a')
        self.assertIs(self.ll.head.next.data, 'c')

        found_head = self.ll.remove('a')
        # c -> d
        self.assertEqual(found_head.data, 'a')
        self.assertEqual(self.ll.head.data, 'c')
        self.assertEqual(self.ll.head.next.data, 'd')

        found_tail = self.ll.remove('d')
        # c
        self.assertEqual(found_tail.data, 'd')
        self.assertEqual(self.ll.tail.data, 'c')

        found_only = self.ll.remove('c')
        self.assertEqual(found_only.data, 'c')
        self.assertIsNone(self.ll.head)
        self.assertIsNone(self.ll.tail)

    def test_ll_find(self):
        found_none = self.ll.find('x')
        self.assertFalse(found_none)

        found_a = self.ll.find('a')
        self.assertTrue(found_a)

    def test_ll_all(self):
        empty = [node for node in self.empty_ll.all()]
        self.assertEqual(empty, [])

        full = [node for node in self.ll.all()]
        self.assertEqual(len(full), 4)
        self.assertIs(full[0], self.ll.head)
        self.assertIs(full[-1], self.ll.tail)

    def test_ll_repr(self):
        self.assertEqual(repr(self.empty_ll), "<Linked List: head=None tail=None>")

        self.assertEqual(repr(self.ll), "<Linked List: head=a tail=d>")


class TestParsing(unittest.TestCase):
    """Tests for parsing helper functions"""

    def test_is_enqueue_message(self):
        enqueue_text = "Enqueue"
        self.assertTrue(parsing.is_enqueue_message(enqueue_text), msg=f"Text: {enqueue_text}")

        nqueue_text = "nqueue me~"
        self.assertTrue(parsing.is_enqueue_message(nqueue_text), msg=f"Text: {nqueue_text}")

        enq_text = "   enq me please"
        self.assertTrue(parsing.is_enqueue_message(enq_text), msg=f"Text: {enq_text}")

        nq_text = "nq me"
        self.assertTrue(parsing.is_enqueue_message(nq_text), msg=f"Text: {nq_text}")

        with_feeling = "ENQ!!!"
        self.assertTrue(parsing.is_enqueue_message(with_feeling), msg=f"Text: {with_feeling}")

        empty_text = ""
        self.assertFalse(parsing.is_enqueue_message(empty_text),  msg=f"Text: {empty_text}")

        mid_text = "I have enqueue in the message, but not at the start"
        self.assertFalse(parsing.is_enqueue_message(mid_text),  msg=f"Text: {mid_text}")

        boundarytext = "enqueueis at the start, but without a word boundary"
        self.assertFalse(parsing.is_enqueue_message(boundarytext),  msg=f"Text: {boundarytext}")

    def test_is_dequeue_message(self):
        dequeue_text = "Dequeue"
        self.assertTrue(parsing.is_dequeue_message(dequeue_text), msg=f"Text: {dequeue_text}")

        dqueue_text = "dqueue dairy queen"
        self.assertTrue(parsing.is_dequeue_message(dqueue_text), msg=f"Text: {dqueue_text}")

        deq_text = "   deq me please thx"
        self.assertTrue(parsing.is_dequeue_message(deq_text), msg=f"Text: {deq_text}")

        dq_text = "dq <@U12345678>"
        self.assertTrue(parsing.is_dequeue_message(dq_text), msg=f"Text: {dq_text}")

        omw_text = "OMW <@U12345678>!"
        self.assertTrue(parsing.is_dequeue_message(omw_text), msg=f"Text: {omw_text}")

        with_feeling = "DQ!!!"
        self.assertTrue(parsing.is_dequeue_message(with_feeling), msg=f"Text: {with_feeling}")

        empty_text = ""
        self.assertFalse(parsing.is_dequeue_message(empty_text),  msg=f"Text: {empty_text}")

        mid_text = "I have dequeue in the message, but not at the start"
        self.assertFalse(parsing.is_dequeue_message(mid_text),  msg=f"Text: {mid_text}")

        boundarytext = "dequeueis at the start, but without a word boundary"
        self.assertFalse(parsing.is_dequeue_message(boundarytext),  msg=f"Text: {boundarytext}")

    def test_get_user_to_pop(self):
        omw_text = "OMW <@U12345678>!"
        user = parsing.get_user_to_pop(omw_text)
        self.assertEqual(user, '<@U12345678>', msg=f"Text: {omw_text}")

        tiny_user_text = "<@x>"
        tiny_user = parsing.get_user_to_pop(tiny_user_text)
        self.assertEqual(tiny_user, '<@x>', msg=f"Text: {tiny_user_text}")

        first_user_text = "<@x123> <@y456>"
        first_user = parsing.get_user_to_pop(first_user_text)
        self.assertEqual(first_user, '<@x123>', msg=f"Text: {first_user_text}")

        no_user_text = "these are not the users you're looking for"
        no_user = parsing.get_user_to_pop(no_user_text)
        self.assertIsNone(no_user, msg=f"Text: {no_user_text}")

        ghost_user_text = "<@     > (boo)"
        spooky = parsing.get_user_to_pop(ghost_user_text)
        self.assertIsNone(spooky, msg=f"Text: {ghost_user_text}")

    def test_get_queue_change(self):
        empty_queue_text = "QUEUE.empty()"
        empty_queue = parsing.get_queue_change(empty_queue_text)
        self.assertEqual(empty_queue, [], msg=f"Text: {empty_queue_text}")

        clear_queue_text = "Q.CLear(    )"
        clear_queue = parsing.get_queue_change(clear_queue_text)
        self.assertEqual(clear_queue, [], msg=f"Text: {clear_queue_text}")

        new_queue_text = "q=[]"
        new_queue = parsing.get_queue_change(new_queue_text)
        self.assertEqual(new_queue, [], msg=f"Text: {new_queue_text}")

        spacy_new_queue_text = "   queue    =   [         ]"
        spacy_new_queue = parsing.get_queue_change(spacy_new_queue_text)
        self.assertEqual(spacy_new_queue, [], msg=f"Text: {spacy_new_queue_text}")

        construct_queue_text = "Queue = [ <@U1234> <@xyz>   ]"
        construct_queue = parsing.get_queue_change(construct_queue_text)
        self.assertEqual(construct_queue, ['<@U1234>', '<@xyz>'], msg=f"Text: {construct_queue_text}")

        typo_queue_text = "Queue = [ <@U1234> <@xyz> typo ]"
        typo_queue = parsing.get_queue_change(typo_queue_text)
        self.assertIsNone(typo_queue, msg=f"Text: {typo_queue_text}")

        fake_queue_text = "Queue = <@fake> <@wrong>"
        fake_queue = parsing.get_queue_change(fake_queue_text)
        self.assertIsNone(fake_queue, msg=f"Text: {fake_queue_text}")

    def test_is_help_message(self):
        q_help_text = "qbot!! help!!"
        self.assertTrue(parsing.is_help_message(q_help_text), msg=f"Text: {q_help_text}")

        queue_help_text = "  QUEUEbot come help me thx"
        self.assertTrue(parsing.is_help_message(queue_help_text), msg=f"Text: {queue_help_text}")

        rescue_text = "queuebot to the rescue"
        self.assertFalse(parsing.is_help_message(rescue_text), msg=f"Text: {rescue_text}")

        mid_text = "i hope qbot will help me"
        self.assertFalse(parsing.is_help_message(mid_text), msg=f"Text: {mid_text}")

        boundarytext = "qbot is a helpful dood"
        self.assertFalse(parsing.is_help_message(boundarytext), msg=f"Text: {boundarytext}")

    def test_is_status_message(self):
        qbot_status_text = "qbot!! status!!"
        self.assertTrue(parsing.is_status_message(qbot_status_text), msg=f"Text: {qbot_status_text}")

        queuebot_status_text = "QUEUEbot give me that status thx"
        self.assertTrue(parsing.is_status_message(queuebot_status_text), msg=f"Text: {queuebot_status_text}")

        q_status_text = "q  status?"
        self.assertTrue(parsing.is_status_message(q_status_text), msg=f"Text: {q_status_text}")

        queue_status_text = "  queue status please!!"
        self.assertTrue(parsing.is_status_message(queue_status_text), msg=f"Text: {queue_status_text}")

        stats_text = "queuebot give me the stats"
        self.assertFalse(parsing.is_status_message(stats_text), msg=f"Text: {stats_text}")

        mid_text = "i hope qbot update its status"
        self.assertFalse(parsing.is_status_message(mid_text), msg=f"Text: {mid_text}")

        boundarytext = "q is a statusupdating thing"
        self.assertFalse(parsing.is_status_message(boundarytext), msg=f"Text: {boundarytext}")



if __name__ == "__main__":
    unittest.main()
