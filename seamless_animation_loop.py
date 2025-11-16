import bpy

# Get all actions in the scene
for action in bpy.data.actions:
    for fcurve in action.fcurves:
        if len(fcurve.keyframe_points) < 2:
            continue
        
        first = fcurve.keyframe_points[0]
        last = fcurve.keyframe_points[-1]
        
        # Make the handles symmetric for looping
        # Copy the outgoing handle of the last frame to the incoming handle of the first
        first.handle_left_type = 'FREE'
        last.handle_right_type = 'FREE'
        
        # Calculate handle positions to make them continuous
        handle_offset = last.handle_left - last.co
        first.handle_left = first.co + handle_offset
        
        handle_offset = first.handle_right - first.co
        last.handle_right = last.co + handle_offset
        
        print(f"Fixed loop for {fcurve.data_path}")

print("Done! Loop handles fixed.")
