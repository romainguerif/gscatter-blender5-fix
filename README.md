# GScatter — Blender 4.2+ / 5.x compatibility fork

A community-maintained fork of **[GScatter](https://gscatter.com/) 0.12.0** by
[Graswald](https://www.graswald3d.com/), patched to install and run on recent
Blender versions (**4.2+ and 5.x**, which ship **Python 3.13**). The original
0.12.0 build failed to load and to scatter on these versions.

> This is an unofficial community fix. All credit for GScatter goes to Graswald.
> The code is licensed **GPL-3.0-or-later** (see [`LICENSE`](LICENSE) /
> [`NOTICE`](NOTICE)); this fork keeps that license.

## What this fixes

| Problem on Blender 4.2+/5.x | Fix |
| --- | --- |
| Extension fails to enable; Blender throws `ImportError: cannot import name 'NothingType' from 'attrs'` | Bundled `attrs` bumped **24.2.0 → 26.1.0** (the old one shadowed the copy Blender's own asset system needs) |
| Nothing downloads in the asset panel | Same root cause as above (broke the asset install/download step) |
| Scattering crashes with `IndexError: bpy_prop_collection[index]: index 8 out of range, size 4` | Random Value geometry node addressed by socket **name** (`inputs["Seed"]`) instead of the removed index `8` |
| Pillow fails to import (image previews) | Added **Pillow 11.2.1 `cp313`** wheels for all platforms (bundle was `cp311`-only) |

Full technical write-up: [**BLENDER5_FIXES.md**](BLENDER5_FIXES.md).

### Verified on Blender 5.2 (Python 3.13)
- Extension enables with no `ImportError`; `attrs 26.1.0` and Blender's `cattrs` import cleanly.
- Pillow imports (11.2.1); the free-asset list loads.
- All three built-in system presets scatter without error
  (`system.default`, `system.weight_paint`, `system.simple_terrain_generator`).

## About GScatter

GScatter is a free scattering add-on built on Blender's geometry nodes. It lets
you scatter any object on a surface and control the look — density, scale,
rotation and much more — to quickly create natural environments like meadows or
forests.

## Installation

1. Download this repository as a ZIP (green **Code** button → **Download ZIP**),
   or build one from the folder. **Do not unzip it** before installing.
2. In Blender, open **Edit → Preferences → Add-ons / Extensions**.
3. Click **Install…** (or the dropdown → **Install from Disk**) and pick the ZIP.
4. Enable **GScatter** in the add-on list.
5. Make sure **Preferences → System → Allow Online Access** is enabled so the
   add-on can fetch the free asset list.

## Links (original project)

- Website: <https://www.graswald3d.com/>
- Discord: <https://discord.com/invite/nsV9g55MGQ>

## License

GPL-3.0-or-later. Copyright © 2024 Graswald GmbH. See [`LICENSE`](LICENSE).
