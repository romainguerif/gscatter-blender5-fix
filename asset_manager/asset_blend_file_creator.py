import bpy
import sys
import pathlib
import io
from zlib import decompress
from mathutils import Matrix

addon_name = "gscatter"

try:
    success = bpy.ops.preferences.addon_enable(module=addon_name)
    from PIL import Image
except ImportError:
    print(addon_name, "is not found")

GRASWALD_CATALOG_ID = "b97f2a08-d271-44a3-bde4-aaf0554b37c"
ASSETS_CATALOG_ID = "66e56e9d-4215-42a4-984d-a986d54e3fce"
ENVIRONMENTS_CATALOG_ID = "a0baa115-d25a-44e7-a5ad-eca5384d5f0f"
SYSTEM_PRESETS_CATALOG_ID = "fbc8debc-401d-47df-b9ea-18cd85dc9b74"
SINGLE_SYSTEM_PRESETS_CATALOG_ID = "9b5207ab-ac59-4bea-b680-1825424eca00"
FREE_ASSET_CATALOG_ID = "f686fee3-ac80-4754-b00a-fe2e8b059bc8"

# read command line arguments
args = []

skip = True

for arg in sys.argv:
    if arg == "--":
        skip = False
        continue

    if skip:
        continue

    args.append(arg)

blend_file_src = args[0]
blend_file_path = args[1]
product_name = args[2]
product_id = args[3]
catalog_id = args[4]
variants = eval(args[5])
asset_type = args[6]
preview = args[7]
create_object_entry = eval(args[8])
create_lod_collection_entry = eval(args[9])


def save():
    bpy.ops.wm.save_as_mainfile(filepath=blend_file_path)


def create_collection(name, parent_collection=None):
    collection = bpy.data.collections.new(name)
    if parent_collection:
        parent_collection.children.link(collection)
    return collection


def _bip_to_image(src, dst):
    """Convert BIP to various image formats."""
    _BIP2_MAGIC = b"BIP2"
    with open(src, "rb") as bip:
        if bip.read(4) != _BIP2_MAGIC:
            raise ValueError("input is not a supported file format")

        count = int.from_bytes(bip.read(1), "big")
        assert count > 0, "the file contains no images"
        bip.seek(8 * (count - 1), io.SEEK_CUR)

        size = [int.from_bytes(bip.read(2), "big") for _ in range(2)]
        length = int.from_bytes(bip.read(4), "big")

        bip.seek(-length, io.SEEK_END)
        content = decompress(bip.read(length))
        image = Image.frombytes("RGBa", size, content)
        image = image.convert("RGBA")
        image = image.transpose(Image.FLIP_TOP_BOTTOM)

        try:
            image.save(dst)
        except OSError:
            image.convert("RGB").save(dst)


if asset_type == "3D_PLANT":
    # shutil.copyfile(blend_file_src, blend_file_path)
    bpy.ops.wm.open_mainfile(filepath=blend_file_src)

    preview_icon_id = None
    is_vol1 = False
    for variant in variants:
        print(variant["id"])
        col = bpy.data.collections.get(variant["id"])
        if col is None or is_vol1:
            is_vol1 = True
            col = create_collection(variant["id"])
            bpy.context.scene.collection.children.link(col)

            for obj in bpy.data.objects:
                name_parts = obj.name.split("_")
                if len(name_parts) >= 4 and name_parts[1] == variant["id"]:
                    if (
                        bpy.data.collections.get(f"{variant['id']}_{name_parts[2]}")
                        is None
                    ):
                        type_col = create_collection(
                            f"{variant['id']}_{name_parts[2]}", col
                        )
                    if (
                        bpy.data.collections.get(
                            f"{variant['id']}_{name_parts[2]}_{name_parts[3]}"
                        )
                        is None
                    ):
                        lod_col = create_collection(
                            f"{variant['id']}_{name_parts[2]}_{name_parts[3]}", type_col
                        )

                    for collection in obj.users_collection:
                        collection.objects.unlink(obj)
                    lod_col.objects.link(obj)

                    if obj.data.shape_keys:
                        for key in obj.data.shape_keys.key_blocks:
                            if "height" in key.name.lower():
                                key.value = 0
                    key = obj.shape_key_add(from_mix=True)
                    key.value = 1.0

                    for key in obj.data.shape_keys.key_blocks:
                        obj.shape_key_remove(key)

                    mw = obj.matrix_world
                    mb = obj.matrix_basis

                    loc, rot, scale = mb.decompose()

                    # rotation & scale
                    T = Matrix.Translation(loc)
                    R = rot.to_matrix().to_4x4()
                    S = Matrix.Diagonal(scale).to_4x4()

                    if hasattr(obj.data, "transform"):
                        obj.data.transform(R @ S)

                    for c in obj.children:
                        c.matrix_local = (R @ S) @ c.matrix_local

                    obj.matrix_basis = T

        child: bpy.types.Collection
        for child in col.children:
            ob: bpy.types.Object
            for idx, ob in enumerate(child.objects):
                mat = ob.active_material
                albedo = mat.node_tree.nodes.get("albedo")
                if albedo:
                    mat.node_tree.nodes.active = albedo

            if create_object_entry:
                for ob in child.objects:
                    # ob.asset_mark()
                    bpy.context.view_layer.objects.active = ob
                    bpy.ops.object.select_all(action="DESELECT")
                    ob.select_set(True)
                    try:
                        with bpy.context.temp_override(id=ob, object=ob):
                            bpy.ops.asset.mark()
                            # bpy.ops.ed.lib_id_generate_preview()
                            # time.sleep(0.3)
                        ob.asset_data.description = variant["description"]
                        ob.asset_data.catalog_id = variant["lod_catalog_ids"][
                            ob.name.split("_")[-2]
                        ]
                        ob.asset_data.author = variant["author"]
                        ob.asset_data.copyright = "© Graswald GmbH 2024"
                        ob.asset_data.tags.new(name=product_id)
                        ob.asset_data.tags.new(name=variant["name"])
                    except Exception:
                        ...

            if create_lod_collection_entry:
                try:
                    with bpy.context.temp_override(id=child):
                        bpy.ops.asset.mark()
                        # bpy.ops.ed.lib_id_generate_preview()
                        # time.sleep(0.3)
                    lod = child.name.split("_")[-1]
                    child.name = variant["name"] + " " + lod.upper()
                    child.asset_data.description = variant["description"]
                    child.asset_data.catalog_id = variant["lod_catalog_ids"][lod]
                    child.asset_data.author = variant["author"]
                    child.asset_data.copyright = "© Graswald GmbH 2024"
                    child.asset_data.tags.new(name=product_id)
                    child.asset_data.tags.new(name=variant["name"])
                except Exception:
                    ...

        with bpy.context.temp_override(id=col):
            bpy.ops.asset.mark()
        col.name = variant["name"]
        col.asset_data.catalog_id = variant["variant_catalog_id"]
        col.asset_data.description = variant["description"]
        col.asset_data.author = variant["author"]
        col.asset_data.copyright = "© Graswald GmbH 2024"
        col["gscatter_type"] = "asset"
        col.asset_data.tags.new(name=product_id)
        col.asset_data.tags.new(name=variant["name"])
        col.asset_data.tags.new(name="asset_type:3D_PLANT")

        with bpy.context.temp_override(id=col):
            if pathlib.Path(variant["preview"].replace(".bip", ".png")).exists():
                bpy.ops.ed.lib_id_load_custom_preview(
                    filepath=variant["preview"].replace(".bip", ".png")
                )
            else:
                try:
                    if pathlib.Path(variant["preview"]).exists() and not variant[
                        "preview"
                    ].startswith("."):
                        _bip_to_image(
                            src=pathlib.Path(variant["preview"]),
                            dst=pathlib.Path(
                                variant["preview"].replace(".bip", ".png")
                            ),
                        )
                        bpy.ops.ed.lib_id_load_custom_preview(
                            filepath=variant["preview"].replace(".bip", ".png")
                        )
                except ImportError:
                    bpy.ops.ed.lib_id_generate_preview()
        # time.sleep(1)
    if is_vol1:
        bpy.ops.wm.save_as_mainfile(filepath=blend_file_src)

else:
    o = bpy.data.objects.new(
        name=product_name, object_data=bpy.data.meshes.new(name=product_name)
    )

    if asset_type == "ENVIRONMENT":
        with bpy.context.temp_override(id=o):
            bpy.ops.asset.mark()
            if preview:
                bpy.ops.ed.lib_id_load_custom_preview(filepath=preview)
    else:
        o.asset_mark()
        with bpy.context.temp_override(id=o):
            if preview:
                bpy.ops.ed.lib_id_load_custom_preview(filepath=preview)

    o.asset_data.catalog_id = catalog_id
    o["gscatter_type"] = asset_type
    o.asset_data.tags.new(name=product_id)
    o.asset_data.tags.new(name=f"asset_type:{asset_type.upper()}")


def batch_generate_previews():
    # Ensure you're in object mode
    if bpy.context.mode != "OBJECT":
        bpy.ops.object.mode_set(mode="OBJECT")

    # Iterate through all objects in the current blend file
    for obj in bpy.context.view_layer.objects:
        # Select the object
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)

        # Generate preview
        bpy.ops.wm.previews_batch_generate()

        # Deselect the object
        obj.select_set(False)


batch_generate_previews()
print("Gscatter: Saving")
save()


def quit():
    if pathlib.Path(blend_file_path).exists():
        bpy.ops.wm.quit_blender()
    return 0.5


bpy.app.timers.register(function=quit)
