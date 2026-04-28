class HexTile:
    """
    Represents a hexagonal tile with specific edge types.
    """

    def __init__(self, edges: list[str], name: str = "", rotation: int = 0):
        if len(edges) != 6:
            raise ValueError("HexTile requires exactly 6 edges")
        self.edges = tuple(edges)
        self.name = name
        self.rotation = rotation

    def __eq__(self, other: object) -> bool:
        return isinstance(other, HexTile) and self.edges == other.edges

    def __hash__(self) -> int:
        return hash(self.edges)

    @classmethod
    def rotations(cls, name: str, edges: list[str]) -> set["HexTile"]:
        """Return the set of all rotationally unique variants of a tile.

        Each variant is a left-rotation of `edges` by r steps (r = 0..5).
        Symmetric tiles (e.g. all-grass) produce fewer than 6 results because
        duplicate edge configs are deduplicated via __eq__/__hash__.
        """
        result: set[HexTile] = set()
        for r in range(6):
            result.add(cls(edges=edges[r:] + edges[:r], name=name, rotation=r))
        return result

    def __repr__(self) -> str:
        return f"HexTile(name={self.name!r}, rotation={self.rotation}, edges={list(self.edges)})"
