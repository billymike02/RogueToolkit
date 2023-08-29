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

# define custom properties
class MyProperties(bpy.types.PropertyGroup):
    
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

class SceneProperties(bpy.types.PropertyGroup):
    
    starfield: bpy.props.PointerProperty(
    name = "Starfield",
    description = "Reference to generated starfield shader.",
    type = bpy.types.World
    )

