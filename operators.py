import bpy
import math
import random
import os
from mathutils import Vector, Matrix, Quaternion

# Hard-coded names
projectile_collection_name = 'RogueToolkit_Projectiles'
decal_collection_name = 'RogueToolkit_Decals'
explosion_collection_name = 'RogueToolkit_Explosions'
muzzlef_collection_name = 'RogueToolkit_MuzzleFlash'
linkedobjs_collection_name = 'RogueToolkit_LinkedObjects'

# Get a relative filepath
addon_dir = os.path.dirname(os.path.abspath(__file__))
blend_file_name = "objects.blend"
blend_file_path = os.path.join(addon_dir, blend_file_name)

# Given a value and a range, get a variation on that number
def get_varied_scale(value: float, offset: float) -> float:
    min_scale = value - offset
    max_scale = value + offset
    return random.uniform(min_scale, max_scale)

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

class CreateProjectile(bpy.types.Operator):
    bl_idname = "object.create_projectile"
    bl_label = "Simulate Projectile"
    bl_description = "Instantiate a new projectile projectile from this emitter."

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

        projectile_collection = bpy.data.collections.get(projectile_collection_name)
        if projectile_collection:
            ignored_objects += projectile_collection.objects
        decal_collection = bpy.data.collections.get(decal_collection_name)
        if decal_collection:
            ignored_objects += decal_collection.objects
        explosion_collection = bpy.data.collections.get(explosion_collection_name)
        if explosion_collection:
            ignored_objects += explosion_collection.objects

        if emitter.projectile_tool.muzzlef_obj is not None:
            ignored_objects.append(emitter.projectile_tool.muzzlef_obj)

        for source in ignored_objects:
            source.hide_viewport = setting

    def create_decal(self, context, source, rc_result, collision_frame, loc):

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
            return {'CANCELLED'}

        # Align to surface
        decal.location = loc

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
        decal.location = loc + vec_rot

        # Set decal scale
        scale = get_varied_scale(source.projectile_tool.decal_scale, source.projectile_tool.decal_scale_variation)
        decal.scale = (scale, scale, scale)

        new_item = source.projectile_tool.impact_decals.add()
        new_item.impact_decal = decal

        context.scene.frame_set(collision_frame)

        # Create a Child Of constraint
        child_of_constraint = decal.constraints.new(type='CHILD_OF')
        child_of_constraint.target = rc_result[4]
        child_of_constraint.mute = False

        # # Potentially disable for performance gains if it ends up being unnecessary 
        shrinkwrap_modifier = decal.modifiers.new(name="Shrinkwrap", type='SHRINKWRAP')
        shrinkwrap_modifier.target = rc_result[4]
        shrinkwrap_modifier.wrap_method = 'TARGET_PROJECT'
        shrinkwrap_modifier.wrap_mode = 'ON_SURFACE'
        bpy.context.view_layer.objects.active = decal
        decal.select_set(True)
        bpy.ops.object.modifier_apply(modifier="Shrinkwrap")

        # offset the explosion closer to the camera
        vec = Vector((0.0, 0.0, 0.03))
        inv = decal.matrix_world.copy()
        inv.invert()
        vec_rot = vec @ inv
        decal.location += vec_rot

        bpy.context.view_layer.objects.active = source
        source.select_set(True)
        decal.select_set(False)

        self.set_visibility(context, obj=decal, fshow=collision_frame + 1)

        context.scene.frame_set(origin_frame)



    def create_explosion(self, context, source, rc_result, collision_frame, loc):

        origin_frame = context.scene.frame_current

        # Create decal mesh
        explosion = None

        with bpy.data.libraries.load(blend_file_path) as (data_from, data_to):
            data_to.collections = ["billboards"]

        for collection in data_to.collections:
            for obj in collection.objects:
                move_to_collection(explosion_collection_name, obj)
                explosion = obj

                bpy.context.view_layer.objects.active = explosion
                explosion.select_set(True)
                break

        if explosion is None:
            return {'CANCELLED'}
        
        
        # Change start frame
        if explosion.material_slots:
            if explosion.material_slots[0]:
                material = explosion.material_slots[0].material

                if material.node_tree.nodes["Image Texture"]:
                    material.node_tree.nodes["Image Texture"].image_user.frame_start = collision_frame

        # Align to surface
        explosion.location = loc

        # Align to surface
        face_normal = Vector(rc_result[2])
        z = Vector(explosion.matrix_world.col[2][:3])
        axis = z.cross(face_normal)
        angle_cos = z.dot(face_normal)
        angle_cos = max(min(angle_cos, 1.0), -1.0)
        angle = math.acos(angle_cos)
        m = Matrix.Rotation(angle, 4, axis)
        explosion.matrix_world = m @ explosion.matrix_world
        vec = Vector((0.0, 0.0, round(random.uniform(0.003, 0.006), 10)))
        inv = explosion.matrix_world.copy()
        inv.invert()
        vec_rot = vec @ inv
        explosion.location = loc + vec_rot

        scale = get_varied_scale(source.projectile_tool.explosion_scale, source.projectile_tool.explosion_scale_variation)
        explosion.scale = (scale, scale, scale)
        new_item = source.projectile_tool.impact_decals.add()
        new_item.impact_decal = explosion

        # Track to camera
        orient_target = bpy.context.scene.camera

        if (orient_target is None):
            orient_target = source

        # Add a Track To constraint to the object
        track_constraint = explosion.constraints.new(type='TRACK_TO')
        track_constraint.target = orient_target
        track_constraint.track_axis = 'TRACK_Z'
        track_constraint.up_axis = 'UP_Y' 

        context.scene.frame_set(collision_frame)
        bpy.context.view_layer.objects.active = source
        source.select_set(True)
        explosion.select_set(False)

        self.set_visibility(context, obj=explosion, fshow=collision_frame)

        context.scene.frame_set(origin_frame)


    # Make source emitter check for collisions during the entire life of the projectile to be fired
    def check_collision(self, source, projectile, lifetime, context):

        origin_frame = context.scene.frame_current
        context.scene.frame_set(origin_frame)

        # Save locations of the moving projectile
        locs = []
        prev_ip = None # save locations of intersection points
        last_collision = None
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
            rc_result = bpy.context.scene.ray_cast(bpy.context.window.view_layer.depsgraph,locs[f],source_dir)
            
            if rc_result[0]:
                
                intersection_point = rc_result[1]
                distance = (locs[f] - intersection_point).length
                coll_frame = None
                
                if min_dist is None:
                    min_dist = distance
                elif distance < min_dist:
                    min_dist = distance 
                elif distance > min_dist:
                    coll_frame = context.scene.frame_current - 1

                    # rc_result[2] is the impact normal
                    data = [rc_result, coll_frame, prev_ip, rc_result[2]]
                    break

                prev_ip = intersection_point
                last_collision = [rc_result, context.scene.frame_current - 1, prev_ip, rc_result[2]]


            # Increase the frame
            context.scene.frame_set(context.scene.frame_current + 1)
            f += 1

        # Reshow objects that were hidden
        self.ignore_objects(context, False, source)
    
        # Return to the original scene frame
        context.scene.frame_set(origin_frame)

        # Return details
        if last_collision != None:
            return last_collision
        else:
            return data

    def apply_color_to_obj(self, context, source, obj):
        new_color = (0, 0, 0, 0)
        if source.projectile_tool.projectile_color == "Red":
            new_color = (1.0, 0, 0, 1.0)
            
        elif source.projectile_tool.projectile_color == "Blue":
            new_color = (0, 0, 1.0, 1.0)
        elif source.projectile_tool.projectile_color == "Green":
            new_color = (0, 1, 0, 1)
        elif source.projectile_tool.projectile_color == "Custom":
            new_color = source.projectile_tool.custom_color

        obj.color = new_color

        # Make sure the object has a material
        if obj.material_slots:
            # Access the first material slot
            material_slot = obj.material_slots[0]

            # Make sure the material slot is assigned to a material
            if material_slot.material:
                # Access the material
                material = material_slot.material

            # Set the viewport display color
            material.diffuse_color = new_color

    def create_impact_flash(self, context, source, rc_result, collision_frame):
        pass


    def create_termination_flak(self, context, source, new_projectile, origin_frame):

        context.scene.frame_set(origin_frame + source.projectile_tool.projectile_lifetime)
        flak_loc = Vector(new_projectile.location) # use Vector constructor so it's a full copy
        collision_frame = context.scene.frame_current
        context.scene.frame_set(origin_frame)

        # Create decal mesh
        explosion = None

        with bpy.data.libraries.load(blend_file_path) as (data_from, data_to):
            data_to.collections = ["billboards"]

        for collection in data_to.collections:
            for obj in collection.objects:
                move_to_collection(explosion_collection_name, obj)
                explosion = obj

                bpy.context.view_layer.objects.active = explosion
                explosion.select_set(True)
                break

        if explosion is None:
            return {'CANCELLED'}
        
        
        # Change start frame
        if explosion.material_slots:
            if explosion.material_slots[0]:
                material = explosion.material_slots[0].material

                if material.node_tree.nodes["Image Texture"]:
                    material.node_tree.nodes["Image Texture"].image_user.frame_start = collision_frame

        # Set location
        explosion.location = flak_loc

        explosion.scale = (source.projectile_tool.flak_scale, source.projectile_tool.flak_scale, source.projectile_tool.flak_scale)
        new_item = source.projectile_tool.impact_decals.add()
        new_item.impact_decal = explosion

        # offset the explosion closer to the camera
        vec = Vector((0.0, 0.0, 0.1))
        inv = explosion.matrix_world.copy()
        inv.invert()
        vec_rot = vec @ inv
        explosion.location += vec_rot

        scale = get_varied_scale(source.projectile_tool.flak_scale, source.projectile_tool.flak_scale_variation)
        explosion.scale = (scale, scale, scale)

        # Track to camera
        orient_target = bpy.context.scene.camera

        if (orient_target is None):
            orient_target = source

        # Add a Track To constraint to the object
        track_constraint = explosion.constraints.new(type='TRACK_TO')
        track_constraint.target = orient_target
        track_constraint.track_axis = 'TRACK_Z'
        track_constraint.up_axis = 'UP_Y' 

        context.scene.frame_set(collision_frame)
        bpy.context.view_layer.objects.active = source
        source.select_set(True)
        explosion.select_set(False)

        self.set_visibility(context, obj=explosion, fshow=collision_frame)

        context.scene.frame_set(origin_frame)

    
    # Responsible for creation of each individual projectile
    def init_projectile(self, source, context):

        origin_frame = context.scene.frame_current
        location = (0, 0, 0)

        # Muzzle flash
        if source.projectile_tool.toggle_muzzlef is True:

            if source.projectile_tool.muzzlef_obj is None:

                # Create muzzle
                new_muzzle = None

                try:
                    template_muzzle = bpy.data.objects["MuzzleFlash"]
                except:

                    with bpy.data.libraries.load(blend_file_path, link=True) as (data_from, data_to):
                        data_to.collections = ["muzzlef"]

                    for collection in data_to.collections:
                        for obj in collection.objects:
                            move_to_collection(linkedobjs_collection_name, obj)
                            template_muzzle = obj

                            bpy.context.view_layer.objects.active = new_muzzle
                            template_muzzle.select_set(False)

                            break


                for view_layer in context.scene.view_layers:
                    view_layer.layer_collection.children[linkedobjs_collection_name].exclude = True  
            

                new_muzzle = template_muzzle.copy()
                new_muzzle.parent = source
                new_muzzle.animation_data_create()

                self.apply_color_to_obj(context, source, new_muzzle)

                new_muzzle.animation_data_create()
                new_muzzle.animation_data.action = bpy.data.actions.new(name=f"MuzzleAction_{new_muzzle.name}")

                move_to_collection(muzzlef_collection_name, new_muzzle)

                bpy.context.view_layer.objects.active = source
                source.select_set(True)
                new_muzzle.select_set(False)

                source.projectile_tool.muzzlef_obj = new_muzzle

            # Animate visibility
            source.projectile_tool.muzzlef_obj.scale = (0, 0, 0)
            source.projectile_tool.muzzlef_obj.keyframe_insert(data_path="scale", frame=context.scene.frame_current - 1)

            source.projectile_tool.muzzlef_obj.scale = (source.projectile_tool.muzzlef_scale, source.projectile_tool.muzzlef_scale, source.projectile_tool.muzzlef_scale)
            source.projectile_tool.muzzlef_obj.keyframe_insert(data_path="scale", frame=context.scene.frame_current)

            source.projectile_tool.muzzlef_obj.scale = (0, 0, 0)
            source.projectile_tool.muzzlef_obj.keyframe_insert(data_path="scale", frame=context.scene.frame_current + 1)

        # Create projectile mesh
        new_projectile = None

        try:
            template_projectile = bpy.data.objects["Projectile"]
        except:

            with bpy.data.libraries.load(blend_file_path, link=True) as (data_from, data_to):
                data_to.collections = ["projectiles"]

            for collection in data_to.collections:
                for obj in collection.objects:
                    move_to_collection(linkedobjs_collection_name, obj)
                    template_projectile = obj

                    bpy.context.view_layer.objects.active = new_projectile
                    template_projectile.select_set(False)

                    break


            for view_layer in context.scene.view_layers:
                view_layer.layer_collection.children[linkedobjs_collection_name].exclude = True  
        

        new_projectile = template_projectile.copy()
        new_projectile.animation_data_create()

        self.apply_color_to_obj(context, source, new_projectile)

        # Create a unique action for each new_projectile object
        new_projectile.animation_data.action = bpy.data.actions.new(name=f"ProjectileAction_{new_projectile.name}")

        move_to_collection(projectile_collection_name, new_projectile)

        bpy.context.view_layer.objects.active = new_projectile
        source.select_set(False)
        new_projectile.select_set(True)

        # Confusing calculations to determine how to orient projectile to proper axes
        new_projectile.matrix_world = source.matrix_world
        emitter_matrix = source.matrix_world.copy()
        emitter_matrix.invert() # inversion basically cancels out transformations applied to the object
        location, rotation, scale = emitter_matrix.decompose()
        projectile_matrix = Matrix.LocRotScale(location, rotation, scale)
        rotation_vector = Vector((0,0,0)) @ projectile_matrix
        new_projectile.location = new_projectile.location + rotation_vector

        new_projectile.scale = (source.projectile_tool.projectile_scale, source.projectile_tool.projectile_scale, source.projectile_tool.projectile_scale)

        bpy.context.view_layer.objects.active = source
        source.select_set(True)
        new_projectile.select_set(False)

        # Animate movement of projectile
        origin = new_projectile.location
        new_projectile.keyframe_insert( data_path = 'location', frame = context.scene.frame_current)
        new_projectile.location = source.matrix_world.translation + Vector((0, 0, context.object.projectile_tool.projectile_lifetime * context.object.projectile_tool.projectile_velocity)) @ projectile_matrix
        new_projectile.keyframe_insert( data_path = 'location', frame = context.scene.frame_current + context.object.projectile_tool.projectile_lifetime)
        new_projectile.location = origin

        # Make animation linear
        fcurves = new_projectile.animation_data.action.fcurves
        for fcurve in fcurves:
            for kf in fcurve.keyframe_points:
                kf.interpolation = 'LINEAR'



        # Check for collisions of projectiles
        if source.projectile_tool.toggle_collision:
            data = self.check_collision(source, new_projectile, source.projectile_tool.projectile_lifetime, context)

            if data is None: # if there is no collision

                self.set_visibility(context, new_projectile, context.scene.frame_current, context.scene.frame_current + source.projectile_tool.projectile_lifetime)

            else: # if there is a collision

                self.set_visibility(context, new_projectile, context.scene.frame_current, data[1] + 1)
                            
                # Decal handling
                if source.projectile_tool.toggle_decals is True:
                    hit_info = data[0]
                    if hit_info[0] is True:
                        self.create_decal(context, source, data[0], data[1], data[2])
                if source.projectile_tool.toggle_flash is True:
                    hit_info = data[0]
                    if hit_info[0] is True:
                        self.create_impact_flash(context, source, data[0], data[1])
                if source.projectile_tool.toggle_explosion is True:
                    hit_info = data[0]
                    if hit_info[0] is True:
                        self.create_explosion(context, source, data[0], data[1], data[2])
        else:
            self.set_visibility(context, new_projectile, context.scene.frame_current, context.scene.frame_current + source.projectile_tool.projectile_lifetime)


        # handle flak separately from collisions
        if (source.projectile_tool.toggle_flak is True):
            self.create_termination_flak(context, source, new_projectile, origin_frame)

        # Save projectile and frame to source
        new_item = source.projectile_tool.instantiated_projectiles.add()
        new_item.instantiated_projectile = new_projectile

        new_frame = source.projectile_tool.projectile_frames.add()
        new_frame.projectile_frame = int(bpy.context.scene.frame_current)

        # context.scene.frame_set(origin_frame)

        self.report({'INFO'}, "Projectile created.")
        return {'FINISHED'}

    def execute(self, context):

        if bpy.context.object is None:
            return {'CANCELLED'}
        if bpy.context.object.projectile_tool.valid_emitter is False:
            return {'CANCELLED'}
        if bpy.context.object.projectile_tool.child_emitter is True:
            self.report({'INFO'}, "Select owning emitter to use.")
            return {'CANCELLED'}

        results = []

        selected_emitter = bpy.context.object
        results.append(self.init_projectile(selected_emitter, context))

        # Purge any linked emitters if they've been deleted
        for i, item in enumerate(selected_emitter.projectile_tool.linked_emitters):
            child = item.linked_emitter

            if not child or child.name not in context.scene.objects:
                selected_emitter.projectile_tool.linked_emitters.remove(i)
            else:
                results.append(self.init_projectile(child, context))

        curr_selection = bpy.context.object
        curr_selection.select_set(False)

        bpy.context.view_layer.objects.active = selected_emitter
        selected_emitter.select_set(True)

        if 'CANCELLED' in results:
            return {'CANCELLED'}
        else:
            return {'FINISHED'}

class SimulateFlakField(bpy.types.Operator):
    bl_idname = "object.simulate_flak_field"
    bl_label = "Simulate"
    bl_description = "Simulate volume in which explosions are random and everywhere!"

    def create_explosion(self, context, location: tuple, start_frame, parent):
        origin_frame = context.scene.frame_current

        # Create decal mesh
        explosion = None

        with bpy.data.libraries.load(blend_file_path) as (data_from, data_to):
            data_to.collections = ["billboards"]

        for collection in data_to.collections:
            for obj in collection.objects:
                move_to_collection(explosion_collection_name, obj)
                explosion = obj

                bpy.context.view_layer.objects.active = explosion
                explosion.select_set(True)
                break

        if explosion is None:
            return {'CANCELLED'}
        

        
        # Change start frame
        if explosion.material_slots:
            if explosion.material_slots[0]:
                material = explosion.material_slots[0].material

                if material.node_tree.nodes["Image Texture"]:
                    material.node_tree.nodes["Image Texture"].image_user.frame_start = start_frame

        # Make the child object the child of the parent object
        explosion.parent = parent

        # Optionally, you can keep the child object's transformation relative to the parent
        explosion.matrix_parent_inverse = parent.matrix_world.inverted()
        explosion.location = (location[0], location[1], location[2])
        explosion.scale = (parent.flakfield_tool.explosion_scale, parent.flakfield_tool.explosion_scale, parent.flakfield_tool.explosion_scale)  

        # Track to camera
        orient_target = bpy.context.scene.camera

        if (orient_target is None):
            orient_target = parent

        # Add a Track To constraint to the object
        track_constraint = explosion.constraints.new(type='TRACK_TO')
        track_constraint.target = orient_target
        track_constraint.track_axis = 'TRACK_Z'
        track_constraint.up_axis = 'UP_Y' 

        context.scene.frame_set(start_frame)
        explosion.select_set(False)

        new_item = parent.flakfield_tool.explosion_billboards.add()
        new_item.explosion_billboard = explosion
        context.scene.frame_set(origin_frame)

    def calculate_explosions(self, context, empty):


        location = empty.location
        rotation = empty.rotation_euler
        scale = empty.scale

        # Calculate rotation matrix
        rotation_matrix = rotation.to_matrix().to_4x4()

        # Transform unit vectors representing axes by the rotation
        axis_x = rotation_matrix @ Vector((1, 0, 0))
        axis_y = rotation_matrix @ Vector((0, 1, 0))
        axis_z = rotation_matrix @ Vector((0, 0, 1))

        # Calculate maximum extents based on rotated axes and scale
        max_x = location.x + scale.x * max(abs(axis_x.x), abs(axis_x.y), abs(axis_x.z))
        max_y = location.y + scale.y * max(abs(axis_y.x), abs(axis_y.y), abs(axis_y.z))
        max_z = location.z + scale.z * max(abs(axis_z.x), abs(axis_z.y), abs(axis_z.z))

        for i in range(empty.flakfield_tool.num_explosions):
            startf = int(random.uniform(empty.flakfield_tool.start_frame, empty.flakfield_tool.end_frame))
            pos = (random.uniform(-max_x, max_x), random.uniform(-max_y, max_y), random.uniform(-max_z, max_z))
            self.create_explosion(context, pos, startf, empty)

    def execute(self, context):
        empty = bpy.context.object

        flakfield_properties = empty.flakfield_tool

        # Create a list of objects to delete
        objects_to_delete = [ref.explosion_billboard for ref in flakfield_properties.explosion_billboards]

        # Clear the collection property
        flakfield_properties.explosion_billboards.clear()

        # Delete the objects from the scene
        for obj in objects_to_delete:
            bpy.data.objects.remove(obj, do_unlink=True)

        self.calculate_explosions(context, empty)

        bpy.context.view_layer.objects.active = empty

        return {'FINISHED'}


class CreateFlakField(bpy.types.Operator):
    bl_idname = "scene.create_flak_field"
    bl_label = "Create Simulation"
    bl_description = "Create volume for simulation"

    def execute(self, context):
       
        bpy.ops.object.empty_add(type='CUBE', align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
        
        # Get the newly created cube object
        empty = bpy.context.object
        empty.scale = (10, 10, 10)
        empty.name = 'Flakfield'

        empty.flakfield_tool.valid_flakfield = True

        bpy.context.view_layer.objects.active = empty

        return {'FINISHED'}

class DeleteFlakField(bpy.types.Operator):
    bl_idname = "object.delete_flak_field"
    bl_label = "Clear Simulation"
    bl_description = "Delete volume and all linked explosion billboards."

    def execute(self, context):

        flakfield_properties = context.object.flakfield_tool

        # Create a list of objects to delete
        objects_to_delete = [ref.explosion_billboard for ref in flakfield_properties.explosion_billboards]

        # Clear the collection property
        flakfield_properties.explosion_billboards.clear()

        # Delete the objects from the scene
        for obj in objects_to_delete:
            bpy.data.objects.remove(obj, do_unlink=True)

        # bpy.data.objects.remove(context.object, do_unlink=True)

        return {'FINISHED'}

class CreateProjectileEmitter(bpy.types.Operator):
    bl_idname = "scene.create_projectile_emitter"
    bl_label = "Create Emitter"
    bl_description = "Create emitter object for projectiles."

    def execute(self, context):
        location = (0, 0, 0)

        selected_objects = bpy.context.selected_objects
        active_object = bpy.context.active_object

        if active_object and active_object in selected_objects:
            # Get the location of the active object
            location = active_object.location

        bpy.ops.object.empty_add(type='SINGLE_ARROW', align='WORLD', location=location, scale=(1, 1, 1))
        new_emitter = bpy.context.active_object
        new_emitter.name = "ProjectileEmitter"

        new_emitter.projectile_tool.valid_emitter = True

        # Apply a 90-degree rotation around the X-axis
        rotation_angle = math.radians(90)  # Convert degrees to radians
        new_emitter.rotation_euler.x = rotation_angle

        self.report({'INFO'}, "Projectile emitter created.")
        return {'FINISHED'}

class CreateLinkedEmitter(bpy.types.Operator):
    bl_idname = "object.create_linked_emitter"
    bl_label = "Create Linked Emitter"
    bl_description = "Add an emitter with linked settings to the selected emitter that will create projectiles in unison."

    def execute(self, context):

        main_emitter = bpy.context.active_object

        bpy.ops.scene.create_projectile_emitter()

        new_emitter = bpy.context.active_object
        new_emitter.projectile_tool.child_emitter = True

        added_emitter = main_emitter.projectile_tool.linked_emitters.add()
        added_emitter.linked_emitter = new_emitter

        added_emitter.linked_emitter.projectile_tool.parent_emitter = main_emitter
    
        main_emitter.projectile_tool.sync(context)

        return {'FINISHED'}

class RecalculateProjectiles(bpy.types.Operator):
    bl_idname = "object.recalculate_projectiles"
    bl_label = "Update Simulation"
    bl_description = "Recalculate all projectiles created by this emitter. (for use when settings are changed, etc.)"


    def execute(self, context):
        source = bpy.context.object
        origin_frame = bpy.context.scene.frame_current

        projectile_frames =[]
        
        for frame in source.projectile_tool.projectile_frames:
            projectile_frames.append(frame.projectile_frame)

        bpy.ops.object.delete_all_projectiles()

        for item in projectile_frames:
            bpy.context.scene.frame_set(item)
            bpy.ops.object.create_projectile()


        bpy.context.scene.frame_set(origin_frame)
        return {'FINISHED'}



class DeleteAllProjectiles(bpy.types.Operator):
    bl_idname = "object.delete_all_projectiles"
    bl_label = "Clear Simulation"
    bl_description = "Delete all projectiles created by this emitter."

    def delete_emitters_projectiles(self, source, context):

        emitter_properties = source.projectile_tool

        # Create a list of objects to delete
        objects_to_delete = [obj_ref.instantiated_projectile for obj_ref in emitter_properties.instantiated_projectiles]
        objects_to_delete += [obj_ref.impact_decal for obj_ref in emitter_properties.impact_decals]

        # Clear the collection property
        emitter_properties.instantiated_projectiles.clear()
        emitter_properties.impact_decals.clear()
        emitter_properties.projectile_frames.clear()

        # Delete the objects from the scene
        for obj in objects_to_delete:
            bpy.data.objects.remove(obj, do_unlink=True)

        if emitter_properties.muzzlef_obj:
            bpy.data.objects.remove(emitter_properties.muzzlef_obj, do_unlink=True)

        self.report({'INFO'}, "All emitter's projectiles deleted.")
        return {'FINISHED'}
    

    def execute(self, context):

        selected_emitter = bpy.context.object

        self.delete_emitters_projectiles(selected_emitter, context)
        # Purge any linked emitters if they've been deleted
        for i, item in enumerate(selected_emitter.projectile_tool.linked_emitters):
            child = item.linked_emitter

            if not child or child.name not in context.scene.objects:
                selected_emitter.projectile_tool.linked_emitters.remove(i)
            else:
                self.delete_emitters_projectiles(child, context)
        
        return {'FINISHED'}


class DeleteLinkedEmitter(bpy.types.Operator):
    bl_idname = "object.delete_linked_emitter"
    bl_label = "Remove"
    bl_description = "Deletes this linked emitter along with all it's simulated objects"

    def execute(self, context):
        if context.object.projectile_tool.child_emitter is False:
            return {'CANCELLED'}
        
        coll =  context.object.projectile_tool.parent_emitter.projectile_tool.linked_emitters
        i = 0
        for item in coll:
            if item.linked_emitter == context.object:
                coll.remove(i)
            i += 1

        bpy.ops.object.delete_all_projectiles()
        bpy.data.objects.remove(context.object, do_unlink=True)

        return {'FINISHED'}

