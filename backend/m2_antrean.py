class CustomStack:
    def __init__(self):
        self.items = []

    def push(self, val):
        self.items.append(val)

    def pop(self):
        if len(self.items) == 0:
            return None
        return self.items.pop()

    def peek(self):
        if len(self.items) == 0:
            return None
        return self.items[-1]

    def is_empty(self):
        return len(self.items) == 0

    def clear(self):
        self.items = []

    def size(self):
        return len(self.items)

    def to_string(self):
        if len(self.items) == 0:
            return "kosong"
        return " ".join([str(x) for x in self.items])


class NaiveQueue:
    """Antrean naif di atas larik biasa: dequeue memakai pop(0) sehingga menggeser sisa elemen O(n)."""
    def __init__(self):
        self.data = []
        self.total_geseran = 0

    def enqueue(self, val):
        self.data.append(val)
        return True

    def dequeue(self):
        if len(self.data) == 0:
            return None, 0
        geseran = len(self.data) - 1
        val = self.data.pop(0)
        self.total_geseran += geseran
        return val, geseran

    def pop_back(self):
        """Untuk keperluan UNDO enqueue: keluarkan dari belakang."""
        if len(self.data) == 0:
            return None
        return self.data.pop()

    def prepend_batch(self, items):
        """Untuk keperluan UNDO dequeue: kembalikan daftar pesanan ke DEPAN antrean."""
        self.data = list(items) + self.data

    def size(self):
        return len(self.data)


class CircularQueue:
    """Antrean melingkar: hanya penunjuk front dan rear yang bergerak O(1) dengan modulo."""
    def __init__(self, capacity=32768):
        self.capacity = capacity
        self.queue = [None] * capacity
        self.front = 0
        self.rear = 0
        self.count = 0

    def _grow(self):
        new_cap = self.capacity * 2
        new_q = [None] * new_cap
        for i in range(self.count):
            new_q[i] = self.queue[(self.front + i) % self.capacity]
        self.queue = new_q
        self.front = 0
        self.rear = self.count
        self.capacity = new_cap

    def enqueue(self, val):
        if self.count == self.capacity:
            self._grow()
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

    def pop_back(self):
        """Untuk keperluan UNDO enqueue: keluarkan elemen paling belakang."""
        if self.count == 0:
            return None
        self.rear = (self.rear - 1 + self.capacity) % self.capacity
        val = self.queue[self.rear]
        self.queue[self.rear] = None
        self.count -= 1
        return val

    def prepend_batch(self, items):
        """Untuk keperluan UNDO dequeue: kembalikan daftar pesanan ke DEPAN antrean."""
        while self.count + len(items) > self.capacity:
            self._grow()
        for item in reversed(items):
            self.front = (self.front - 1 + self.capacity) % self.capacity
            self.queue[self.front] = item
            self.count += 1

    def size(self):
        return self.count


# --- BAGIAN A(1): MESIN KASIR INFIX KE POSTFIX DAN EVALUASI ---

def pecah_token(ekspresi):
    tokens = []
    angka = ""
    for ch in ekspresi:
        if ch in "0123456789":
            angka += ch
        else:
            if angka != "":
                tokens.append(angka)
                angka = ""
            if ch in "+-*/()":
                tokens.append(ch)
    if angka != "":
        tokens.append(angka)
    return tokens

def prioritas_op(op):
    if op == "*" or op == "/":
        return 2
    if op == "+" or op == "-":
        return 1
    return 0

def ke_postfix(ekspresi):
    tokens = pecah_token(ekspresi)
    stack = CustomStack()
    keluaran = []
    langkah_log = []
    step_no = 1

    for tok in tokens:
        if tok[0] in "0123456789":
            keluaran.append(tok)
            langkah_log.append((f"1.{step_no}", tok, "operand, langsung ke output", stack.to_string(), " ".join(keluaran)))
        elif tok == "(":
            stack.push(tok)
            langkah_log.append((f"1.{step_no}", tok, "push ( ke stack", stack.to_string(), " ".join(keluaran)))
        elif tok == ")":
            while not stack.is_empty() and stack.peek() != "(":
                keluaran.append(stack.pop())
            stack.pop()  # Buang '('
            langkah_log.append((f"1.{step_no}", tok, "pop sampai (, lalu buang (", stack.to_string(), " ".join(keluaran)))
        else:
            popped_ops = []
            while (not stack.is_empty() and stack.peek() != "(" and
                   prioritas_op(stack.peek()) >= prioritas_op(tok)):
                popped_ops.append(stack.pop())
                keluaran.append(popped_ops[-1])
            stack.push(tok)
            if len(popped_ops) > 0:
                aksi = f"pop {' '.join(popped_ops)}, lalu push {tok}"
            else:
                aksi = f"push {tok}"
            langkah_log.append((f"1.{step_no}", tok, aksi, stack.to_string(), " ".join(keluaran)))
        step_no += 1

    sisa = []
    while not stack.is_empty():
        op = stack.pop()
        sisa.append(op)
        keluaran.append(op)
    langkah_log.append(("1.akhir", "-", f"pop sisa stack: {' '.join(sisa) if sisa else '-'}", stack.to_string(), " ".join(keluaran)))

    return keluaran, langkah_log

def hitung_postfix(postfix_tokens):
    stack = CustomStack()
    langkah_log = []
    step_no = 1

    for tok in postfix_tokens:
        if tok[0] in "0123456789":
            stack.push(int(tok))
            langkah_log.append((f"2.{step_no}", tok, f"operand, push {tok}", stack.to_string(), "-"))
        else:
            b = stack.pop()  # Operand kanan keluar lebih dulu
            a = stack.pop()  # Operand kiri
            if b is None or a is None:
                return 0, langkah_log
            if tok == "+":
                res = a + b
            elif tok == "-":
                res = a - b
            elif tok == "*":
                res = a * b
            elif tok == "/":
                res = a // b if b != 0 else 0
            else:
                res = 0
            stack.push(res)
            langkah_log.append((f"2.{step_no}", tok, f"pop {b} dan {a} -> {a} {tok} {b} = {res}", stack.to_string(), str(res)))
        step_no += 1

    total = stack.pop() if not stack.is_empty() else 0
    return total, langkah_log
