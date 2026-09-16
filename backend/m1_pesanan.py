class Node:
    def __init__(self, data):
        self.data = data
        self.next = None

class CustomArray:
    def __init__(self):
        self.data = []

    def append(self, val):
        self.data.append(val)

    def insert(self, idx, val):
        self.data.insert(idx, val)

    def remove_at(self, idx):
        if 0 <= idx < len(self.data):
            return self.data.pop(idx)
        return None

    def get(self, idx):
        if 0 <= idx < len(self.data):
            return self.data[idx]
        return None

    def size(self):
        return len(self.data)

class CustomLinkedList:
    def __init__(self):
        self.head = None
        self._size = 0

    def append(self, val):
        new_node = Node(val)
        if not self.head:
            self.head = new_node
        else:
            curr = self.head
            while curr.next:
                curr = curr.next
            curr.next = new_node
        self._size += 1

    def insert_head(self, val):
        new_node = Node(val)
        new_node.next = self.head
        self.head = new_node
        self._size += 1

    def insert_at(self, idx, val):
        if idx <= 0:
            self.insert_head(val)
            return
        if idx >= self._size:
            self.append(val)
            return
        new_node = Node(val)
        curr = self.head
        for _ in range(idx - 1):
            curr = curr.next
        new_node.next = curr.next
        curr.next = new_node
        self._size += 1

    def remove_at(self, idx):
        if not self.head or idx < 0 or idx >= self._size:
            return None
        if idx == 0:
            val = self.head.data
            self.head = self.head.next
            self._size -= 1
            return val
        curr = self.head
        for _ in range(idx - 1):
            curr = curr.next
        val = curr.next.data
        curr.next = curr.next.next
        self._size -= 1
        return val

    def size(self):
        return self._size