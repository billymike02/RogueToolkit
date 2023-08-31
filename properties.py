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

        print("sellers")


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

class LaserEmitterProperties(bpy.types.PropertyGroup):

    instantiated_lasers: bpy.props.CollectionProperty(type=LaserPointer)

    laser_obj: bpy.props.PointerProperty(
        name = "Laser Object",
        description = "Object to instantiate as laser.",
        type=bpy.types.Object
    )

    laser_velocity: bpy.props.FloatProperty(
        name = "Laser Velocity",
        description = "Velocity of lasers created by emitter.",
        default = 1.0,
        min = 1.0
    )

    laser_lifetime: bpy.props.IntProperty(
        name = "Laser Lifetime",
        description = "How long the laser will 'exist' within the scene.",
        default = 50,
        min = 1
    )

    laser_scale: bpy.props.FloatVectorProperty(
        name = "Laser Scale",
        description = "The scale of the lasers to be instantiated.",
        default = (1.0, 1.0, 1.0),
    )

    toggle_collision: bpy.props.BoolProperty(
        name = "Toggle Collision",
        description = "Sets whether or not laser should be destroyed when colliding with another object.",
        default = True
    )

    toggle_sparks: bpy.props.BoolProperty(
        name = "Toggle Sparks",
        description = "Set whether or not the laser should create sparks on impact.",
        default = True
    )

    toggle_decals: bpy.props.BoolProperty(
        name = "Toggle Decals",
        description = "Set whether or not physical markers are made where the laser impacts objects.",
        default = True
    )

    decal_scale: bpy.props.FloatVectorProperty(
        name = "Decal Scale",
        description = "Size that decals will be made.",
        default = (0.1, 0.1, 0.1)
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



