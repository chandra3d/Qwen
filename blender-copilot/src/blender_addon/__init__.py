bl_info = {
    "name": "AI Copilot",
    "author": "Blender AI Copilot Team",
    "version": (0, 1, 0),
    "blender": (4, 5, 0),
    "location": "View3D > Sidebar > AI Copilot",
    "description": "Real-time AI assistant that understands your Blender workflow",
    "category": "Interface",
}

import bpy
import json
import threading
import websocket
from datetime import datetime
from .operators import (
    COPILLOT_OT_connect,
    COPILLOT_OT_disconnect,
    COPILLOT_OT_send_context,
    COPILLOT_OT_ask_ai
)
from .panels import (
    COPILLOT_PT_main_panel,
    COPILLOT_PT_status_panel,
    COPILLOT_PT_settings_panel
)
from .handlers import (
    on_scene_update,
    on_selection_change,
    on_mode_change,
    on_depsgraph_update
)


# Global WebSocket connection
ws_connection = None
ws_thread = None
is_connected = False
backend_url = "ws://localhost:8000/ws/blender"


class CopilotPreferences(bpy.types.AddonPreferences):
    """Addon preferences for AI Copilot"""
    
    bl_idname = __name__
    
    backend_host: bpy.props.StringProperty(
        name="Backend Host",
        description="Backend server host",
        default="localhost"
    )
    
    backend_port: bpy.props.IntProperty(
        name="Backend Port",
        description="Backend server port",
        default=8000,
        min=1,
        max=65535
    )
    
    auto_connect: bpy.props.BoolProperty(
        name="Auto Connect",
        description="Automatically connect to backend on startup",
        default=True
    )
    
    send_interval: bpy.props.FloatProperty(
        name="Send Interval",
        description="Interval in seconds to send state updates",
        default=1.0,
        min=0.1,
        max=10.0
    )
    
    def draw(self, context):
        layout = self.layout
        
        box = layout.box()
        box.label(text="Backend Settings:", icon='SERVER')
        box.prop(self, "backend_host")
        box.prop(self, "backend_port")
        box.prop(self, "auto_connect")
        box.prop(self, "send_interval")


def get_blender_state():
    """Capture current Blender state"""
    context = bpy.context
    
    # Get active object
    active_object = context.active_object
    active_obj_name = active_object.name if active_object else None
    active_obj_type = active_object.type if active_object else None
    
    # Get selected objects
    selected_objects = [obj.name for obj in context.selected_objects]
    
    # Get active mode
    active_mode = active_object.mode if active_object else 'OBJECT'
    
    # Get scene info
    scene = context.scene
    frame_current = scene.frame_current
    frame_start = scene.frame_start
    frame_end = scene.frame_end
    
    # Get viewport info
    workspace = context.workspace
    workspace_name = workspace.name if workspace else None
    
    # Count objects by type
    object_counts = {}
    for obj in bpy.data.objects:
        obj_type = obj.type
        object_counts[obj_type] = object_counts.get(obj_type, 0) + 1
    
    # Get render engine
    render_engine = scene.render.engine
    
    # Check if node editor is open
    has_node_editor = any(area.type == 'NODE_EDITOR' for area in context.screen.areas)
    
    # Get active modifiers (if object exists)
    modifiers = []
    if active_object and hasattr(active_object, 'modifiers'):
        modifiers = [mod.name for mod in active_object.modifiers]
    
    state = {
        "active_object": {
            "name": active_obj_name,
            "type": active_obj_type,
            "mode": active_mode,
            "modifiers": modifiers
        },
        "selected_objects": selected_objects,
        "scene": {
            "name": scene.name,
            "frame_current": frame_current,
            "frame_start": frame_start,
            "frame_end": frame_end,
            "render_engine": render_engine
        },
        "workspace": {
            "name": workspace_name
        },
        "object_counts": object_counts,
        "has_node_editor": has_node_editor,
        "timestamp": datetime.now().isoformat()
    }
    
    return state


def ws_thread_func(url):
    """WebSocket thread function"""
    global ws_connection, is_connected
    
    def on_message(ws, message):
        data = json.loads(message)
        print(f"🤖 AI Copilot: {data}")
        
        # Handle AI responses
        if data.get("type") == "suggestion":
            # Show suggestion as notification
            suggestion = data.get("text", "")
            bpy.app.timers.register(lambda: show_notification(suggestion))
    
    def on_error(ws, error):
        print(f"WebSocket error: {error}")
        is_connected = False
    
    def on_close(ws, close_status_code, close_msg):
        print("WebSocket closed")
        is_connected = False
    
    def on_open(ws):
        print("✅ Connected to AI Copilot backend")
        is_connected = True
        # Send initial state
        send_blender_state(ws)
    
    ws_connection = websocket.WebSocketApp(
        url,
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )
    
    ws_connection.run_forever()


def send_blender_state(ws=None):
    """Send current Blender state to backend"""
    global ws_connection, is_connected
    
    if not is_connected:
        return
    
    ws_to_use = ws if ws else ws_connection
    
    if ws_to_use:
        try:
            state = get_blender_state()
            ws_to_use.send(json.dumps(state))
        except Exception as e:
            print(f"Error sending state: {e}")


def show_notification(message):
    """Show notification in Blender"""
    bpy.context.window_manager.popup_menu(
        lambda self, context: self.layout.label(text=message[:200]),
        title="AI Copilot Suggestion",
        icon='INFO'
    )


# Store timer for periodic updates
update_timer_handle = None


def update_timer():
    """Periodic update timer"""
    global is_connected
    
    if is_connected:
        send_blender_state()
    
    # Return interval for next call (in seconds)
    prefs = bpy.context.preferences.addons[__name__].preferences
    return prefs.send_interval


classes = (
    CopilotPreferences,
    COPILLOT_OT_connect,
    COPILLOT_OT_disconnect,
    COPILLOT_OT_send_context,
    COPILLOT_OT_ask_ai,
    COPILLOT_PT_main_panel,
    COPILLOT_PT_status_panel,
    COPILLOT_PT_settings_panel,
)


def register():
    """Register addon"""
    for cls in classes:
        bpy.utils.register_class(cls)
    
    # Register handlers
    bpy.app.handlers.depsgraph_update_post.append(on_depsgraph_update)
    bpy.app.handlers.load_factory_startup_post.append(on_scene_update)
    
    print("✅ AI Copilot addon registered")


def unregister():
    """Unregister addon"""
    global update_timer_handle, ws_connection, is_connected
    
    # Stop timer
    if update_timer_handle:
        bpy.app.timers.unregister(update_timer_handle)
        update_timer_handle = None
    
    # Disconnect WebSocket
    if ws_connection:
        ws_connection.close()
        ws_connection = None
    
    is_connected = False
    
    # Unregister handlers
    if on_depsgraph_update in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.remove(on_depsgraph_update)
    if on_scene_update in bpy.app.handlers.load_factory_startup_post:
        bpy.app.handlers.load_factory_startup_post.remove(on_scene_update)
    
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    
    print("👋 AI Copilot addon unregistered")


if __name__ == "__main__":
    register()
