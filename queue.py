"""Classes for the queue"""


class Node(object):
    """Node class for linked list elements"""

    def __init__(self, data, next_node=None):
        """Create a Node"""
        self.data = data
        self.next = next_node

    def __repr__(self):
        """Representation of a node"""
        return f"<Node data={self.data}>"


class LinkedList(object):
    """Linked list class"""

    def __init__(self, head=None):
        self.head = head
        self.tail = head

    def append(self, data):
        """Add new node with given data to end of linked list"""

        new_node = Node(data)

        if not self.head:
            self.head = new_node
        if self.tail:
            self.tail.next = new_node
        self.tail = new_node

    def remove(self, value):
        """Remove and return node with matching data from linked list"""

        prev = None
        curr = self.head

        while curr:
            if curr.data == value:
                if curr is self.head:
                    self.head = curr.next
                else:
                    prev.next = curr.next
                if curr is self.tail:
                    self.tail = prev
                return curr
            prev = curr
            curr = curr.next

        return None

    def find(self, value):
        """Return whether node with matching data is in linked list"""

        curr = self.head:
        while curr:
            if curr.data == value:
                return True
            curr = curr.next
        return False

    def __repr__(self):
        """Representation of the queue"""

        if self.head:
            return f"<Linked List: head={self.head.data} tail={self.tail.data}>"
        else:
            return f"<Linked List: head={self.head} tail={self.tail}>"


class Queue(object):
    """Hackbright Queue class"""

    def __init__(self):
        self._list = LinkedList()

    def push(self):
        """Add an element to the end of the linked list"""
        pass

    def pop(self):
        """Remove the first element from the linked list"""
        pass

    def peek(self):
        """Return first element in queue without modifying linked list"""
        pass

    def is_empty(self):
        """Return boolean for whether the queue is empty"""
        pass

    def __repr__(self):
        """Representation of the queue"""
        return "<HB Queue>"

    def __str__(self):
        """String format for the queue"""
        return "I'll figure this out later"
