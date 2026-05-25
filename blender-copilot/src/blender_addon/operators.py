"""
Blender Add-on Operators
UI buttons and actions for AI Copilot
"""

import bpy
import json
import threading


class COPILLOT_OT_connect(bpy.types.Operator):
    """Connect to AI Copilot backend"""
    
    bl_idname = "copilot.connect"
    bl_label = "Connect to Backend"
    bl_description = "Connect to the AI Copilot backend server"
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        from . import ws_thread_func, backend_url, is_connected, ws_thread
        
        if is_connected:
            self.report({'INFO'}, "Already connected")
            return {'CANCELLED'}
        
        prefs = context.preferences.addons[__package__].preferences
        url = f"ws://{prefs.backend_host}:{prefs.backend_port}/ws/blender"
        
        # Start WebSocket thread
        ws_thread = threading.Thread(target=ws_thread_func, args=(url,), daemon=True)
        ws_thread.start()
        
        self.report({'INFO'}, "Connecting to backend...")
        return {'FINISHED'}


class COPILLOT_OT_disconnect(bpy.types.Operator):
    """Disconnect from AI Copilot backend"""
    
    bl_idname = "copilot.disconnect"
    bl_label = "Disconnect"
    bl_description = "Disconnect from the AI Copilot backend server"
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        from . import ws_connection, is_connected
        
        if not is_connected or not ws_connection:
            self.report({'INFO'}, "Not connected")
            return {'CANCELLED'}
        
        ws_connection.close()
        
        self.report({'INFO'}, "Disconnected from backend")
        return {'FINISHED'}


class COPILLOT_OT_send_context(bpy.types.Operator):
    """Send current Blender state to backend"""
    
    bl_idname = "copilot.send_context"
    bl_label = "Send Context"
    bl_description = "Manually send current Blender state to the AI"
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        from . import send_blender_state, is_connected
        
        if not is_connected:
            self.report({'WARNING'}, "Not connected to backend")
            return {'CANCELLED'}
        
        send_blender_state()
        self.report({'INFO'}, "Context sent")
        return {'FINISHED'}


class COPILLOT_OT_ask_ai(bpy.types.Operator):
    """Ask AI for help with current context"""
    
    bl_idname = "copilot.ask_ai"
    bl_label = "Ask AI"
    bl_description = "Ask the AI for suggestions based on current context"
    bl_options = {'REGISTER'}
    
    question: bpy.props.StringProperty(
        name="Question",
        description="Your question for the AI",
        default=""
    )
    
    def execute(self, context):
        from . import ws_connection, is_connected, get_blender_state
        
        if not is_connected or not ws_connection:
            self.report({'WARNING'}, "Not connected to backend")
            return {'CANCELLED'}
        
        # Get current state
        state = get_blender_state()
        
        # Send question with context
        message = {
            "type": "question",
            "question": self.question,
            "blender_state": state,
            "timestamp": str(bpy.context.scene.frame_current)
        }
        
        ws_connection.send(json.dumps(message))
        
        self.report({'INFO'}, "Question sent to AI")
        return {'FINISHED'}
    
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=400)
    
    def draw(self, context):
        layout = self.layout
        layout.prop(self, "question")
