import bpy
import math
import random
import os
from mathutils import Vector, Matrix

# Hard-coded names
laser_collection_name = 'RogueToolkit_Lasers'
decal_collection_name = 'RogueToolkit_Decals'
muzzlef_collection_name = 'RogueToolkit_MuzzleFlash'
linkedobjs_collection_name = 'RogueToolkit_LinkedObjects'

# Get a relative filepath
addon_dir = os.path.dirname(os.path.abspath(__file__))
blend_file_name = "objects.blend"
blend_file_path = os.path.join(addon_dir, blend_file_name)

print("Directory:", blend_file_path)

class AttachToPath(bpy.types.Operator):
    
    bl_idname = "object.simple_operator"
    bl_label = "Slave to Path"
    bl_description = "Automatically wrangles selected object and assigns it to the selected path"

    def execute(self, context):

        selected_objects = bpy.context.selected_objects
        
        if len(selected_objects) > 1:
            self.report({'ERROR'}, "Only use when one object is selected.")
            return {'CANCELLED'}
        
        bpy.ops.object.constraint_add(type='FOLLOW_PATH')
        bpy.context.object.constraints["Follow Path"].target = context.object.rigging_tool.path
        bpy.context.object.constraints["Follow Path"].use_fixed_location = True
        bpy.context.object.constraints["Follow Path"].use_curve_follow = True
        bpy.context.object.constraints["Follow Path"].forward_axis = context.object.rigging_tool.forward_axis
        bpy.context.object.constraints["Follow Path"].keyframe_insert("offset_factor", frame=bpy.context.scene.frame_current)
        bpy.context.object.constraints["Follow Path"].offset_factor = 1.0
        bpy.context.object.constraints["Follow Path"].keyframe_insert("offset_factor", frame=bpy.context.scene.frame_end)


        context.object.rigging_tool.path.name = bpy.context.object.name + "_path"
        

        context.object.rigging_tool.path = None
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
        # Assign the path object to the property
        selected_obj.rigging_tool.path = active_object

        # Clean-up
        context.view_layer.objects.active = selected_obj
        context.object.rigging_tool.path = active_object
        
        return {'FINISHED'}

# 'Create Starfield' operator
class CreateStarfield(bpy.types.Operator):
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

def move_to_collection(name: str, obj) -> None:
    active_collection = bpy.context.collection
    target_collection = None

    if name in bpy.data.collections:
        target_collection = bpy.data.collections[name]
    else:
        target_collection = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(target_collection)

    target_collection.objects.link(obj)

    if obj.name in active_collection.objects:
        active_collection.objects.unlink(obj)

class CreateLaser(bpy.types.Operator):
    bl_idname = "object.create_laser"
    bl_label = "Create Laser"
    bl_description = "Instantiate a new laser projectile from this emitter."

    def set_visibility(self, context, obj, fshow, fhide=None):

        origin_frame = context.scene.frame_current

        # Set initial visibility
        obj.hide_viewport = True
        obj.hide_render = True
        obj.keyframe_insert(data_path="hide_viewport", frame=fshow - 1)
        obj.keyframe_insert(data_path="hide_render", frame=fshow - 1)

        # Make the empty visible before it starts moving
        obj.hide_viewport = False
        obj.hide_render = False
        obj.keyframe_insert(data_path="hide_viewport", frame=fshow)
        obj.keyframe_insert(data_path="hide_render", frame=fshow)

        if fhide:
            # Set visibility to hide again after animation ends
            obj.hide_viewport = True
            obj.hide_render = True
            obj.keyframe_insert(data_path="hide_viewport", frame=fhide)
            obj.keyframe_insert(data_path="hide_render", frame=fhide)

        #making animation linear
        fcurves = obj.animation_data.action.fcurves
        for fcurve in fcurves:
            for kf in fcurve.keyframe_points:
                kf.interpolation = 'LINEAR'

        context.scene.frame_set(origin_frame)

    def ignore_objects(self, context, setting: bool, emitter):

        ignored_objects = []

        laser_collection = bpy.data.collections.get(laser_collection_name)
        if laser_collection:
            ignored_objects += laser_collection.objects
        decal_collection = bpy.data.collections.get(decal_collection_name)
        if decal_collection:
            ignored_objects += decal_collection.objects

        if emitter.laser_tool.muzzlef_obj is not None:
            ignored_objects.append(emitter.laser_tool.muzzlef_obj)

        for source in ignored_objects:
            source.hide_viewport = setting

    def create_decal(self, context, source, rc_result, collision_frame):

        origin_frame = context.scene.frame_current

        # Create decal mesh
        decal = None

        with bpy.data.libraries.load(blend_file_path) as (data_from, data_to):
            data_to.collections = ["decals"]

        for collection in data_to.collections:
            for obj in collection.objects:
                move_to_collection(decal_collection_name, obj)
                decal = obj

                bpy.context.view_layer.objects.active = decal
                decal.select_set(True)

                mat_name = obj.name.split(".")[0]

                if bpy.data.materials.get(mat_name) and obj.material_slots[0].material != bpy.data.materials.get(mat_name):
                    bpy.data.materials.remove(obj.material_slots[0].material)

                     # Remove all material slots
                    for i in range(len(decal.material_slots) - 1, -1, -1):
                        bpy.context.object.active_material_index = i
                        bpy.ops.object.material_slot_remove()

                    bpy.ops.object.material_slot_remove()
                    decal.data.materials.append(bpy.data.materials[mat_name])

                break

        if decal is None:
            print("Decal is invalid!")
            return {'CANCELLED'}

        # Align to surface
        face_normal = Vector(rc_result[2])
                    
        z = Vector(decal.matrix_world.col[2][:3])
        axis = z.cross(face_normal)
        angle_cos = z.dot(face_normal)
        angle_cos = max(min(angle_cos, 1.0), -1.0)
        angle = math.acos(angle_cos)
        m = Matrix.Rotation(angle, 4, axis)
        decal.matrix_world = m @ decal.matrix_world
        vec = Vector((0.0, 0.0, round(random.uniform(0.003, 0.006), 10)))
        inv = decal.matrix_world.copy()
        inv.invert()
        vec_rot = vec @ inv
        decal.location = rc_result[1] + vec_rot

        decal.scale = source.laser_tool.decal_scale

        new_item = source.laser_tool.impact_decals.add()
        new_item.impact_decal = decal

        context.scene.frame_set(collision_frame)

        # Create a Child Of constraint
        child_of_constraint = decal.constraints.new(type='CHILD_OF')
        child_of_constraint.target = rc_result[4]
        child_of_constraint.mute = False

        # Potentially disable for performance gains if it ends up being unnecessary 
        shrinkwrap_modifier = decal.modifiers.new(name="Shrinkwrap", type='SHRINKWRAP')
        shrinkwrap_modifier.target = rc_result[4]
        shrinkwrap_modifier.wrap_method = 'TARGET_PROJECT'
        shrinkwrap_modifier.offset = 0.005
        bpy.context.view_layer.objects.active = decal
        decal.select_set(True)
        bpy.ops.object.modifier_apply(modifier="Shrinkwrap")

        bpy.context.view_layer.objects.active = source
        source.select_set(True)
        decal.select_set(False)

        self.set_visibility(context, obj=decal, fshow=collision_frame)

        context.scene.frame_set(origin_frame)

    # Make source emitter check for collisions during the entire life of the projectile to be fired
    def check_collision(self, source, projectile, lifetime, context):

        origin_frame = context.scene.frame_current
        context.scene.frame_set(origin_frame)

        # Save locations of the moving projectile
        locs = []
        startf = origin_frame
        endf = startf + lifetime

        while context.scene.frame_current <= endf:
            projectile.hide_viewport = False
            locs.append(projectile.location.copy())

            # Increase the frame
            context.scene.frame_set(context.scene.frame_current + 1)

        context.scene.frame_set(origin_frame)

        # Ensure that only the correct type of objects will be hit by a ray-cast
        self.ignore_objects(context, True, source)

        # For each frame in the lifetime of the projectile, check if there has been a hit.
        startf = origin_frame
        endf = startf + lifetime
        f = 0
        min_dist = None
        data = None

        while context.scene.frame_current <= endf:
            self.ignore_objects(context, True, source)
            source_dir = Vector(source.matrix_world.col[2][:3])
            result = bpy.context.scene.ray_cast(bpy.context.window.view_layer.depsgraph,source.matrix_world.translation,source_dir)
            
            if result[0]:

                
                # print("Ray hit something:", result[4].name, "at frame:", context.scene.frame_current - 1)
                intersection_point = result[1]
                normal = result[2]
                distance = (locs[f] - intersection_point).length
                coll_frame = None

                # print("Ray hit something:", result[4].name, "at frame:", context.scene.frame_current - 1, "and distance:", distance)

                if min_dist is None:
                    min_dist = distance
                elif distance < min_dist:
                    min_dist = distance 
                elif distance > min_dist:
                    coll_frame = context.scene.frame_current - 1
                    # print("Obj:", projectile.name, "hit something:", result[4].name, "at frame:", coll_frame)
                    data = [result, coll_frame, intersection_point, normal]
                    break

            # Increase the frame
            context.scene.frame_set(context.scene.frame_current + 1)
            f += 1

        # Reshow objects that were hidden
        self.ignore_objects(context, False, source)
    
        # Return to the original scene frame
        context.scene.frame_set(origin_frame)

        # Return details
        return data

    def apply_color_to_obj(self, context, source, obj):
        if source.laser_tool.laser_color == "Red":
            obj.color = (1.0, 0, 0, 1.0)
        elif source.laser_tool.laser_color == "Blue":
            obj.color = (0, 0, 1.0, 1.0)
        elif source.laser_tool.laser_color == "Green":
            obj.color = (0, 1, 0, 1)
        else:
            obj.color = (1, 1, 1, 1)
    
    # Responsible for creation of each individual laser
    def init_laser(self, source, context):
        origin_frame = context.scene.frame_current
        location = (0, 0, 0)

        # Muzzle flash
        if source.laser_tool.toggle_muzzlef is True:

            if source.laser_tool.muzzlef_obj is None:

                 # Create laser mesh
                muzzlef = None

                try:
                    template_muzzlef = bpy.data.objects["MuzzleFlash"]
                except:
                    with bpy.data.libraries.load(blend_file_path, link=True) as (data_from, data_to):
                        data_to.collections = ["muzzlef"]

                    for collection in data_to.collections:
                        for obj in collection.objects:
                            move_to_collection(linkedobjs_collection_name, obj)
                            template_muzzlef = obj

                            bpy.context.view_layer.objects.active = muzzlef
                            template_muzzlef.select_set(False)

                            break

                muzzlef = template_muzzlef.copy()
                muzzlef.parent = source

                self.apply_color_to_obj(context, source, muzzlef)

                bpy.context.view_layer.objects.active = source
                source.select_set(True)
                muzzlef.select_set(False)

                move_to_collection(muzzlef_collection_name, muzzlef)

                source.laser_tool.muzzlef_obj = muzzlef

            # Animate visibility
            source.laser_tool.muzzlef_obj.scale = (0, 0, 0)
            source.laser_tool.muzzlef_obj.keyframe_insert(data_path="scale", frame=context.scene.frame_current - 1)

            source.laser_tool.muzzlef_obj.scale = source.laser_tool.muzzlef_scale
            source.laser_tool.muzzlef_obj.keyframe_insert(data_path="scale", frame=context.scene.frame_current)

            source.laser_tool.muzzlef_obj.scale = (0, 0, 0)
            source.laser_tool.muzzlef_obj.keyframe_insert(data_path="scale", frame=context.scene.frame_current + 1)

        # Create laser mesh
        new_laser = None

        try:
            template_laser = bpy.data.objects["Laser"]
        except:

            with bpy.data.libraries.load(blend_file_path, link=True) as (data_from, data_to):
                data_to.collections = ["lasers"]

            for collection in data_to.collections:
                for obj in collection.objects:
                    move_to_collection(linkedobjs_collection_name, obj)
                    template_laser = obj

                    bpy.context.view_layer.objects.active = new_laser
                    template_laser.select_set(False)

                    break


            for view_layer in context.scene.view_layers:
                view_layer.layer_collection.children[linkedobjs_collection_name].exclude = True  
        

        new_laser = template_laser.copy()
        new_laser.animation_data_create()

        self.apply_color_to_obj(context, source, new_laser)

        print(new_laser.color)

        # Create a unique action for each new_laser object
        new_laser.animation_data.action = bpy.data.actions.new(name=f"LaserAction_{new_laser.name}")

        move_to_collection(laser_collection_name, new_laser)

        bpy.context.view_layer.objects.active = new_laser
        source.select_set(False)
        new_laser.select_set(True)

        # Confusing calculations to determine how to orient laser to proper axes
        new_laser.matrix_world = source.matrix_world
        emitter_matrix = source.matrix_world.copy()
        emitter_matrix.invert() # inversion basically cancels out transformations applied to the object
        location, rotation, scale = emitter_matrix.decompose()
        laser_matrix = Matrix.LocRotScale(location, rotation, scale)
        rotation_vector = Vector((0,0,0)) @ laser_matrix
        new_laser.location = new_laser.location + rotation_vector

        new_laser.scale = source.laser_tool.laser_scale

        bpy.context.view_layer.objects.active = source
        source.select_set(True)
        new_laser.select_set(False)

        # Animate movement of laser
        origin = new_laser.location
        new_laser.keyframe_insert( data_path = 'location', frame = context.scene.frame_current)
        new_laser.location = source.matrix_world.translation + Vector((0, 0, context.object.laser_tool.laser_lifetime * context.object.laser_tool.laser_velocity)) @ laser_matrix
        new_laser.keyframe_insert( data_path = 'location', frame = context.scene.frame_current + context.object.laser_tool.laser_lifetime)
        new_laser.location = origin

        # Make animation linear
        fcurves = new_laser.animation_data.action.fcurves
        for fcurve in fcurves:
            for kf in fcurve.keyframe_points:
                kf.interpolation = 'LINEAR'

        # Check for collisions of lasers
        data = self.check_collision(source, new_laser, source.laser_tool.laser_lifetime, context)

        if data is None: # if there is no collision
            self.set_visibility(context, new_laser, context.scene.frame_current, context.scene.frame_current + source.laser_tool.laser_lifetime)
        else: # if there is a collision
            self.set_visibility(context, new_laser, context.scene.frame_current, data[1])
                        
            # Decal handling
            if source.laser_tool.toggle_decals is True:
                hit_info = data[0]
                if hit_info[0] is True:
                    self.create_decal(context, source, data[0], data[1])

        # Save laser and frame to source
        new_item = source.laser_tool.instantiated_lasers.add()
        new_item.instantiated_laser = new_laser

        new_frame = source.laser_tool.laser_frames.add()
        new_frame.laser_frame = bpy.context.scene.frame_current

        context.scene.frame_set(origin_frame)

        self.report({'INFO'}, "Laser created.")
        return {'FINISHED'}

    def execute(self, context):

        if bpy.context.object is None:
            return {'CANCELLED'}

        if bpy.context.object.laser_tool.valid_emitter is False:
            return {'CANCELLED'}

        if bpy.context.object.laser_tool.child_emitter is True:
            return {'CANCELLED'}

        results = []

        selected_emitter = bpy.context.object
        results.append(self.init_laser(selected_emitter, context))

        for child in selected_emitter.laser_tool.linked_emitters:
            linked_emitter = child.linked_emitter

            results.append(self.init_laser(linked_emitter, context))

        curr_selection = bpy.context.object
        curr_selection.select_set(False)

        bpy.context.view_layer.objects.active = selected_emitter
        selected_emitter.select_set(True)

        if 'CANCELLED' in results:
            return {'CANCELLED'}
        else:
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

        new_emitter.laser_tool.valid_emitter = True

        # Apply a 90-degree rotation around the X-axis
        rotation_angle = math.radians(90)  # Convert degrees to radians
        new_emitter.rotation_euler.x = rotation_angle

        self.report({'INFO'}, "Laser emitter created.")
        return {'FINISHED'}

class CreateLinkedEmitter(bpy.types.Operator):
    bl_idname = "object.create_linked_emitter"
    bl_label = "Create Linked Emitter"
    bl_description = "Add an emitter with linked settings to the selected emitter that will create lasers in unison."

    def execute(self, context):

        main_emitter = bpy.context.active_object

        bpy.ops.scene.create_laser_emitter()

        new_emitter = bpy.context.active_object
        new_emitter.laser_tool.child_emitter = True

        added_emitter = main_emitter.laser_tool.linked_emitters.add()
        added_emitter.linked_emitter = new_emitter

        added_emitter.linked_emitter.laser_tool.parent_emitter = main_emitter

        bpy.context.view_layer.objects.active = main_emitter
        main_emitter.select_set(True)
        added_emitter.linked_emitter.select_set(False)

        return {'FINISHED'}

class RecalculateLasers(bpy.types.Operator):
    bl_idname = "object.recalculate_lasers"
    bl_label = "Recalculate Emitter's Lasers"
    bl_description = "Recalculate all lasers created by this emitter. (for use when settings are changed, etc.)"

    def recalculate_emitter_lasers(self, source, context):

        laser_frames = []

        for item in source.laser_tool.laser_frames:
            laser_frames.append(item.laser_frame)

        bpy.ops.object.delete_all_lasers()

        laser_frames = set(laser_frames)
        print("Laser frames:", laser_frames)

        for laser_frame in laser_frames:
            bpy.context.scene.frame_set(laser_frame)
            print("executed once")
            bpy.ops.object.create_laser()

    def execute(self, context):

        selected_emitter = bpy.context.object
        curr_frame = bpy.context.scene.frame_current

        self.recalculate_emitter_lasers(selected_emitter, context)

        bpy.context.scene.frame_set(curr_frame)
        return {'FINISHED'}



class DeleteAllLasers(bpy.types.Operator):
    bl_idname = "object.delete_all_lasers"
    bl_label = "Delete Emitter's Lasers"
    bl_description = "Delete all lasers created by this emitter."

    def delete_emitters_lasers(self, source, context):

        emitter_properties = source.laser_tool

        # Create a list of objects to delete
        objects_to_delete = [obj_ref.instantiated_laser for obj_ref in emitter_properties.instantiated_lasers]
        objects_to_delete += [obj_ref.impact_decal for obj_ref in emitter_properties.impact_decals]

        # Clear the collection property
        emitter_properties.instantiated_lasers.clear()
        emitter_properties.impact_decals.clear()
        emitter_properties.laser_frames.clear()

        # Delete the objects from the scene
        for obj in objects_to_delete:
            bpy.data.objects.remove(obj, do_unlink=True)

        if emitter_properties.muzzlef_obj:
            bpy.data.objects.remove(emitter_properties.muzzlef_obj, do_unlink=True)

        self.report({'INFO'}, "All emitter's lasers deleted.")
        return {'FINISHED'}
    

    def execute(self, context):

        selected_emitter = bpy.context.object

        self.delete_emitters_lasers(selected_emitter, context)
        for child in selected_emitter.laser_tool.linked_emitters:
            linked_emitter = child.linked_emitter
            self.delete_emitters_lasers(linked_emitter, context)
        
        return {'FINISHED'}


class DeleteLinkedEmitter(bpy.types.Operator):
    bl_idname = "object.delete_linked_emitter"
    bl_label = "Delete Linked Emitter"
    bl_description = "DaDASD"

    def execute(self, context):
        if context.object.laser_tool.child_emitter is False:
            return {'CANCELLED'}
        
        coll =  context.object.laser_tool.parent_emitter.laser_tool.linked_emitters
        i = 0
        for item in coll:
            if item.linked_emitter == context.object:
                coll.remove(i)
            i += 1

        bpy.ops.object.delete_all_lasers()
        bpy.data.objects.remove(context.object, do_unlink=True)

        return {'FINISHED'}

