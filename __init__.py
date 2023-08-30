import bpy
from RogueToolkit.operators import *
from RogueToolkit.panels import *
from RogueToolkit.properties import *

# to create and edit a multifile blender addon, make the git repository take place in the addons folder of the blender application (in %appdata%)

# basic information
bl_info = {
    "name": "Rogue Toolkit",
    "author": "Billy Woodward",
    "version": (0, 0, 2),
    "blender": (3, 6, 1),
    "location": "View3D > Tools",
    "description": "An addon designed to assist artists in the creation of multifaceted sci-fi scenes within Blender.",
}

# keep track of all classes to register
classes = [
    SimpleOperator, 
    CreateFlightPlan, 
    CreateLightspeedJump, 
    CreateLightspeedReturn, 
    SimplePanel,
    LaserCreator,
    WorldPanel, 
    WorldOperator,
    CreateLaserEmitter, 
    CreateLaser,
    DeleteAllLasers,
    MyProperties,
    SceneProperties]


addon_keymaps = []

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
    bpy.types.Object.my_tool = bpy.props.PointerProperty(type=MyProperties) # save custom properties
    bpy.types.Scene.scene_tool = bpy.props.PointerProperty(type=SceneProperties)

    # Add the hotkey
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        km = wm.keyconfigs.addon.keymaps.new(name='3D View', space_type='VIEW_3D')
        kmi = km.keymap_items.new(CreateLaser.bl_idname, type='P', value='PRESS', ctrl=False)
        addon_keymaps.append((km, kmi))


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    
    del bpy.types.Object.my_tool # delete custom properties
    del bpy.types.Scene.scene_tool

    # Remove the hotkey
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()

if __name__ == "__main__":
    register()
