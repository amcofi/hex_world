from hex_map import HexMap
from hex_tile import HexTile


def main():
    tile_set = (
        HexTile.rotations("plain",         ["grass", "grass", "grass", "grass", "grass", "grass"]) |
        HexTile.rotations("road_end",      ["road",  "grass", "grass", "grass", "grass", "grass"]) |
        HexTile.rotations("road_straight", ["road",  "grass", "grass", "road",  "grass", "grass"])
    )

    hex_map = HexMap.hexagon(radius=2, possible_tiles=tile_set)
    print(f"Hexagon (radius=2): {hex_map}")
    solved = hex_map.collapse()
    print(f"Collapsed: {solved}")
    for node in hex_map.nodes:
        tile = next(iter(node.possible_tiles))
        print(f"  {node} -> {tile}")

    with open("map.json", "w") as f:
        f.write(hex_map.to_json())
    print("\nSaved map.json — open viewer.html to render it.")


if __name__ == "__main__":
    main()
