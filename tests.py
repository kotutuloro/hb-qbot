import unittest

import qbot
import myqueue
import parsing


class TestQbot(unittest.TestCase):
    """Tests for the QBot"""
    pass


class TestQueue(unittest.TestCase):
    """Tests for the Queue and related classes"""
    pass


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
