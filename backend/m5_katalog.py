class BSTNode:
    def __init__(self, harga, menu):
        self.harga = harga
        self.menus = [menu]
        self.left = None
        self.right = None

class KatalogBST:
    def __init__(self):
        self.root = None

    def insert(self, harga, menu):
        self.root = self._insert(self.root, harga, menu)

    def _insert(self, node, harga, menu):
        if not node:
            return BSTNode(harga, menu)
        if harga == node.harga:
            node.menus.append(menu)
        elif harga < node.harga:
            node.left = self._insert(node.left, harga, menu)
        else:
            node.right = self._insert(node.right, harga, menu)
        return node

    def range_search(self, min_h, max_h):
        res = []
        self._range_search(self.root, min_h, max_h, res)
        return res

    def _range_search(self, node, min_h, max_h, res):
        if not node:
            return
        if min_h < node.harga:
            self._range_search(node.left, min_h, max_h, res)
        if min_h <= node.harga <= max_h:
            for m in node.menus:
                res.append((node.harga, m))
        if max_h > node.harga:
            self._range_search(node.right, min_h, max_h, res)

class MinHeapPriority:
    def __init__(self):
        self.heap = []

    def push(self, priority, item):
        self.heap.append((priority, item))
        self._up(len(self.heap) - 1)

    def pop(self):
        if not self.heap:
            return None
        if len(self.heap) == 1:
            return self.heap.pop()
        root = self.heap[0]
        self.heap[0] = self.heap.pop()
        self._down(0)
        return root

    def _up(self, i):
        while i > 0:
            p = (i - 1) // 2
            if self.heap[i][0] < self.heap[p][0]:
                self.heap[i], self.heap[p] = self.heap[p], self.heap[i]
                i = p
            else:
                break

    def _down(self, i):
        n = len(self.heap)
        while 2 * i + 1 < n:
            left = 2 * i + 1
            right = 2 * i + 2
            smallest = left
            if right < n and self.heap[right][0] < self.heap[left][0]:
                smallest = right
            if self.heap[smallest][0] < self.heap[i][0]:
                self.heap[i], self.heap[smallest] = self.heap[smallest], self.heap[i]
                i = smallest
            else:
                break