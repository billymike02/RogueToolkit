import bpy

# enumation to let the user decide the axis used for the 'Slave to Path' operator
forward_axis_options = [
    ("FORWARD_X", "X", "Forward along the X-axis"),
    ("FORWARD_Y", "Y", "Forward along the Y-axis"),
    ("FORWARD_Z", "Z", "Forward along the Z-axis"),
    ("TRACK_NEGATIVE_X", "-X", "Negative along the X-axis"),
    ("TRACK_NEGATIVE_Y", "-Y", "Negative along the Y-axis"),
    ("TRACK_NEGATIVE_Z", "-Z", "Negative along the Z-axis")
]

# TODO ensure that this is correct location
def path_selector(self, obj):
    return obj.type == 'CURVE'

class MyUpdateFunctions:

    @staticmethod
    def update_starfield_scale(self, context):
         # Update the color value in the world shader node tree
        world = bpy.context.scene.world
        nodes = world.node_tree.nodes

        # Find the ColorRamp node
        noise_node = None
        for node in nodes:
            if isinstance(node, bpy.types.ShaderNodeTexNoise):
                noise_node = node
                break

        noise_node.inputs['Scale'].default_value = context.scene.scene_tool.starfield_scale

    @staticmethod
    def update_star_color(self, context):
        
        # Update the color value in the world shader node tree
        world = bpy.context.scene.world
        nodes = world.node_tree.nodes

        # Find the ColorRamp node
        color_ramp_node = None
        for node in nodes:
            if isinstance(node, bpy.types.ShaderNodeValToRGB):
                color_ramp_node = node
                break

        second_element = color_ramp_node.color_ramp.elements[1]

        # Set the position of the first element to 0.7 (left marker)
        second_element.color = context.scene.scene_tool.star_color



# define custom properties
class RiggingProperties(bpy.types.PropertyGroup):
    
    path: bpy.props.PointerProperty(
        name = "Path",
        description = "what to slave to",
        type=bpy.types.Object,
        poll=path_selector
    )

    
    lightspeed_time: bpy.props.IntProperty(
        name = "Transition Length",
        description = "Number of frames for the object to transition to/from realspace.",
        default = 4
    )
    
    forward_axis: bpy.props.EnumProperty(
        name="Forward Axis",
        description="Choose the forward axis",
        items=forward_axis_options,
        default="FORWARD_X"
    )

class LaserPointer(bpy.types.PropertyGroup):
    instantiated_laser: bpy.props.PointerProperty(type=bpy.types.Object)

class ImpactDecalPointer(bpy.types.PropertyGroup):
    impact_decal: bpy.props.PointerProperty(type=bpy.types.Object)

class LinkedEmitterPointer(bpy.types.PropertyGroup):

    linked_emitter: bpy.props.PointerProperty(
        type=bpy.types.Object
    )

class LaserFrame(bpy.types.PropertyGroup):
    laser_frame: bpy.props.IntProperty(
        name="Laser Frame"
    )

class CollisionFlashPointer(bpy.types.PropertyGroup):

    collision_flash: bpy.props.PointerProperty(type=bpy.types.Object)

class LaserEmitterProperties(bpy.types.PropertyGroup):

    def update_callback(self, context):

        # print(self,": is trying to update and they're a:", self.child_emitter)

        # avoid updating if you're linked to a parent
        if self.child_emitter is True:
            return

        for child_sh in self.linked_emitters:
            linked_emitter = child_sh.linked_emitter

            # Synchronize all settings that you want to copy from parent to linked here.
            if linked_emitter.laser_tool.toggle_collision != self.toggle_collision:
                linked_emitter.laser_tool.toggle_collision = self.toggle_collision
            if linked_emitter.laser_tool.laser_scale != self.laser_scale:
                linked_emitter.laser_tool.laser_scale = self.laser_scale
            if linked_emitter.laser_tool.muzzlef_scale != self.muzzlef_scale:
                linked_emitter.laser_tool.muzzlef_scale = self.muzzlef_scale
            if linked_emitter.laser_tool.laser_obj != self.laser_obj:
                linked_emitter.laser_tool.laser_obj = self.laser_obj
            if linked_emitter.laser_tool.laser_velocity != self.laser_velocity:
                linked_emitter.laser_tool.laser_velocity = self.laser_velocity
            if linked_emitter.laser_tool.laser_lifetime != self.laser_lifetime:
                linked_emitter.laser_tool.laser_lifetime = self.laser_lifetime
            if linked_emitter.laser_tool.toggle_muzzlef != self.toggle_muzzlef:
                linked_emitter.laser_tool.toggle_muzzlef = self.toggle_muzzlef
            if linked_emitter.laser_tool.toggle_sparks != self.toggle_sparks:
                linked_emitter.laser_tool.toggle_sparks = self.toggle_sparks
            if linked_emitter.laser_tool.toggle_decals != self.toggle_decals:
                linked_emitter.laser_tool.toggle_decals = self.toggle_decals
            if linked_emitter.laser_tool.decal_scale != self.decal_scale:
                linked_emitter.laser_tool.decal_scale = self.decal_scale
            if linked_emitter.laser_tool.tracked_obj != self.tracked_obj:
                linked_emitter.laser_tool.tracked_obj = self.tracked_obj
            if linked_emitter.laser_tool.laser_color != self.laser_color:
                linked_emitter.laser_tool.laser_color = self.laser_color
            if linked_emitter.laser_tool.toggle_targeter != self.toggle_targeter:
                linked_emitter.laser_tool.toggle_targeter = self.toggle_targeter
            if linked_emitter.laser_tool.custom_color != self.custom_color:
                linked_emitter.laser_tool.custom_color = self.custom_color
            if linked_emitter.laser_tool.toggle_flash != self.toggle_flash:
                linked_emitter.laser_tool.toggle_flash = self.toggle_flash

        # print(self,"has updated its settings.")

    def update_color(self, context):

        if self.muzzlef_obj:
            if self.laser_color == "Red":
                self.muzzlef_obj.color = (1.0, 0, 0, 1.0)
            elif self.laser_color == "Blue":
                self.muzzlef_obj.color = (0, 0, 1.0, 1.0)
            elif self.laser_color == "Green":
                self.muzzlef_obj.color = (0, 1, 0, 1)
            elif self.laser_color == "Custom":
                self.muzzlef_obj.color = self.custom_color

        self.update_callback(context)

    instantiated_lasers: bpy.props.CollectionProperty(type=LaserPointer)

    impact_decals: bpy.props.CollectionProperty(type=ImpactDecalPointer)

    collision_flashes: bpy.props.CollectionProperty(type=CollisionFlashPointer)

    linked_emitters: bpy.props.CollectionProperty(type=LinkedEmitterPointer)

    laser_frames: bpy.props.CollectionProperty(type=LaserFrame)

    child_emitter: bpy.props.BoolProperty(
        default = False
    )

    parent_emitter: bpy.props.PointerProperty(
        name = "Parent Emitter",
        type = bpy.types.Object
    )

    valid_emitter: bpy.props.BoolProperty(
        default = False
    )

    muzzlef_obj: bpy.props.PointerProperty(
        name = "Muzzle Flash",
        description = "Reference to emitter's muzzle flash object.",
        type=bpy.types.Object
    )
    
    muzzlef_scale: bpy.props.FloatVectorProperty(
        name = "Muzzle Flash Scale",
        description = "Peak size of the muzzle flash (if enabled).",
        default = (1, 1, 1),
        update=update_callback
    )

    laser_obj: bpy.props.PointerProperty(
        name = "Laser Object",
        description = "Object to instantiate as laser.",
        type=bpy.types.Object,
        update=update_callback
    )

    laser_velocity: bpy.props.FloatProperty(
        name = "Laser Velocity",
        description = "Velocity of lasers created by emitter.",
        default = 1.0,
        min = 0.1,
        update=update_callback
    )

    laser_lifetime: bpy.props.IntProperty(
        name = "Laser Lifetime",
        description = "How long the laser will 'exist' within the scene.",
        default = 50,
        min = 1,
        update=update_callback
    )

    laser_scale: bpy.props.FloatVectorProperty(
        name = "Laser Scale",
        description = "The scale of the lasers to be instantiated.",
        default = (1.0, 1.0, 1.0),
        update=update_callback
    )

    toggle_collision: bpy.props.BoolProperty(
        name = "Collision",
        description = "Sets whether or not laser should be destroyed when colliding with another object.",
        default = True,
        update=update_callback
    )

    toggle_muzzlef: bpy.props.BoolProperty(
        name = "Muzzle Flash",
        description = "Toggle creation of muzzle flashes when the lasers are created by this emitter.",
        default = True,
        update=update_callback
    )

    toggle_sparks: bpy.props.BoolProperty(
        name = "Sparks",
        description = "Set whether or not the laser should create sparks on impact.",
        default = True,
        update=update_callback
    )

    toggle_decals: bpy.props.BoolProperty(
        name = "Decals",
        description = "Set whether or not physical markers are made where the laser impacts objects.",
        default = True,
        update=update_callback
    )

    decal_scale: bpy.props.FloatVectorProperty(
        name = "Decal Scale",
        description = "Size that decals will be made.",
        default = (1, 1, 1),
        update=update_callback
    )

    tracked_obj: bpy.props.PointerProperty(
        name = "Tracked Object",
        description = "Select the object for this emitter to track.",
        type=bpy.types.Object
    )

    # visuals
    toggle_targeter: bpy.props.BoolProperty(
        name = "Toggle Targeter",        
        description = "Set whetherl or not a visual assist will be drawn to help in aiming the emitter.",
        default = False
    )

    laser_color: bpy.props.EnumProperty(
        items=(
            ("Red", "Red", "Red Laser Color"),
            ("Green", "Green", "Green Laser Color"),
            ("Blue", "Blue", "Blue Laser Color"),
            ("Custom", "Custom", "Custom Laser Color"),
        ),
        name="Color",
        default="Red",
        description="Select color of the laser and it's muzzle flash.",
        update=update_color
    )

    custom_color : bpy.props.FloatVectorProperty(  
       name="Custom Color",
       subtype='COLOR',
       size=4,
       default=(1.0, 0, 0, 1),
       min=0.0, max=1.0,
       description="Select a custom color.",
       update=update_callback
    )

    toggle_flash: bpy.props.BoolProperty(
        name="Toggle Collision Flash",
        description="Enable a light flash when laser impacts an object.",
        default=True,
        update=update_callback
    )

class SceneProperties(bpy.types.PropertyGroup):

    starfield: bpy.props.PointerProperty(
        name = "Starfield",
        description = "Reference to generated starfield shader.",
        type = bpy.types.World
    )
    
    starfield_scale: bpy.props.FloatProperty(
        name = "Starfield Scale",
        description = "How large the stars within the starfield shoul be.",
        default = 1000,
        min = 0,
        update = MyUpdateFunctions.update_starfield_scale
    )

    star_color: bpy.props.FloatVectorProperty(
        name="Star Color",
        description = "Sets the color of the stars in the starfield. (Hint: to change the brightness of the stars change the 'Value' attribute)",
        subtype='COLOR',
        size=4,
        min=0.0,
        default=(1.0, 1.0, 1.0, 1.0),
        update=MyUpdateFunctions.update_star_color
    )



