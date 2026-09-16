class CircularQueue:
    def __init__(self, capacity=1000):
        self.capacity = capacity
        self.queue = [None] * capacity
        self.front = 0
        self.rear = 0
        self.count = 0

    def enqueue(self, val):
        if self.count == self.capacity:
            return False  # Full
        self.queue[self.rear] = val
        self.rear = (self.rear + 1) % self.capacity
        self.count += 1
        return True

    def dequeue(self):
        if self.count == 0:
            return None
        val = self.queue[self.front]
        self.queue[self.front] = None
        self.front = (self.front + 1) % self.capacity
        self.count -= 1
        return val

    def size(self):
        return self.count

class CustomStack:
    def __init__(self):
        self.items = []

    def push(self, val):
        self.items.append(val)

    def pop(self):
        if len(self.items) == 0:
            return None
        return self.items.pop()

    def is_empty(self):
        return len(self.items) == 0