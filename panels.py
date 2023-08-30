import bpy


# Panel to be found in View 3D (hit 'n' in the viewport)
class SimplePanel(bpy.types.Panel):
    bl_idname = "VIEW3D_PT_simple_panel"
    bl_label = "Rigging"
    bl_space_type = "VIEW_3D" # to be found in the side-menu in 3D view
    bl_region_type = "UI"
    bl_category = "Rogue Toolkit"

    def draw(self, context):
        
        if context.object is None:
            return
        
        layout = self.layout
        
        my_tool = context.object.my_tool
        
        # Paths and anim
        layout.prop(my_tool, "path")
        row = layout.row()
        row.operator("object.simple_operator", icon = "LINKED")
        
        if my_tool.path is None:
            row.enabled = False
            
        layout.row().operator("object.create_flight_plan", icon = "STROKE")
        layout.label(text="Forward Axis")
        layout.row().prop(my_tool, "forward_axis", expand=True)
        
        # Lightspeed
        layout.label(text="Animation")
        box = layout.box()
        box.label(text="Lightspeed")
        box.row().prop(my_tool, "lightspeed_time")
        box.row().operator("object.create_lightspeed_jump", icon="EXPORT")
        box.row().operator("object.create_lightspeed_return", icon="IMPORT")
        
        # World
        layout.row().operator("scene.create_starfield", icon = "SORTBYEXT")

class LaserCreator(bpy.types.Panel):
    bl_idname = "VIEW3D_PT_laser_creator"
    bl_label = "Lasers"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Rogue Toolkit"

    def draw(self, context):
        scene_tool = context.scene.scene_tool
        layout = self.layout

        row = layout.row()
        row.operator("scene.create_laser_emitter")
        row = layout.row()
        row.operator("scene.delete_all_lasers")

class WorldPanel(bpy.types.Panel):
    bl_idname = "PROPERTIES_PT_world_panel"
    bl_label = "Rogue Toolkit"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"

    def draw(self, context):

        layout = self.layout
        # World
        row = layout.row()
        row.operator("scene.create_starfield", icon = "SORTBYEXT")

        if context.scene.scene_tool.starfield:
            row.enabled = False

        row = layout.row()
        row.prop(context.scene.scene_tool, "starfield_scale")
        row = layout.row()
        row.prop(context.scene.scene_tool, "star_color")
            