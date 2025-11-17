import bpy

print(f"Total actions: {len(bpy.data.actions)}\n")

for action in bpy.data.actions:
    print(f"Processing: {action.name}")
    
    if action.is_empty:
        print(f"  Skipped: empty\n")
        continue
    
    fixed_count = 0
    
    # Blender 5: action → layers → strips → keyframe_data → channelbags → fcurves
    for layer in action.layers:
        print(f"  Layer: {layer.name}")
        for strip in layer.strips:
            # Access channelbags directly from strip
            if not hasattr(strip, 'channelbags'):
                continue
            
            for channelbag in strip.channelbags:
                for fcurve in channelbag.fcurves:
                    if len(fcurve.keyframe_points) < 2:
                        continue
                    
                    first = fcurve.keyframe_points[0]
                    last = fcurve.keyframe_points[-1]
                    
                    # Make handles symmetric for seamless looping
                    first.handle_left_type = 'FREE'
                    last.handle_right_type = 'FREE'
                    
                    # Mirror the handle directions
                    handle_offset = last.handle_left - last.co
                    first.handle_left = first.co + handle_offset
                    
                    handle_offset = first.handle_right - first.co
                    last.handle_right = last.co + handle_offset
                    
                    fixed_count += 1
    
    if fixed_count > 0:
        print(f"  ✓ Fixed {fixed_count} curves\n")
    else:
        print(f"  No curves found\n")

print("Done!")
