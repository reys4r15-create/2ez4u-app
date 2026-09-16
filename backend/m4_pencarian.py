class HashNode:
    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.next = None

class CustomHashTable:
    def __init__(self, capacity=10007):
        self.capacity = capacity
        self.buckets = [None] * capacity

    def _hash(self, key):
        h = 0
        for char in str(key):
            h = (h * 31 + ord(char)) % self.capacity
        return h

    def put(self, key, value):
        idx = self._hash(key)
        head = self.buckets[idx]
        curr = head
        while curr:
            if curr.key == key:
                curr.value = value
                return
            curr = curr.next
        new_node = HashNode(key, value)
        new_node.next = head
        self.buckets[idx] = new_node

    def get(self, key):
        idx = self._hash(key)
        curr = self.buckets[idx]
        while curr:
            if curr.key == key:
                return curr.value
            curr = curr.next
        return None

def merge_sort_by_time(arr):
    if len(arr) <= 1:
        return arr
    mid = len(arr) // 2
    left = merge_sort_by_time(arr[:mid])
    right = merge_sort_by_time(arr[mid:])

    result = []
    i = j = 0
    while i < len(left) and j < len(right):
        t_left = int(left[i][6]) if left[i][6] else 0
        t_right = int(right[j][6]) if right[j][6] else 0
        if t_left <= t_right:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    while i < len(left):
        result.append(left[i])
        i += 1
    while j < len(right):
        result.append(right[j])
        j += 1
    return result