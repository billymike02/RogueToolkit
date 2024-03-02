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
        
        rigging_tool = context.object.rigging_tool
        
        # Paths and anim
        layout.prop(rigging_tool, "path")
        row = layout.row()
        row.operator("object.simple_operator", icon = "LINKED")
        
        if rigging_tool.path is None:
            row.enabled = False
            
        layout.row().operator("object.create_flight_plan", icon = "STROKE")
        layout.label(text="Forward Axis")
        layout.row().prop(rigging_tool, "forward_axis", expand=True)
        
        # Lightspeed
        layout.label(text="Quick Effects")
        box = layout.box()
        box.label(text="Lightspeed")
        box.row().prop(rigging_tool, "lightspeed_time")
        box.row().operator("object.create_lightspeed_jump", icon="EXPORT")
        box.row().operator("object.create_lightspeed_return", icon="IMPORT")

class LaserCreator(bpy.types.Panel):
    bl_idname = "VIEW3D_PT_laser_creator"
    bl_label = "Lasers"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Rogue Toolkit"

    def draw(self, context):

        layout = self.layout
        
        selected_objects = bpy.context.selected_objects
        active_object = bpy.context.active_object

        if active_object is None or len(selected_objects) == 0 or active_object.laser_tool.valid_emitter is False:
            row = layout.row()
            row.operator("scene.create_laser_emitter")
            return
        
        laser_tool = context.object.laser_tool
        
        if laser_tool.child_emitter is True:
            row = layout.row()
            row.operator("object.delete_linked_emitter")
            row = layout.row()
            row.label(text="Parent Emitter: " + context.object.laser_tool.parent_emitter.name)
        else:
            row = layout.row()
            row.prop(laser_tool, "laser_color")
            if laser_tool.laser_color == "Custom":
                row = layout.row()
                row.prop(laser_tool, "custom_color")

            row = layout.row()
            row.prop(laser_tool, "toggle_targeter")
            row = layout.row()
            row.prop(laser_tool, "laser_lifetime")
            row = layout.row()
            row.prop(laser_tool, "laser_scale")
            row = layout.row()
            row.prop(laser_tool, "laser_velocity")

            row = layout.separator()
            row = layout.row()
            row.prop(laser_tool, "toggle_muzzlef")
            if laser_tool.toggle_muzzlef is True:
                box = layout.box()
                box.prop(laser_tool, "muzzlef_scale")
            row = layout.separator()

            row = layout.separator()
            row = layout.row()
            row.prop(laser_tool, "toggle_collision")
            if laser_tool.toggle_collision is True:
                box = layout.box()
                box.prop(laser_tool, "toggle_decals")
                row = box.row()
                row.prop(laser_tool, "decal_scale")
                row = box.row()
                row.prop(laser_tool, "toggle_flash")
                row = box.row()
                row.prop(laser_tool, "toggle_explosion")
                row = box.row()
                row.prop(laser_tool, "explosion_scale")

            row = layout.separator()
            row = layout.row()
            row.prop(laser_tool, "linked_emitters")
            row = layout.row()
            row.operator("object.create_linked_emitter")
            row = layout.separator()

            row = layout.row()
            row.operator("object.create_laser")
            row = layout.row()
            row.operator("object.recalculate_lasers")
            row = layout.row()
            row.alert = True
            row.operator("object.delete_all_lasers", icon = 'TRASH')

class WorldPanel(bpy.types.Panel):
    bl_idname = "PROPERTIES_PT_world_panel"
    bl_label = "Rogue Toolkit"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = 'world'

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
            