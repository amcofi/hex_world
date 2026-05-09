import json

from .hex_node import HexNode
from .hex_tile import HexTile

_DIRECTIONS = [(1, -1, 0), (1, 0, -1), (0, 1, -1), (-1, 1, 0), (-1, 0, 1), (0, -1, 1)]


def _edge_index_for_direction(direction: int) -> int:
    """Map a neighbor direction index to the tile edge index facing that neighbor.

    The renderer defines edge i as the segment from vertex i to vertex (i+1),
    with vertex 0 at angle 0deg (east) and increasing clockwise in screen space.
    Under that geometry, direction d faces edge (d - 1) mod 6.
    """
    return (direction - 1) % 6


class HexMap:
    """
    Represents a collection of HexNodes that form a map.
    """

    def __init__(self, nodes: list[HexNode]):
        self.nodes = nodes
        self._node_map: dict[tuple[int, int], HexNode] = {(n.q, n.r): n for n in nodes}

    @classmethod
    def hexagon(cls, radius: int, possible_tiles: set[HexTile] | None = None) -> "HexMap":
        """All nodes within `radius` steps of the origin."""
        nodes = [
            HexNode(q, r, possible_tiles=possible_tiles)
            for q in range(-radius, radius + 1)
            for r in range(max(-radius, -q - radius), min(radius, -q + radius) + 1)
        ]
        return cls(nodes)

    @classmethod
    def rectangle(cls, width: int, height: int, possible_tiles: set[HexTile] | None = None) -> "HexMap":
        """Rectangular grid using odd-row offset layout."""
        nodes = []
        for row in range(height):
            offset = -(row // 2)
            for col in range(width):
                q = col + offset
                r = row
                nodes.append(HexNode(q, r, possible_tiles=possible_tiles))
        return cls(nodes)

    def _find_min_entropy(self) -> HexNode | None:
        candidates = [n for n in self.nodes if len(n.possible_tiles) > 1]
        return min(candidates, key=lambda n: len(n.possible_tiles), default=None)

    def _propagate(self, start: HexNode) -> bool:
        """BFS arc-consistency from start. Returns False on contradiction."""
        queue = [start]
        while queue:
            node = queue.pop()
            for d, (dq, dr, _) in enumerate(_DIRECTIONS):
                neighbor = self._node_map.get((node.q + dq, node.r + dr))
                if not neighbor:
                    continue
                edge_idx = _edge_index_for_direction(d)
                allowed_edge_labels = {t.edges[edge_idx] for t in node.possible_tiles}
                opp = (d + 3) % 6
                opp_edge_idx = _edge_index_for_direction(opp)
                before_tiles = neighbor.possible_tiles
                has_possible_tiles = neighbor.constrain_to_edge_labels(opp_edge_idx, allowed_edge_labels)
                if not has_possible_tiles:
                    return False
                if neighbor.possible_tiles != before_tiles:
                    queue.append(neighbor)
        return True

    def collapse(self) -> bool:
        """
        WFC: collapses all nodes to a single tile each.

        Each node supplies its own ordered tile options via ``node.select_tiles()``.
        That per-node selector can reorder tiles stochastically or return only a
        subset of the current possibilities, which makes it possible to bias or
        constrain different regions of the map differently.

        Returns True on success, False if the tile set has no valid solution.
        """
        def save() -> dict[HexNode, set[HexTile]]:
            return {n: set(n.possible_tiles) for n in self.nodes}

        def restore(snapshot: dict[HexNode, set[HexTile]]) -> None:
            for n, tiles in snapshot.items():
                n.possible_tiles = tiles

        def try_from(node: HexNode, start_n: int,
                     snapshot: dict[HexNode, set[HexTile]],
                     ordered: list[HexTile]) -> int:
            """Try ordered[start_n:] for node, restoring snapshot after each failure.
            Returns the index of the first successful option, or -1 if all fail."""
            for n in range(start_n, len(ordered)):
                node.possible_tiles = {ordered[n]}
                if self._propagate(node):
                    return n
                restore(snapshot)
            return -1

        stack: list[tuple[HexNode, int, dict[HexNode, set[HexTile]], list[HexTile]]] = []

        while True:
            node = self._find_min_entropy()
            if node is None:
                return True

            snapshot = save()
            ordered = node.select_tiles()
            n = try_from(node, 0, snapshot, ordered)

            if n >= 0:
                stack.append((node, n, snapshot, ordered))
                continue

            # All options exhausted — backtrack
            while stack:
                node, prev_n, snapshot, ordered = stack.pop()
                restore(snapshot)
                n = try_from(node, prev_n + 1, snapshot, ordered)
                if n >= 0:
                    stack.append((node, n, snapshot, ordered))
                    break
            else:
                return False

    def to_json(self) -> str:
        """Serialise the map to JSON.

        Each node carries its cube coordinates and, if collapsed, its tile's
        name, rotation, and edges.  Uncollapsed nodes have ``"tile": null``.
        """
        nodes = []
        for node in self.nodes:
            tile_data = node.tile_json()
            nodes.append({"q": node.q, "r": node.r, "s": node.s, "tile": tile_data})
        return json.dumps({"nodes": nodes}, indent=2)

    def __len__(self) -> int:
        return len(self.nodes)

    def __repr__(self) -> str:
        return f"HexMap({len(self.nodes)} nodes)"