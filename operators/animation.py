import bpy

class AttachToPath(bpy.types.Operator):
    
    bl_idname = "object.simple_operator"
    bl_label = "Attach to Path"
    bl_description = "Automatically wrangles selected object and assigns it to the selected path"

    def execute(self, context):

        selected_objects = bpy.context.selected_objects
        
        if len(selected_objects) > 1:
            self.report({'ERROR'}, "Only use when one object is selected.")
            return {'CANCELLED'}
        
        origin_frame = int(context.scene.frame_start)

        bpy.ops.object.constraint_add(type='FOLLOW_PATH')
        bpy.context.object.constraints["Follow Path"].target = context.object.rigging_tool.path
        bpy.context.object.constraints["Follow Path"].use_fixed_location = True
        bpy.context.object.constraints["Follow Path"].use_curve_follow = True
        bpy.context.object.constraints["Follow Path"].forward_axis = context.object.rigging_tool.forward_axis
        bpy.context.object.constraints["Follow Path"].keyframe_insert("offset_factor", frame=origin_frame)
        bpy.context.object.constraints["Follow Path"].offset_factor = 1.0
        bpy.context.object.constraints["Follow Path"].keyframe_insert("offset_factor", frame=bpy.context.scene.frame_end)


        context.object.rigging_tool.path.name = bpy.context.object.name + "_path"
        

        context.object.rigging_tool.path = None

        context.scene.frame_set(origin_frame)

        self.report({'INFO'}, "Successfully slaved object to path.")

        return {'FINISHED'}

# 'Jump to Lightspeed' operator
class CreateLightspeedJump(bpy.types.Operator):
    bl_idname = "object.create_lightspeed_jump"
    bl_label = "Jump to Lightspeed"
    bl_description = "Makes selected object speedily leave the scene"

    def execute(self, context):
        
        obj = context.active_object
        frame = bpy.context.scene.frame_current
        
        rigging_tool = obj.rigging_tool
        lightspeed_frame = frame + rigging_tool.lightspeed_time
        
        # Keyframing
        obj.hide_viewport = False
        obj.hide_render = False
        obj.keyframe_insert(data_path="hide_viewport", frame=frame)
        obj.keyframe_insert(data_path="hide_render", frame=frame)
        obj.keyframe_insert(data_path="location", frame=frame)

        location = obj.location
        rotation = obj.rotation_euler.to_matrix()

        # Calculate the vector representing the object's normal-x direction
        normal_x = rotation @ Vector((0, 0, 1))

        # Define the amount of translation along the normal-x direction
        translation_amount = 999.9

        # Apply the translation along the normal-x direction
        obj.location += normal_x * translation_amount

    
        obj.keyframe_insert(data_path="location", frame=lightspeed_frame)
        obj.hide_viewport = True
        obj.hide_render = True
        obj.keyframe_insert(data_path="hide_viewport", frame=lightspeed_frame)
        obj.keyframe_insert(data_path="hide_render", frame=lightspeed_frame)
        
        
        bpy.context.scene.frame_current = frame
        context.view_layer.objects.active = obj
        

        return {'FINISHED'}
    
# 'Revert from Lightspeed' operator
class CreateLightspeedReturn(bpy.types.Operator):
    bl_idname = "object.create_lightspeed_return"
    bl_label = "Revert from Lightspeed"
    bl_description = "Makes selected object speedily join the scene"

    def execute(self, context):

        obj = context.active_object
        frame = bpy.context.scene.frame_current
        
        rigging_tool = obj.rigging_tool
        lightspeed_frame = frame - rigging_tool.lightspeed_time
        
        # Keyframe
        bpy.context.scene.frame_current = lightspeed_frame
        obj.hide_viewport = True
        obj.hide_render = True
        obj.keyframe_insert(data_path="hide_viewport", frame=lightspeed_frame - 1)
        obj.keyframe_insert(data_path="hide_render", frame=lightspeed_frame - 1)
        obj.keyframe_insert(data_path="location", frame=frame - 1)
        
        # -- Math -- #
        location = obj.location
        rotation = obj.rotation_euler.to_matrix()
        # Calculate the vector representing the object's normal-x direction
        normal_x = rotation @ Vector((0, 0, 1))
        # Define the amount of translation along the normal-x direction
        translation_amount = -999.9
        # Apply the translation along the normal-x direction
        obj.location += normal_x * translation_amount
        
        # Keyframe
        bpy.context.scene.frame_current = frame
        obj.keyframe_insert(data_path="location", frame=lightspeed_frame)
        obj.hide_viewport = False
        obj.hide_render = False
        obj.keyframe_insert(data_path="hide_viewport", frame=lightspeed_frame)
        obj.keyframe_insert(data_path="hide_render", frame=lightspeed_frame)
        
        # Clean-up
        context.view_layer.objects.active = obj
        bpy.context.scene.frame_current = frame

        return {'FINISHED'}
    

# 'Create Flight Plan' operator
class CreateFlightPlan(bpy.types.Operator):
    bl_idname = "object.create_flight_plan"
    bl_label = "Create Flight Plan"
    bl_description = "Automatically wrangles selected object and assigns it to a new selected path"

    def execute(self, context):

        selected_objects = bpy.context.selected_objects
        
        if len(selected_objects) > 1:
            self.report({'ERROR'}, "Only use when one object is selected.")
            return {'CANCELLED'}
        
        selected_obj = bpy.context.selected_objects[0]
       
        # Create a new path object
        bpy.ops.curve.primitive_nurbs_path_add(radius=1, enter_editmode=False, align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
        bpy.context.object.data.resolution_u = 64
        bpy.context.object.data.render_resolution_u = 256


        # Get the active object (which is the newly created path object)
        active_object = bpy.context.active_object
        active_object.scale = (10, 10, 10)
        # Assign the path object to the property
        selected_obj.rigging_tool.path = active_object

        # Clean-up
        context.view_layer.objects.active = selected_obj
        context.object.rigging_tool.path = active_object
        
        return {'FINISHED'}