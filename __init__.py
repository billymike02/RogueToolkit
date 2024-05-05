import bpy
from RogueToolkit.operators import *
from RogueToolkit.panels import *
from RogueToolkit.properties import *

# to create and edit a multifile blender addon, make the git repository take place in the addons folder of the blender application (in %appdata%)

def delete_obj(scene):
    pass
    # print("Updating depsgraph...")

    # for obj in scene.objects:
    #     # Check if the object is in your custom collection property
    #     if obj.projectile_tool and obj.projectile_tool.valid_emitter:
    #         # Purge any linked emitters if they've been deleted
    #         for i, item in enumerate(obj.projectile_tool.linked_emitters):
    #             child = item.linked_emitter

    #             if not child or child.name not in scene.objects:
    #                 obj.projectile_tool.linked_emitters.remove(i)


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
    AttachToPath, 
    CreateFlightPlan, 
    CreateLightspeedJump, 
    CreateLightspeedReturn, 
    SimplePanel,
    ProjectileCreator,
    WorldPanel, 
    MiscCreator,
    SimulateFlakField,
    CreateFlakField,
    DeleteFlakField,
    CreateStarfield,
    CreateProjectileEmitter, 
    CreateProjectile,
    CreateLinkedEmitter,
    DeleteAllProjectiles,
    RiggingProperties,
    SceneProperties,
    ProjectilePointer,
    ImpactDecalPointer,
    LinkedEmitterPointer,
    FlakExplosionPointer,
    FlakFieldProperties,
    ProjectileFrame,
    CollisionFlashPointer,
    ProjectileEmitterProperties,
    RecalculateProjectiles,
    DeleteLinkedEmitter
    ]


addon_keymaps = []

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
    bpy.types.Object.rigging_tool = bpy.props.PointerProperty(type=RiggingProperties) # save custom properties
    bpy.types.Scene.scene_tool = bpy.props.PointerProperty(type=SceneProperties)
    bpy.types.Object.projectile_tool = bpy.props.PointerProperty(type=ProjectileEmitterProperties)
    bpy.types.Object.flakfield_tool = bpy.props.PointerProperty(type=FlakFieldProperties)

    # Add the hotkey
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        km = wm.keyconfigs.addon.keymaps.new(name='3D View', space_type='VIEW_3D')
        kmi = km.keymap_items.new(CreateProjectile.bl_idname, type='K', value='PRESS', ctrl=False)
        addon_keymaps.append((km, kmi))

    bpy.app.handlers.depsgraph_update_post.append(delete_obj)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    
    del bpy.types.Object.rigging_tool # delete custom properties
    del bpy.types.Scene.scene_tool
    del bpy.types.Object.projectile_tool

    # Remove the hotkey
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()

if __name__ == "__main__":
    register()
