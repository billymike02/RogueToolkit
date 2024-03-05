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

class ProjectilePointer(bpy.types.PropertyGroup):
    instantiated_projectile: bpy.props.PointerProperty(type=bpy.types.Object)

class ImpactDecalPointer(bpy.types.PropertyGroup):
    impact_decal: bpy.props.PointerProperty(type=bpy.types.Object)

class FlakExplosionPointer(bpy.types.PropertyGroup):
    explosion_billboard: bpy.props.PointerProperty(type=bpy.types.Object)

class LinkedEmitterPointer(bpy.types.PropertyGroup):

    linked_emitter: bpy.props.PointerProperty(
        type=bpy.types.Object
    )

class ProjectileFrame(bpy.types.PropertyGroup):
    projectile_frame: bpy.props.IntProperty(
        name="Projectile Frame"
    )

class CollisionFlashPointer(bpy.types.PropertyGroup):

    collision_flash: bpy.props.PointerProperty(type=bpy.types.Object)

class FlakFieldProperties(bpy.types.PropertyGroup):

    def update_callback(self, context):
        if self.end_frame <= self.start_frame + 1:
            self.end_frame = self.start_frame + 1
    


    explosion_billboards: bpy.props.CollectionProperty(type=FlakExplosionPointer)

    valid_flakfield: bpy.props.BoolProperty(default=False)

    num_explosions: bpy.props.IntProperty(
        name="Number of Explosions",
        description="The number of explosions to occur within the field",
        default = 10,
        min = 1
    )

    explosion_scale: bpy.props.FloatProperty(
        name="Explosion Scale",
        description="Scale of the explosions within the field",
        default=1,
        min=0.01
    )


    start_frame: bpy.props.IntProperty(
        name="Start Frame",
        description="The frame to start the flak field simulation on.",
        default = 1,
        update = update_callback
    )

    end_frame: bpy.props.IntProperty(
        name="End Frame",
        description="The frame to end the flak field simulation on.",
        default = 100,
        update = update_callback
    )

class ProjectileEmitterProperties(bpy.types.PropertyGroup):

    def update_callback(self, context):

        # avoid updating if you're linked to a parent
        if self.child_emitter is True:
            return

        for child_sh in self.linked_emitters:

            if child_sh.name not in bpy.data.objects:
                item_to_remove = None

                for i, item in enumerate(self.linked_emitters):
                    # Example condition: remove the item with the name 'item_name'
                    if item.name == child_sh.name:
                        item_to_remove = i
                        break

                if item_to_remove is not None:
                    self.linked_emitters.remove(item_to_remove)

                continue


            linked_emitter = child_sh.linked_emitter

            attributes = dir(linked_emitter.projectile_tool)

            for attribute in attributes:

                if not isinstance(getattr(self, attribute), bpy.props.CollectionProperty):
                    try:
                        setattr(linked_emitter.projectile_tool, attribute, getattr(self, attribute))
                    except:
                        pass # some things can't be updated and that's fine

        # print(self,"has updated its settings.")

    def update_color(self, context):

        if self.muzzlef_obj:
            if self.projectile_color == "Red":
                self.muzzlef_obj.color = (1.0, 0, 0, 1.0)
            elif self.projectile_color == "Blue":
                self.muzzlef_obj.color = (0, 0, 1.0, 1.0)
            elif self.projectile_color == "Green":
                self.muzzlef_obj.color = (0, 1, 0, 1)
            elif self.projectile_color == "Custom":
                self.muzzlef_obj.color = self.custom_color

        self.update_callback(context)

    instantiated_projectiles: bpy.props.CollectionProperty(type=ProjectilePointer)

    impact_decals: bpy.props.CollectionProperty(type=ImpactDecalPointer)

    collision_flashes: bpy.props.CollectionProperty(type=CollisionFlashPointer)

    linked_emitters: bpy.props.CollectionProperty(
        type=LinkedEmitterPointer)

    projectile_frames: bpy.props.CollectionProperty(type=ProjectileFrame)

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
        name = "Animate Muzzle Flash",
        description = "Reference to emitter's muzzle flash object.",
        type=bpy.types.Object
    )
    
    muzzlef_scale: bpy.props.FloatProperty(
        name = "Muzzle Flash Scale",
        description = "Peak size of the muzzle flash (if enabled).",
        default =  1,
        update=update_callback
    )

    projectile_obj: bpy.props.PointerProperty(
        name = "Projectile Object",
        description = "Object to instantiate as projectile.",
        type=bpy.types.Object,
        update=update_callback
    )

    projectile_velocity: bpy.props.FloatProperty(
        name = "Velocity",
        description = "Velocity of projectiles created by emitter.",
        default = 1.0,
        min = 0.1,
        update=update_callback
    )

    projectile_lifetime: bpy.props.IntProperty(
        name = "Lifetime",
        description = "How long the projectile will 'exist' within the scene.",
        default = 50,
        min = 1,
        update=update_callback
    )

    projectile_scale: bpy.props.FloatProperty(
        name = "Scale",
        description = "The scale of the projectiles to be instantiated.",
        default = 1,
        update=update_callback
    )

    toggle_collision: bpy.props.BoolProperty(
        name = "Enable Collision",
        description = "Sets whether or not projectile should be destroyed when colliding with another object.",
        default = True,
        update=update_callback
    )

    toggle_muzzlef: bpy.props.BoolProperty(
        name = "Muzzle Flash",
        description = "Toggle creation of muzzle flashes when the projectiles are created by this emitter.",
        default = True,
        update=update_callback
    )

    toggle_sparks: bpy.props.BoolProperty(
        name = "Sparks",
        description = "Set whether or not the projectile should create sparks on impact.",
        default = True,
        update=update_callback
    )

    toggle_decals: bpy.props.BoolProperty(
        name = "Draw Impact Marks",
        description = "Set whether or not physical markers are made where the projectile impacts objects.",
        default = True,
        update=update_callback
    )

    decal_scale: bpy.props.FloatProperty(
        name = "Decal Scale",
        description = "Size that decals will be made.",
        default =  1,
        update=update_callback
    )

    explosion_scale: bpy.props.FloatProperty(
        name = "Billboard Scale",
        description = "Size that explosions will be made.",
        default = 1,
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

    projectile_color: bpy.props.EnumProperty(
        items=(
            ("Red", "Red", "Red Projectile Color"),
            ("Green", "Green", "Green Projectile Color"),
            ("Blue", "Blue", "Blue Projectile Color"),
            ("Custom", "Custom", "Custom Projectile Color"),
        ),
        name="Color",
        default="Red",
        description="Select color of the projectile and it's muzzle flash.",
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
        name="Flash on Impact",
        description="Enable a light flash when projectile impacts an object",
        default=True,
        update=update_callback
    )

    toggle_explosion: bpy.props.BoolProperty(
        name="Explode on Impact",
        description="Enable an explosion billboard when projectile impacts an object",
        default=False,
        update=update_callback
    )

    toggle_flak: bpy.props.BoolProperty(
        name="Toggle Flak",
        description="Enable an explosion at the termination point of each projectile",
        default=True,
        update=update_callback
    )

    flak_scale: bpy.props.FloatProperty(
    name="Flak Scale",
    description='Scale of the flak sprite',
    default=1,
    min=0.01
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



