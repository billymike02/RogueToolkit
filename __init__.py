import bpy
from ProjectOrion.operators import *
from ProjectOrion.panels import *
from ProjectOrion.properties import *

# basic information
bl_info = {
    "name": "Project Orion",
    "author": "Billy Woodward",
    "version": (0, 0, 1),
    "blender": (3, 3, 1),
    "location": "View3D > Tools",
    "description": "A simple addon",
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
