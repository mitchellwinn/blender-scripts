import bpy
import os
from mathutils import Vector

OUTPUT_DIR = r"C:\linked_blend_files"
os.makedirs(OUTPUT_DIR, exist_ok=True)

obj = bpy.context.active_object
if not obj:
    print("No active object selected!")
else:
    obj_name = obj.name
    main_file = bpy.data.filepath
    export_path = os.path.join(OUTPUT_DIR, f"{obj_name}.blend")
    
    # Store original transform and collection NAME
    original_loc = obj.location.copy()
    original_rot = obj.rotation_euler.copy()
    original_scale = obj.scale.copy()
    collection_name = obj.users_collection[0].name if obj.users_collection else None
    
    # Calculate where the object's bottom center is in world space
    if obj.type == 'MESH':
        bbox_corners = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
        min_x = min(corner.x for corner in bbox_corners)
        max_x = max(corner.x for corner in bbox_corners)
        min_y = min(corner.y for corner in bbox_corners)
        max_y = max(corner.y for corner in bbox_corners)
        min_z = min(corner.z for corner in bbox_corners)
        
        bottom_center_world = Vector(((min_x + max_x) / 2, (min_y + max_y) / 2, min_z))
    
    print(f"Original bottom center in world: {bottom_center_world}")
    
    # Save main file
    bpy.ops.wm.save_mainfile()
    
    # New file
    bpy.ops.wm.read_homefile(use_empty=True)
    
    # Use low-level API to append
    with bpy.data.libraries.load(main_file) as (data_from, data_to):
        data_to.objects = [obj_name]
    
    # Link to scene
    for o in data_to.objects:
        bpy.context.collection.objects.link(o)
        
        # Select and make active
        bpy.ops.object.select_all(action='DESELECT')
        o.select_set(True)
        bpy.context.view_layer.objects.active = o
        
        # First set origin to geometry center (XY center, bottom Z)
        if o.type == 'MESH':
            mesh = o.data
            
            # Get bbox in local space
            bbox_corners = [Vector(corner) for corner in o.bound_box]
            min_x = min(corner.x for corner in bbox_corners)
            max_x = max(corner.x for corner in bbox_corners)
            min_y = min(corner.y for corner in bbox_corners)
            max_y = max(corner.y for corner in bbox_corners)
            min_z = min(corner.z for corner in bbox_corners)
            
            center_x = (min_x + max_x) / 2
            center_y = (min_y + max_y) / 2
            
            # Move all vertices so origin is at XY center, bottom Z
            for vert in mesh.vertices:
                vert.co.x -= center_x
                vert.co.y -= center_y
                vert.co.z -= min_z
            mesh.update()
        
        # Now reset object transform to world origin
        o.location = (0, 0, 0)
        o.rotation_euler = (0, 0, 0)
        o.scale = (1, 1, 1)
        
        print(f"Object centered at world origin, bottom at z=0")
    
    # Save
    bpy.ops.wm.save_as_mainfile(filepath=export_path)
    
    # Reopen main
    bpy.ops.wm.open_mainfile(filepath=main_file)
    
    # Delete original
    obj = bpy.data.objects[obj_name]
    bpy.data.objects.remove(obj)
    
    # Link back
    with bpy.data.libraries.load(export_path, link=True) as (data_from, data_to):
        data_to.objects = [obj_name]
    
    linked = data_to.objects[0]
    if collection_name:
        bpy.data.collections[collection_name].objects.link(linked)
    else:
        bpy.context.scene.collection.objects.link(linked)
    
    # Make library override using low-level API
    override_obj = linked.override_create(remap_local_usages=True)
    
    # Restore position - since origin is now at bottom center, just place it there
    override_obj.location = bottom_center_world
    override_obj.rotation_euler = original_rot
    override_obj.scale = original_scale
    
    print(f"Done: {obj_name} restored to bottom center at {override_obj.location}")