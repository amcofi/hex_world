import json
import math
import os

from hex_tile import HexTile

EDGE_COLORS: dict[str, str] = {
    "grass": "#6aaa52",
    "road":  "#b8a898",
}
DEFAULT_EDGE_COLOR = "#cccccc"
HEX_FILL   = "#e4d5b5"
HEX_STROKE = "#666666"
HEX_RADIUS = 72
EDGE_WIDTH  = 16
IMAGE_SIZE  = 180
OUTPUT_DIR  = "tiles"

# Edge i connects vertex[i] to vertex[(i+1)%6] of a flat-top hexagon.
# Vertices sit at i*60° clockwise from the right (0° = east in screen coords).
# This matches the _DIRECTIONS ordering in hex_map.py:
#   edge 0 → NE face  (between v0 and v1)
#   edge 1 → SE face  (between v1 and v2)
#   edge 2 → S face   (between v2 and v3)
#   edge 3 → SW face  (between v3 and v4)
#   edge 4 → NW face  (between v4 and v5)
#   edge 5 → N face   (between v5 and v0)


def _hex_vertices(cx: float, cy: float, r: float) -> list[tuple[float, float]]:
    return [
        (cx + r * math.cos(math.radians(i * 60)),
         cy + r * math.sin(math.radians(i * 60)))
        for i in range(6)
    ]


def render_svg(tile: HexTile) -> str:
    cx = cy = IMAGE_SIZE / 2
    verts = _hex_vertices(cx, cy, HEX_RADIUS)
    pts = " ".join(f"{x:.2f},{y:.2f}" for x, y in verts)

    edge_lines = []
    for i, edge_type in enumerate(tile.edges):
        color = EDGE_COLORS.get(edge_type, DEFAULT_EDGE_COLOR)
        x1, y1 = verts[i]
        x2, y2 = verts[(i + 1) % 6]
        edge_lines.append(
            f'    <line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}"'
            f' stroke="{color}" stroke-width="{EDGE_WIDTH}" stroke-linecap="round"/>'
        )

    return "\n".join([
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{IMAGE_SIZE}" height="{IMAGE_SIZE}">',
        "  <defs>",
        '    <clipPath id="hex">',
        f'      <polygon points="{pts}"/>',
        "    </clipPath>",
        "  </defs>",
        f'  <polygon points="{pts}" fill="{HEX_FILL}"/>',
        '  <g clip-path="url(#hex)">',
        *edge_lines,
        "  </g>",
        f'  <polygon points="{pts}" fill="none" stroke="{HEX_STROKE}" stroke-width="2"/>',
        f'  <text x="{cx:.0f}" y="{cy + 5:.0f}" text-anchor="middle"',
        f'        font-family="sans-serif" font-size="11" fill="#333">{tile.name} r{tile.rotation}</text>',
        "</svg>",
    ])


def main() -> None:
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    tiles = (
        HexTile.rotations("plain",         ["grass", "grass", "grass", "grass", "grass", "grass"]) |
        HexTile.rotations("road_end",      ["road",  "grass", "grass", "grass", "grass", "grass"]) |
        HexTile.rotations("road_straight", ["road",  "grass", "grass", "road",  "grass", "grass"])
    )

    tile_images: dict[str, str] = {}
    for tile in sorted(tiles, key=lambda t: (t.name, t.rotation)):
        key = f"{tile.name}_r{tile.rotation}"
        svg = render_svg(tile)
        path = os.path.join(OUTPUT_DIR, f"{key}.svg")
        with open(path, "w") as f:
            f.write(svg)
        tile_images[key] = svg
        print(path)

    bundle = os.path.join(OUTPUT_DIR, "tiles.json")
    with open(bundle, "w") as f:
        json.dump(tile_images, f)
    print(bundle)


if __name__ == "__main__":
    main()
