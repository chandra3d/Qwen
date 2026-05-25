"""
Blender Add-on Panels
UI panels for AI Copilot in Blender sidebar
"""

import bpy
from . import is_connected


class COPILLOT_PT_main_panel(bpy.types.Panel):
    """Main AI Copilot panel in 3D View sidebar"""
    
    bl_idname = "COPILLOT_PT_main_panel"
    bl_label = "AI Copilot"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "AI Copilot"
    
    def draw(self, context):
        layout = self.layout
        
        # Connection status
        box = layout.box()
        row = box.row()
        row.label(text="Connection Status:")
        
        if is_connected:
            row.label(text="● Connected", icon='CHECKMARK')
        else:
            row.label(text="○ Disconnected", icon='DOT')
        
        # Connection buttons
        row = box.row(align=True)
        row.operator("copilot.connect", icon='PLUGIN')
        row.operator("copilot.disconnect", icon='UNLINKED')
        
        # Quick actions
        layout.separator()
        layout.label(text="Quick Actions:", icon='ACTION')
        
        col = layout.column(align=True)
        col.operator("copilot.send_context", icon='OUTLINER_OB_LIGHT')
        col.operator("copilot.ask_ai", icon='QUESTION')


class COPILLOT_PT_status_panel(bpy.types.Panel):
    """Status panel showing current context"""
    
    bl_idname = "COPILLOT_PT_status_panel"
    bl_label = "Current Context"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "AI Copilot"
    bl_parent_id = "COPILLOT_PT_main_panel"
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self, context):
        layout = self.layout
        
        # Active object
        active_obj = context.active_object
        box = layout.box()
        box.label(text="Active Object:", icon='OBJECT_DATA')
        
        if active_obj:
            box.label(text=f"  Name: {active_obj.name}")
            box.label(text=f"  Type: {active_obj.type}")
            box.label(text=f"  Mode: {active_obj.mode}")
            
            # Modifiers
            if active_obj.modifiers:
                box.label(text=f"  Modifiers: {len(active_obj.modifiers)}")
        else:
            box.label(text="  No active object")
        
        # Selection info
        selected_count = len(context.selected_objects)
        layout.label(text=f"Selected: {selected_count} objects", icon='RESTRICT_SELECT_OFF')
        
        # Scene info
        scene = context.scene
        layout.label(text=f"Frame: {scene.frame_current}", icon='TIME')


class COPILLOT_PT_settings_panel(bpy.types.Panel):
    """Settings panel for AI Copilot"""
    
    bl_idname = "COPILLOT_PT_settings_panel"
    bl_label = "Settings"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "AI Copilot"
    bl_parent_id = "COPILLOT_PT_main_panel"
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self, context):
        layout = self.layout
        
        # Get addon preferences
        prefs = context.preferences.addons[__package__].preferences
        
        box = layout.box()
        box.label(text="Backend Settings:", icon='SERVER')
        box.prop(prefs, "backend_host")
        box.prop(prefs, "backend_port")
        
        box = layout.box()
        box.label(text="Update Settings:", icon='FILE_REFRESH')
        box.prop(prefs, "auto_connect")
        box.prop(prefs, "send_interval")
