import random
from src.hex_map import HexMap
from src.hex_tile import HexTile


def random_selector(node, tiles):
    """Randomly shuffle tile candidates for stochastic map generation."""
    lst = list(tiles)
    random.shuffle(lst)
    return lst


def main():
    tile_set = (
        HexTile.rotations("grass",         ["grass", "grass", "grass", "grass", "grass", "grass"]) |
        HexTile.rotations("water",         ["water", "water", "water", "water", "water", "water"]) |
        HexTile.rotations("road_end",      ["road",  "grass", "grass", "grass", "grass", "grass"]) |
        HexTile.rotations("road_bend",      ["road",  "road", "grass", "grass", "grass", "grass"]) |
        HexTile.rotations("road_straight", ["road",  "grass", "grass", "road",  "grass", "grass"]) |
        HexTile.rotations("river_end",      ["river",  "grass", "grass", "grass", "grass", "grass"]) |
        HexTile.rotations("river_bend",      ["river",  "river", "grass", "grass", "grass", "grass"]) |
        HexTile.rotations("river_straight", ["river",  "grass", "grass", "river",  "grass", "grass"]) |
        HexTile.rotations("coast_0",         ["coast", "grass", "grass", "grass", "grass", "coast"]) |
        HexTile.rotations("coast_1",         ["water", "coast", "grass", "grass", "grass", "coast"]) |
        HexTile.rotations("coast_2",         ["water", "water", "coast", "grass", "grass", "coast"]) |
        HexTile.rotations("coast_3",         ["water", "water", "water", "coast", "grass", "coast"]) |
        HexTile.rotations("coast_4",         ["water", "water", "water", "water", "coast", "coast"])
    )

    radius = 8
    hex_map = HexMap.hexagon(radius=radius, possible_tiles=tile_set)
    
    # Use random tile selection for more variety
    for node in hex_map.nodes:
        node.tile_selector = random_selector


    # Set the center to a specific tile to anchor the generation
    center = hex_map._node_map[(0, 0)]
    center.possible_tiles = {t for t in tile_set if t.name.startswith("grass")}
    # Set the edges to water to create a natural boundary
    for node in hex_map.nodes:
        if abs(node.q) == radius or abs(node.r) == radius or abs(node.q + node.r) == radius:
            node.possible_tiles = {t for t in tile_set if t.name.startswith("water")}



    print(f"Hexagon (radius={radius}): {hex_map}")
    solved = hex_map.collapse()
    print(f"Collapsed: {solved}")
    for node in hex_map.nodes:
        tile = next(iter(node.possible_tiles))
        print(f"  {node} -> {tile}")

    with open("map.json", "w") as f:
        f.write(hex_map.to_json())
    print("\nSaved map.json — open viewer.html to render it.")
    print(f"Hexagon (radius={radius}): {hex_map}")


if __name__ == "__main__":
    main()
