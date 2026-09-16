class CustomGraph:
    def __init__(self):
        self.adj = {}

    def add_edge(self, u, v, weight):
        if u not in self.adj:
            self.adj[u] = []
        if v not in self.adj:
            self.adj[v] = []
        self.adj[u].append((v, weight))
        self.adj[v].append((u, weight))

    def bfs(self, start_node):
        visited = []
        queue = [start_node]
        visited.append(start_node)
        while queue:
            curr = queue.pop(0)
            for neighbor, _ in self.adj.get(curr, []):
                if neighbor not in visited:
                    visited.append(neighbor)
                    queue.append(neighbor)
        return visited

    def dijkstra(self, start, end):
        distances = {node: float('inf') for node in self.adj}
        previous = {node: None for node in self.adj}
        distances[start] = 0
        unvisited = [node for node in self.adj]

        while unvisited:
            # Cari node jarak terkecil
            current = None
            min_dist = float('inf')
            for node in unvisited:
                if distances[node] < min_dist:
                    min_dist = distances[node]
                    current = node

            if current is None or current == end:
                break

            unvisited.remove(current)

            for neighbor, weight in self.adj.get(current, []):
                if neighbor in unvisited:
                    new_dist = distances[current] + weight
                    if new_dist < distances[neighbor]:
                        distances[neighbor] = new_dist
                        previous[neighbor] = current

        path = []
        curr = end
        while curr:
            path.insert(0, curr)
            curr = previous[curr]

        return distances[end], path