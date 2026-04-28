from hex_tile import HexTile


class HexNode:
    """
    Represents a single hexagonal cell in axial coordinates (q, r).
    This can be one of a set of possible tiles.
    """

    def __init__(self, q: int, r: int, s: int | None = None,
                 possible_tiles: set[HexTile] | None = None):
        self.q = q
        self.r = r
        self.s = s if s is not None else -q - r

        if self.q + self.r + self.s != 0:
            raise ValueError(f"Invalid hex coordinates: q+r+s must equal 0")

        self.possible_tiles: set[HexTile] = possible_tiles if possible_tiles is not None else set()

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

    def __eq__(self, other: object) -> bool:
        return isinstance(other, HexNode) and self.q == other.q and self.r == other.r

    def __hash__(self) -> int:
        return hash((self.q, self.r))

    def __repr__(self) -> str:
        return f"HexNode(q={self.q}, r={self.r}, s={self.s})"
