"""Disjoint Set Union (Union-Find) with path compression and rank optimization."""

class UnionFind:
    """Disjoint Set Union data structure for common-input Bitcoin wallet clustering."""

    def __init__(self):
        self.parent: dict[str, str] = {}
        self.rank: dict[str, int] = {}
        self.sizes: dict[str, int] = {}

    def find(self, item: str) -> str:
        """Find root representative with recursive path compression."""
        if item not in self.parent:
            self.parent[item] = item
            self.rank[item] = 0
            self.sizes[item] = 1
            return item

        # Path compression
        path = []
        curr = item
        while self.parent[curr] != curr:
            path.append(curr)
            curr = self.parent[curr]

        for node in path:
            self.parent[node] = curr

        return curr

    def union(self, item1: str, item2: str) -> bool:
        """Union two sets by rank. Returns True if sets were merged, False if already connected."""
        root1 = self.find(item1)
        root2 = self.find(item2)

        if root1 == root2:
            return False

        # Union by rank
        if self.rank[root1] < self.rank[root2]:
            self.parent[root1] = root2
            self.sizes[root2] += self.sizes[root1]
        elif self.rank[root1] > self.rank[root2]:
            self.parent[root2] = root1
            self.sizes[root1] += self.sizes[root2]
        else:
            self.parent[root2] = root1
            self.rank[root1] += 1
            self.sizes[root1] += self.sizes[root2]

        return True

    def get_clusters(self) -> dict[str, list[str]]:
        """Return all clusters mapped from root representative to list of member wallets."""
        clusters: dict[str, list[str]] = {}
        for item in list(self.parent.keys()):
            root = self.find(item)
            if root not in clusters:
                clusters[root] = []
            clusters[root].append(item)
        return clusters

    def cluster_size(self, item: str) -> int:
        root = self.find(item)
        return self.sizes.get(root, 1)
