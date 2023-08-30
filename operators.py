import bpy
from mathutils import Vector, Matrix

# 'Slave to Path' operator
class SimpleOperator(bpy.types.Operator):
    
    bl_idname = "object.simple_operator"
    bl_label = "Slave to Path"
    bl_description = "Automatically wrangles selected object and assigns it to the selected path"

    def execute(self, context):

        selected_objects = bpy.context.selected_objects
        
        if len(selected_objects) > 1:
            self.report({'ERROR'}, "Only use when one object is selected.")
            return {'CANCELLED'}
        
        bpy.ops.object.constraint_add(type='FOLLOW_PATH')
        bpy.context.object.constraints["Follow Path"].target = context.object.my_tool.path
        bpy.context.object.constraints["Follow Path"].use_fixed_location = True
        bpy.context.object.constraints["Follow Path"].use_curve_follow = True
        bpy.context.object.constraints["Follow Path"].forward_axis = context.object.my_tool.forward_axis
        bpy.context.object.constraints["Follow Path"].keyframe_insert("offset_factor", frame=bpy.context.scene.frame_current)
        bpy.context.object.constraints["Follow Path"].offset_factor = 1.0
        bpy.context.object.constraints["Follow Path"].keyframe_insert("offset_factor", frame=bpy.context.scene.frame_end)


        context.object.my_tool.path.name = bpy.context.object.name + "_path"
        

        context.object.my_tool.path = None
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
        
        my_tool = obj.my_tool
        lightspeed_frame = frame + my_tool.lightspeed_time
        
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
        
        my_tool = obj.my_tool
        lightspeed_frame = frame - my_tool.lightspeed_time
        
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
        # Assign the path object to the property
        selected_obj.my_tool.path = active_object

        # Clean-up
        context.view_layer.objects.active = selected_obj
        context.object.my_tool.path = active_object
        
        return {'FINISHED'}

# 'Create Starfield' operator
class WorldOperator(bpy.types.Operator):
    bl_idname = "scene.create_starfield"
    bl_label = "Create Starfield"
    bl_description = "Creates a new starfield shader and makes it active in this scene"

    def execute(self, context):
        
        world_name = "Starfield"
        
        if world_name in bpy.data.worlds:
            # Delete the existing world
            bpy.data.worlds.remove(bpy.data.worlds[world_name], do_unlink=True)
            
        world = bpy.data.worlds.new(world_name)
        world.use_nodes = True
        nodes = world.node_tree.nodes
        links = world.node_tree.links

        # Clear existing nodes
        for node in nodes:
            nodes.remove(node)

        texture_coord_node = nodes.new(type='ShaderNodeTexCoord')
        mapping_node = nodes.new(type='ShaderNodeMapping')
        noise_node = nodes.new(type='ShaderNodeTexNoise')
        color_ramp_node = nodes.new(type='ShaderNodeValToRGB')
        background_node = nodes.new(type='ShaderNodeBackground')
        world_output_node = nodes.new(type='ShaderNodeOutputWorld')

        # Set up the nodes
        texture_coord_node.location = (-600, 0)
        mapping_node.location = (-400, 0)
        noise_node.location = (-200, 0)
        color_ramp_node.location = (0, 0)
        background_node.location = (200, 0)
        world_output_node.location = (400, 0)

        # Set the scale for the Noise node
        noise_node.inputs['Scale'].default_value = 1000.0

        # Link the nodes
        world.node_tree.links.new(texture_coord_node.outputs['Generated'], mapping_node.inputs['Vector'])
        world.node_tree.links.new(mapping_node.outputs['Vector'], noise_node.inputs['Vector'])
        world.node_tree.links.new(noise_node.outputs['Fac'], color_ramp_node.inputs['Fac'])
        world.node_tree.links.new(color_ramp_node.outputs['Color'], background_node.inputs['Color'])
        world.node_tree.links.new(background_node.outputs['Background'], world_output_node.inputs['Surface'])

        # Find the first element (marker) of the Color Ramp
        first_element = color_ramp_node.color_ramp.elements[0]
        second_element = color_ramp_node.color_ramp.elements[1]

        star_brightness_multiplier = 3

        # Set the position of the first element to 0.7 (left marker)
        first_element.position = 0.7
        second_element.color = (1 * star_brightness_multiplier, 1 * star_brightness_multiplier, 1 * star_brightness_multiplier, 1)

        # Assign the world shader to the active scene
        scene = bpy.context.scene
        scene.world = world

        context.scene.scene_tool.starfield = world
        
        self.report({'INFO'}, "World updated to designated starfield.")
        return {'FINISHED'}

target_collection_name = 'RogueToolkit_Lasers'

class CreateLaser(bpy.types.Operator):
    bl_idname = "scene.create_laser"
    bl_label = "Create Laser"
    bl_description = "Lasers!!!"

    def execute(self, context):
        location = (0, 0, 0)

        selected_objects = bpy.context.selected_objects
        active_object = bpy.context.active_object
        emitter = None

        if active_object and active_object in selected_objects:
            emitter = active_object

            # Get the location of the active object
            location = emitter.location

        else:
            return {'CANCELLED'}
            

        target_collection = None
        active_collection = context.collection

        if target_collection_name in bpy.data.collections:
                target_collection = bpy.data.collections[target_collection_name]
        else:
            # Create the collection if it doesn't exist
            target_collection = bpy.data.collections.new(target_collection_name)
            bpy.context.scene.collection.children.link(target_collection)

        bpy.ops.object.empty_add(type='SINGLE_ARROW', align='WORLD', location=location, scale=(1, 1, 1))
        new_laser = bpy.context.active_object

        bpy.context.view_layer.objects.active = emitter
        emitter.select_set(True)
        new_laser.select_set(False)

        target_collection.objects.link(new_laser)
        active_collection.objects.unlink(new_laser)

        ## Keyframing ##

        cur_frame = context.scene.frame_current
        lifetime = context.object.laser_tool.laser_lifetime
        velocity = context.object.laser_tool.laser_velocity

        new_laser.matrix_world = emitter.matrix_world
        
        emitter_matrix = emitter.matrix_world.copy()
        emitter_matrix.invert() # inversion basically cancels out transformations applied to the object
        location, rotation, scale = emitter_matrix.decompose()
        laser_matrix = Matrix.LocRotScale(location, rotation, scale)
        rotation_vector = Vector((0,0,0)) @ laser_matrix
        new_laser.location = new_laser.location + rotation_vector

        new_laser.keyframe_insert( data_path = 'location', frame = cur_frame)
        new_laser.location = emitter.matrix_world.translation + Vector((0, 0, lifetime * velocity)) @ laser_matrix
        new_laser.keyframe_insert( data_path = 'location', frame = cur_frame + lifetime)

        # Set initial visibility
        new_laser.hide_viewport = True
        new_laser.hide_render = True
        new_laser.keyframe_insert(data_path="hide_viewport", frame=cur_frame - 1)
        new_laser.keyframe_insert(data_path="hide_render", frame=cur_frame - 1)

        # Make the empty visible before it starts moving
        new_laser.hide_viewport = False
        new_laser.hide_render = False
        new_laser.keyframe_insert(data_path="hide_viewport", frame=cur_frame)
        new_laser.keyframe_insert(data_path="hide_render", frame=cur_frame)

        # Set visibility to hide again after animation ends
        new_laser.hide_viewport = True
        new_laser.hide_render = True
        new_laser.keyframe_insert(data_path="hide_viewport", frame=cur_frame + lifetime)
        new_laser.keyframe_insert(data_path="hide_render", frame=cur_frame + lifetime)

        #making animation linear
        fcurves = new_laser.animation_data.action.fcurves
        for fcurve in fcurves:
            for kf in fcurve.keyframe_points:
                kf.interpolation = 'LINEAR'

        ## -- Raycasting -- ##

        if context.object.laser_tool.toggle_collision is True:

            emitter_direction = Vector(emitter.matrix_world.col[2][:3])
            collision_frame = None
                            
            result = bpy.context.scene.ray_cast(
                bpy.context.window.view_layer.depsgraph,
                emitter.matrix_world.translation,
                emitter_direction)

            # In the event of a collision
            if result[0]:
                intersection_point = result[1]
                normal = result[2]
                print("Laser hit at:", intersection_point)
                distance = (emitter.matrix_world.translation - result[1]).length
                print("Distance:", distance)
                print("Normal at hit point:", normal)

                collision_frame = int(cur_frame + distance / velocity) + 1 # the +1 is so the laser fully overlaps with the obj
                print("Frame of Impact:", collision_frame)

                # 'Destroy' the laser
                new_laser.hide_viewport = True
                new_laser.hide_render = True
                new_laser.keyframe_insert(data_path="hide_viewport", frame=collision_frame)
                new_laser.keyframe_insert(data_path="hide_render", frame=collision_frame)
            else:
                print("Laser didn't hit any objects.")

        self.report({'INFO'}, "Laser created.")
        return {'FINISHED'}

class CreateLaserEmitter(bpy.types.Operator):
    bl_idname = "scene.create_laser_emitter"
    bl_label = "Create Laser Emitter"
    bl_description = "Create emitter object for lasers."

    def execute(self, context):
        location = (0, 0, 0)

        selected_objects = bpy.context.selected_objects
        active_object = bpy.context.active_object

        if active_object and active_object in selected_objects:
            # Get the location of the active object
            location = active_object.location

        bpy.ops.object.empty_add(type='SINGLE_ARROW', align='WORLD', location=location, scale=(1, 1, 1))
        new_emitter = bpy.context.active_object

        self.report({'INFO'}, "Laser emitter created.")
        return {'FINISHED'}

class DeleteAllLasers(bpy.types.Operator):
    bl_idname = "scene.delete_all_lasers"
    bl_label = "Delete All Lasers"
    bl_description = "Delete all lasers in this scene."

    def execute(self, context):

        if target_collection_name in bpy.data.collections:
            target_collection = bpy.data.collections[target_collection_name]

            objects_to_delete = target_collection.objects[:]
            for obj in objects_to_delete:
                bpy.data.objects.remove(obj)

            bpy.data.collections.remove(target_collection)

        self.report({'INFO'}, "All lasers deleted.")
        return {'FINISHED'}
    