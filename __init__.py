import bpy
from RogueToolkit.operators import *
from RogueToolkit.panels import *
from RogueToolkit.properties import *

# to create and edit a multifile blender addon, make the git repository take place in the addons folder of the blender application

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
    WorldOperator, 
    MyProperties]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
    bpy.types.Object.my_tool = bpy.props.PointerProperty(type=MyProperties) # save custom properties

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    
    del bpy.types.Object.my_tool # delete custom properties

if __name__ == "__main__":
    register()
