import bpy


# Panel to be found in View 3D (hit 'n' in the viewport)
class SimplePanel(bpy.types.Panel):
    bl_idname = "VIEW3D_PT_simple_panel"
    bl_label = "Animation"
    bl_space_type = "VIEW_3D" # to be found in the side-menu in 3D view
    bl_region_type = "UI"
    bl_category = "Rogue Toolkit"

    def draw(self, context):
        
        layout = self.layout

        if context.object is None:
            layout = layout.label(text="Select an object.")
            return 
    
        
        rigging_tool = context.object.rigging_tool

        layout.label(text="Forward Axis")
        row = layout.row()
        row = row.prop(rigging_tool, "forward_axis", expand=True)
        row = layout.row()
        row.separator()
        
        # Paths and anim
        layout.label(text='Manual Effects')
        box = layout.box()
        row = box.row().label(text='Flight Animation')
        box.prop(rigging_tool, "path")
        row = box.row()
        row.operator("object.simple_operator", icon = "LINKED")
        
        if rigging_tool.path is None:
            row.enabled = False
            
        box.row().operator("object.create_flight_plan", icon = "STROKE")

        
        # Lightspeed
        layout.label(text="Auto Effects")
        box = layout.box()
        box.label(text="Lightspeed")
        box.row().prop(rigging_tool, "lightspeed_time")
        box.row().operator("object.create_lightspeed_jump", icon="EXPORT")
        box.row().operator("object.create_lightspeed_return", icon="IMPORT")

class MiscCreator(bpy.types.Panel):
    bl_idname = "VIEW3D_PT_misc_creator"
    bl_label = "Misc. Tools"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Rogue Toolkit"

    def draw(self, context):
        layout = self.layout

        active_object = bpy.context.active_object

        box = None
        
        if active_object is None or context.object.flakfield_tool.valid_flakfield is False:
            box = layout.box()
            box.label(text="Flak Field")
            row = box.row()
            row.operator("scene.create_flak_field", icon='CUBE')
            return

        flakfield_tool = context.object.flakfield_tool

        if (flakfield_tool.valid_flakfield is True):
            box = layout.box()
            row = box.row()
            row.prop(flakfield_tool, "explosion_scale")
            row = box.row()
            row.prop(flakfield_tool, "start_frame")
            row = box.row()
            row.prop(flakfield_tool, "end_frame")
            row = box.row()
            row.prop(flakfield_tool, "num_explosions")
            box = box.box()
            row = box.row()
            row.operator("object.simulate_flak_field", icon='SNAP_VOLUME')

        if (len(flakfield_tool.explosion_billboards) > 0):
            row = box.row()
            row.alert = True
            row.operator("object.delete_flak_field", icon = 'TRASH')

class ProjectileCreator(bpy.types.Panel):
    bl_idname = "VIEW3D_PT_projectile_creator"
    bl_label = "Projectile Simulation"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Rogue Toolkit"

    def draw(self, context):

        layout = self.layout
        
        selected_objects = bpy.context.selected_objects
        active_object = bpy.context.active_object

        if active_object is None or len(selected_objects) == 0 or active_object.projectile_tool.valid_emitter is False:
            row = layout.row()
            row.operator("scene.create_projectile_emitter", icon="ORIENTATION_NORMAL")
            return
        
        projectile_tool = context.object.projectile_tool
        
        if projectile_tool.child_emitter is True:
            row = layout.row()
            row.operator("object.delete_linked_emitter")
            row = layout.row()
            row.label(text="Parent Emitter: " + context.object.projectile_tool.parent_emitter.name)
        else:
            row = layout.row()
            row.prop(projectile_tool, "projectile_color")
            if projectile_tool.projectile_color == "Custom":
                row = layout.row()
                row.prop(projectile_tool, "custom_color")

            # row = layout.row()
            # row.prop(projectile_tool, "toggle_targeter")
            row = layout.row()
            row.prop(projectile_tool, "projectile_lifetime")
            row = layout.row()
            row.prop(projectile_tool, "projectile_scale")
            row = layout.row()
            row.prop(projectile_tool, "projectile_velocity")

            row = layout.row()
            row.prop(projectile_tool, "toggle_muzzlef")
            if projectile_tool.toggle_muzzlef is True:
                row = layout.row()
                row.prop(projectile_tool, "muzzlef_scale")
            
            row = layout.separator()
            box = layout.box()
            row = box.row()
            row.prop(projectile_tool, "toggle_collision")
            if projectile_tool.toggle_collision is True:
                box2 = box.box()
                box2.prop(projectile_tool, "toggle_decals")
                if projectile_tool.toggle_decals is True:
                    row = box2.row()
                    row.prop(projectile_tool, "decal_scale")
                row = box2.row()
                # row.prop(projectile_tool, "toggle_flash")
                # row = box.row()
                row.prop(projectile_tool, "toggle_explosion")
                if projectile_tool.toggle_explosion is True:
                    row = box2.row()
                    row.prop(projectile_tool, "explosion_scale")

            row = box.row()
            row.prop(projectile_tool, "toggle_flak")

            if projectile_tool.toggle_flak is True:
                row = box.row()
                row.prop(projectile_tool, "flak_scale")
                

            row = layout.separator()
            row = layout.row()
            row.prop(projectile_tool, "linked_emitters")
            row = layout.row()
            row.operator("object.create_linked_emitter", icon='LINKED')
            row = layout.separator()

            row = layout.row()
            row.operator("object.create_projectile", icon='SNAP_NORMAL')
            row = layout.row()
            row.operator("object.recalculate_projectiles", icon='FILE_REFRESH')
            row = layout.row()
            row.alert = True
            row.operator("object.delete_all_projectiles", icon = 'TRASH')

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
            