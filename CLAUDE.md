# HexWorld

A Python library for hex-grid map generation and Wave Function Collapse (WFC) tile placement.

## Running

```
uv run python main.py        # run WFC and save map.json
uv run python generate_tiles.py  # render tile SVGs to tiles/
```

Then open `viewer.html` in a browser and load `map.json` to visualise the result.

Requires Python ≥ 3.14 (uses `type` alias statement syntax). No external dependencies.

## File overview

| File | Purpose |
|---|---|
| `hex_tile.py` | `HexTile` class |
| `hex_node.py` | `HexNode` class |
| `hex_map.py` | `HexMap` class + WFC logic |
| `main.py` | Demo: runs WFC, saves `map.json` |
| `generate_tiles.py` | Renders one SVG per tile into `tiles/` |
| `viewer.html` | Static page: load `map.json`, renders the map |

---

## Architecture

### `HexTile` (`hex_tile.py`)

A tile type defined by its 6 edge labels (strings, e.g. `"grass"`, `"road"`) plus presentation metadata.

- `edges: tuple[str, ...]` — stored as a tuple (hashable). Drives all WFC matching.
- `name: str` — human-readable type name, e.g. `"road_straight"`. Shared by all rotations of the same tile type.
- `rotation: int` — rotation index 0–5 (each step = 60°). **Presentation/rendering only** — has no effect on WFC matching.
- Identity (`__eq__` / `__hash__`) is edge-based only, so two tiles with identical edges are equal regardless of name or rotation.

```python
HexTile(edges=["road", "grass", "grass", "road", "grass", "grass"],
        name="road_straight", rotation=0)
```

#### `HexTile.rotations(name, edges) -> set[HexTile]`

Generates all rotationally unique variants of a tile. Each variant is a left-rotation of `edges` by `r` steps (r = 0…5). Symmetric tiles (e.g. all-grass) deduplicate automatically via `__eq__`/`__hash__`, keeping the lowest rotation index.

```python
tile_set = (
    HexTile.rotations("plain",         ["grass", "grass", "grass", "grass", "grass", "grass"]) |
    HexTile.rotations("road_end",      ["road",  "grass", "grass", "grass", "grass", "grass"]) |
    HexTile.rotations("road_straight", ["road",  "grass", "grass", "road",  "grass", "grass"])
)
```

---

### `HexNode` (`hex_node.py`)

A single hexagonal cell in **cube coordinates** (q, r, s) where q + r + s = 0 (s is auto-derived if omitted).

- `possible_tiles: set[HexTile]` — the tiles this node may still become. Passed by reference so multiple nodes can share the same set object without copying.
- `collapsed` property — `True` when `len(possible_tiles) == 1`.
- `neighbors()` returns 6 new `HexNode` instances (coordinate stubs, not map-aware).
- `distance(other)` — cube-coordinate Chebyshev distance.
- Equality and hashing are on `(q, r)` only.

---

### `HexMap` (`hex_map.py`)

A collection of `HexNode`s plus WFC logic.

- `_node_map: dict[tuple[int,int], HexNode]` — built once at construction for O(1) neighbour lookup.
- Factory methods: `HexMap.hexagon(radius, possible_tiles)` and `HexMap.rectangle(width, height, possible_tiles)`. Both accept the same `set[HexTile]` reference and forward it to every node (no copies).

#### Edge direction convention

`_DIRECTIONS` (module-level) lists the 6 cube-coordinate direction vectors in order:

```
index 0: ( 1, -1,  0)   upper-right
index 1: ( 1,  0, -1)   lower-right
index 2: ( 0,  1, -1)   below
index 3: (-1,  1,  0)   lower-left
index 4: (-1,  0,  1)   upper-left
index 5: ( 0, -1,  1)   above
```

`tile.edges[d]` is the edge label facing direction `d`. The opposite of direction `d` is `(d + 3) % 6`. Two adjacent tiles are compatible when `tile_a.edges[d] == tile_b.edges[(d+3) % 6]`.

#### WFC — `collapse(selector)`

```python
solved: bool = hex_map.collapse(selector=None)
```

Runs WFC until every node has exactly one tile (`collapsed == True`) or determines no solution exists.

**Algorithm:**
1. Find the uncollapsed node with fewest options (`_find_min_entropy`).
2. Call `selector(node, possible_tiles)` to get an ordered list of tiles to try.
3. Assign the first tile and run BFS arc-consistency (`_propagate`) outward.
4. If propagation succeeds, push `(node, n, snapshot, ordered)` onto the backtracking stack and repeat.
5. If propagation fails, restore the snapshot and try `ordered[n+1]`.
6. If all options for a node are exhausted, pop the stack and retry the previous decision at `prev_n + 1`.
7. Returns `False` only if the stack is empty and no option works.

**`selector` signature:** `(node: HexNode, tiles: set[HexTile]) -> list[HexTile]`

- Default: `sorted(tiles, key=hash)` — deterministic.
- Stochastic example: `lambda node, tiles: random.sample(list(tiles), len(tiles))`.
- Per-node weighting is just a conditional inside the lambda.

Backtracking is index-based: the stack stores `n` (which option was chosen), so retrying is `n + 1` with no re-evaluation of the selector.

**Reading a collapsed map:**

```python
for node in hex_map.nodes:
    tile = next(iter(node.possible_tiles))  # len == 1 after collapse
```

#### `to_json() -> str`

Serialises the map to a JSON string. Each node entry contains `q`, `r`, `s`, and a `tile` object (`name`, `rotation`, `edges`) or `null` if not yet collapsed. Load the result in `viewer.html`.

```python
with open("map.json", "w") as f:
    f.write(hex_map.to_json())
```

---

## Tile rendering (`generate_tiles.py`)

Writes one SVG per tile to `tiles/{name}_r{rotation}.svg`. Edge colours are defined in `EDGE_COLORS` at the top of the file — add new edge types there.

**Edge–vertex convention (flat-top hexagon, same in `viewer.html`):**
Edge `i` is the side from vertex `i` to vertex `(i+1) % 6`, where vertex `i` sits at `i × 60°` clockwise from east (screen coordinates, +y downward).

To look up the image for a collapsed tile:

```python
tile = next(iter(node.possible_tiles))
path = f"tiles/{tile.name}_r{tile.rotation}.svg"
```
