# GScatter — Blender 4.2+ / 5.x compatibility fixes

This is a community-maintained fork of **GScatter 0.12.0** by
[Graswald](https://gscatter.com/), patched to run on recent Blender versions
(4.2+ and 5.x), which ship **Python 3.13**. The original add-on failed to load
and to scatter on these builds. The original code is licensed **GPL-3.0-or-later**
(see `LICENSE` / `NOTICE`); this fork keeps that license and credits Graswald as
the original author.

## Symptoms this fixes

- The extension failed to install/enable, or Blender's own asset system threw
  `ImportError: cannot import name 'NothingType' from 'attrs'`.
- Nothing appeared to download in the add-on's asset panel.
- Scattering an asset crashed with:
  `IndexError: bpy_prop_collection[index]: index 8 out of range, size 4`
  (in `scatter/functions.py` → `create_point_mask_node_tree`).

## What was changed

### 1. Python 3.13 wheels (`blender_manifest.toml`, `wheels/`)
Blender 5.x embeds Python 3.13, but the bundle only shipped **cp311** wheels.
- Added **Pillow 11.2.1 `cp313`** wheels for every platform (macOS x64/arm64,
  Linux x64, Windows x64/arm64) and kept the cp311 ones.

### 2. `attrs` dependency conflict (`blender_manifest.toml`, `wheels/`)
The add-on bundled **`attrs 24.2.0`**, which Blender installs into the *shared*
extensions site-packages (`.local/.../site-packages`). That older `attrs`
**shadowed** the version Blender 5.x needs for its own asset back-end: Blender's
bundled `cattrs` imports `NothingType`, which only exists in **attrs ≥ 25.1**.
The result was an `ImportError` that broke Blender's native remote-asset system
and the add-on's asset install/download step.
- Bumped the bundled dependency to **`attrs 26.1.0`**.

### 3. Geometry Nodes API — "Random Value" node (`scatter/functions.py`)
Blender reorganized the **Random Value** node's socket collection. In Blender 3.x
the *Seed* socket was at index `8`; newer Blender only exposes the sockets for the
active data type, so the collection is `[Min, Max, ID, Seed]` (size 4) — index `8`
no longer exists.
- Changed `random_value.inputs[8]` to the version-robust
  `random_value.inputs["Seed"]` (address the socket by name).

## Verified on Blender 5.2 (Python 3.13)

- The extension enables with no `ImportError`; `attrs 26.1.0` and `cattrs` import
  cleanly.
- Pillow imports (`11.2.1`), the free-asset list loads (HTTP 200).
- All three built-in system presets scatter without error:
  `system.default`, `system.weight_paint`, `system.simple_terrain_generator`.

## Install

Install the extension folder as usual (Blender → Preferences → Add-ons /
Extensions → Install from Disk, pointing at a zip of this folder), then enable
**GScatter**. Make sure *Preferences → System → Allow Online Access* is enabled
so the add-on can fetch the free asset list.
