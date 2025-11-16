import bpy
import os
from mathutils import Vector

OUTPUT_DIR = r"C:\exported_blend_collections"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Get active collection from outliner
collection = bpy.context.collection
if not collection or collection == bpy.context.scene.collection:
    print("No collection selected! Select a collection in the outliner.")
else:
    coll_name = collection.name
    safe_filename = coll_name.replace("/", "_").replace("\\", "_").replace(":", "_")
    main_file = bpy.data.filepath
    export_path = os.path.join(OUTPUT_DIR, f"{safe_filename}.blend")
    
    # Get all objects in collection
    objects = [obj for obj in collection.objects if obj.type == 'MESH']
    
    if not objects:
        print("No mesh objects in collection!")
    else:
        # Save main file
        bpy.ops.wm.save_mainfile()
        
        # New file
        bpy.ops.wm.read_homefile(use_empty=True)
        
        # Load the collection
        with bpy.data.libraries.load(main_file) as (data_from, data_to):
            data_to.collections = [coll_name]
        
        # Link collection to scene
        for coll in data_to.collections:
            bpy.context.scene.collection.children.link(coll)
            
            mesh_objects = [obj for obj in coll.objects if obj.type == 'MESH']
            
            # Find the room object (largest by volume)
            largest_obj = None
            largest_volume = 0
            
            for obj in mesh_objects:
                bbox = [Vector(corner) for corner in obj.bound_box]
                size_x = max(c.x for c in bbox) - min(c.x for c in bbox)
                size_y = max(c.y for c in bbox) - min(c.y for c in bbox)
                size_z = max(c.z for c in bbox) - min(c.z for c in bbox)
                volume = size_x * size_y * size_z
                
                if volume > largest_volume:
                    largest_volume = volume
                    largest_obj = obj
            
            print(f"Room object identified: {largest_obj.name}")
            
            # Store original world positions before modifying origins
            original_positions = {}
            for obj in mesh_objects:
                original_positions[obj.name] = obj.matrix_world.translation.copy()
            
            # For each object, set its origin to XY center, bottom Z of its own geometry
            for obj in mesh_objects:
                mesh = obj.data
                
                # Get local bbox
                bbox_local = [Vector(corner) for corner in obj.bound_box]
                min_x = min(c.x for c in bbox_local)
                max_x = max(c.x for c in bbox_local)
                min_y = min(c.y for c in bbox_local)
                max_y = max(c.y for c in bbox_local)
                min_z = min(c.z for c in bbox_local)
                
                center_x = (min_x + max_x) / 2
                center_y = (min_y + max_y) / 2
                
                # Store offset to restore position after moving vertices
                offset_x = center_x
                offset_y = center_y
                offset_z = min_z
                
                # Move vertices so origin is at XY center, bottom Z
                for vert in mesh.vertices:
                    vert.co.x -= center_x
                    vert.co.y -= center_y
                    vert.co.z -= min_z
                mesh.update()
                
                # Restore world position by adjusting object location
                obj.location.x += offset_x
                obj.location.y += offset_y
                obj.location.z += offset_z
            
            # Now get room object's world position
            room_world_pos = largest_obj.location.copy()
            
            # Move all objects so room is at world origin
            for obj in mesh_objects:
                obj.location -= room_world_pos
        
        # Save
        bpy.ops.wm.save_as_mainfile(filepath=export_path)
        
        # Reopen main
        bpy.ops.wm.open_mainfile(filepath=main_file)
        
        print(f"Done: {coll_name} exported to {export_path}")