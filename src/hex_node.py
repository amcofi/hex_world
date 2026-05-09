from collections.abc import Callable

from .hex_tile import HexTile


class HexNode:
    """
    Represents a single hexagonal cell in axial coordinates (q, r).
    This can be one of a set of possible tiles.
    """

    def __init__(self, q: int, r: int, s: int | None = None,
                 possible_tiles: set[HexTile] | None = None,
                 tile_selector: Callable[["HexNode", set[HexTile]], list[HexTile]] | None = None):
        self.q = q
        self.r = r
        self.s = s if s is not None else -q - r

        if self.q + self.r + self.s != 0:
            raise ValueError(f"Invalid hex coordinates: q+r+s must equal 0")

        self.possible_tiles: set[HexTile] = possible_tiles if possible_tiles is not None else set()
        self.tile_selector = tile_selector or self.default_tile_selector

    @property
    def collapsed(self) -> bool:
        return len(self.possible_tiles) == 1

    def neighbors(self) -> list["HexNode"]:
        directions = [(1, -1, 0), (1, 0, -1), (0, 1, -1),
                      (-1, 1, 0), (-1, 0, 1), (0, -1, 1)]
        return [HexNode(self.q + dq, self.r + dr, self.s + ds)
                for dq, dr, ds in directions]

    def distance(self, other: "HexNode") -> int:
        return max(abs(self.q - other.q), abs(self.r - other.r), abs(self.s - other.s))

    @staticmethod
    def default_tile_selector(node: "HexNode", tiles: set[HexTile]) -> list[HexTile]:
        return sorted(tiles, key=hash)

    def select_tiles(self) -> list[HexTile]:
        """Return the ordered tile candidates for this node.

        The selector may reorder tiles stochastically or return a subset to
        constrain this node differently from the rest of the map.
        """
        return list(self.tile_selector(self, self.possible_tiles))

    def constrain_to_edge_labels(self, side_index: int, allowed_edge_labels: set[str]) -> bool:
        """Keep only tiles whose edge at ``side_index`` is allowed.

        Returns True if at least one tile remains after filtering.
        """
        self.possible_tiles = {
            tile for tile in self.possible_tiles
            if tile.edges[side_index] in allowed_edge_labels
        }
        return bool(self.possible_tiles)

    def tile_json(self) -> dict[str, object] | None:
        """Return the JSON-ready representation of the collapsed tile."""
        if not self.collapsed:
            return {
                "name": "unknown",
                "rotation": 0,
            }

        tile = next(iter(self.possible_tiles))
        return {
            "name": tile.name,
            "rotation": tile.rotation,
            "edges": list(tile.edges),
        }

    def __eq__(self, other: object) -> bool:
        return isinstance(other, HexNode) and self.q == other.q and self.r == other.r

    def __hash__(self) -> int:
        return hash((self.q, self.r))

    def __repr__(self) -> str:
        return f"HexNode(q={self.q}, r={self.r}, s={self.s})"