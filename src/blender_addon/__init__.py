bl_info = {
    "name": "AI Copilot",
    "author": "Blender AI Copilot Team",
    "version": (0, 1, 0),
    "blender": (4, 5, 0),
    "location": "View3D > Sidebar > AI Copilot",
    "description": "Multimodal AI assistant for Blender workflow",
    "category": "Interface",
}

import bpy
import json
import threading
import websocket
from bpy.types import Panel, Operator, PropertyGroup
from bpy.props import StringProperty, BoolProperty, IntProperty
from bpy.app.handlers import persistent


# Global connection state
ws_connection = None
connection_thread = None
is_connected = False


class AICopilotProperties(PropertyGroup):
    """AI Copilot properties"""
    server_url: StringProperty(
        name="Server URL",
        default="ws://localhost:8000/ws"
    )
    auto_connect: BoolProperty(
        name="Auto Connect",
        default=False
    )
    is_recording: BoolProperty(
        name="Recording",
        default=False
    )
    session_id: StringProperty(
        name="Session ID",
        default=""
    )


def ws_on_message(ws, message):
    """Handle WebSocket messages"""
    try:
        data = json.loads(message)
        print(f"[AI Copilot] Received: {data}")
    except Exception as e:
        print(f"[AI Copilot] Message error: {e}")


def ws_on_error(ws, error):
    """Handle WebSocket errors"""
    print(f"[AI Copilot] Error: {error}")


def ws_on_close(ws, close_status_code, close_msg):
    """Handle WebSocket close"""
    global is_connected
    is_connected = False
    print("[AI Copilot] Disconnected")


def ws_on_open(ws):
    """Handle WebSocket open"""
    global is_connected
    is_connected = True
    print("[AI Copilot] Connected to server")


def connect_websocket(url):
    """Connect to WebSocket server"""
    global ws_connection
    
    try:
        ws_connection = websocket.WebSocketApp(
            url,
            on_message=ws_on_message,
            on_error=ws_on_error,
            on_close=ws_on_close,
            on_open=ws_on_open
        )
        
        ws_connection.run_forever()
    except Exception as e:
        print(f"[AI Copilot] Connection error: {e}")


def send_event(event_type: str, data: dict):
    """Send event to server"""
    global ws_connection, is_connected
    
    if ws_connection and is_connected:
        try:
            message = {
                "type": event_type,
                "data": data,
                "id": bpy.context.scene.frame_current
            }
            ws_connection.send(json.dumps(message))
        except Exception as e:
            print(f"[AI Copilot] Send error: {e}")


class AICOPILLOT_OT_connect(Operator):
    """Connect to AI Copilot server"""
    bl_idname = "ai_copilot.connect"
    bl_label = "Connect to Server"
    
    def execute(self, context):
        global connection_thread, ws_connection
        
        props = context.scene.ai_copilot
        url = props.server_url
        
        if connection_thread and connection_thread.is_alive():
            self.report({'WARNING'}, "Already connecting")
            return {'CANCELLED'}
        
        # Start connection thread
        connection_thread = threading.Thread(
            target=connect_websocket,
            args=(url,),
            daemon=True
        )
        connection_thread.start()
        
        self.report({'INFO'}, f"Connecting to {url}")
        return {'FINISHED'}


class AICOPILLOT_OT_disconnect(Operator):
    """Disconnect from AI Copilot server"""
    bl_idname = "ai_copilot.disconnect"
    bl_label = "Disconnect"
    
    def execute(self, context):
        global ws_connection, is_connected
        
        if ws_connection:
            ws_connection.close()
            ws_connection = None
        
        is_connected = False
        self.report({'INFO'}, "Disconnected")
        return {'FINISHED'}


class AICOPILLOT_OT_start_session(Operator):
    """Start AI recording session"""
    bl_idname = "ai_copilot.start_session"
    bl_label = "Start Session"
    
    def execute(self, context):
        global is_connected
        
        if not is_connected:
            self.report({'WARNING'}, "Not connected to server")
            return {'CANCELLED'}
        
        props = context.scene.ai_copilot
        props.is_recording = True
        
        # Send start session event
        send_event("session_start", {
            "blender_version": ".".join(map(str, bpy.app.version)),
            "project_name": bpy.path.display_name_from_filepath(bpy.data.filepath) or "Untitled"
        })
        
        self.report({'INFO'}, "Session started")
        return {'FINISHED'}


class AICOPILLOT_OT_stop_session(Operator):
    """Stop AI recording session"""
    bl_idname = "ai_copilot.stop_session"
    bl_label = "Stop Session"
    
    def execute(self, context):
        props = context.scene.ai_copilot
        props.is_recording = False
        
        # Send stop session event
        send_event("session_stop", {})
        
        self.report({'INFO'}, "Session stopped")
        return {'FINISHED'}


class AICOPILLOT_OT_send_state(Operator):
    """Send current Blender state to server"""
    bl_idname = "ai_copilot.send_state"
    bl_label = "Send State"
    
    def execute(self, context):
        # Gather Blender state
        selected_objects = [obj.name for obj in context.selected_objects]
        active_object = context.active_object.name if context.active_object else ""
        active_mode = context.active_object.mode if context.active_object else ""
        
        state_data = {
            "selected_objects": selected_objects,
            "active_object": active_object,
            "active_mode": active_mode,
            "scene_name": context.scene.name,
            "frame_current": context.scene.frame_current,
            "render_engine": context.scene.render.engine,
            "object_count": len(bpy.data.objects),
            "vertex_count": sum(len(obj.data.vertices) for obj in bpy.data.objects if obj.type == 'MESH')
        }
        
        send_event("blender_state", state_data)
        
        self.report({'INFO'}, "State sent")
        return {'FINISHED'}


class AICOPILLOT_PT_main_panel(Panel):
    """Main AI Copilot panel"""
    bl_label = "AI Copilot"
    bl_idname = "AICOPILLOT_PT_main_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "AI Copilot"
    
    def draw(self, context):
        layout = self.layout
        props = context.scene.ai_copilot
        
        # Connection section
        box = layout.box()
        box.label(text="Connection", icon='NETWORK_DRIVE')
        row = box.row()
        row.prop(props, "server_url", text="")
        
        row = box.row(align=True)
        if is_connected:
            row.operator("ai_copilot.disconnect", icon='DISCONNECT', text="Disconnect")
        else:
            row.operator("ai_copilot.connect", icon='CONNECT', text="Connect")
        
        # Status indicator
        status_row = box.row()
        status_row.enabled = False
        if is_connected:
            status_row.label(text="● Connected", icon='CHECKMARK')
        else:
            status_row.label(text="○ Disconnected")
        
        # Session section
        box = layout.box()
        box.label(text="Session", icon='RECORD_ON')
        
        if props.is_recording:
            box.label(text=f"Session: {props.session_id or 'Active'}", icon='REC')
            box.operator("ai_copilot.stop_session", icon='STOP', text="Stop Recording")
        else:
            box.operator("ai_copilot.start_session", icon='REC', text="Start Recording")
        
        # State section
        box = layout.box()
        box.label(text="State", icon='PREFERENCES')
        box.operator("ai_copilot.send_state", icon='EXPORT', text="Send Current State")
        
        # Info section
        box = layout.box()
        box.label(text="Info", icon='INFO')
        box.label(text=f"Blender: {'.'.join(map(str, bpy.app.version))}")
        box.label(text=f"Objects: {len(bpy.data.objects)}")
        
        if context.active_object:
            box.label(text=f"Active: {context.active_object.name}")
            box.label(text=f"Mode: {context.active_object.mode}")


@persistent
def load_handler(dummy):
    """Called when Blender loads a file"""
    send_event("file_loaded", {
        "filepath": bpy.data.filepath
    })


@persistent
def save_handler(dummy):
    """Called when Blender saves a file"""
    send_event("file_saved", {
        "filepath": bpy.data.filepath
    })


@persistent
def frame_change_handler(scene):
    """Called on frame change"""
    props = scene.ai_copilot
    
    if props.is_recording and is_connected:
        send_event("frame_change", {
            "frame": scene.frame_current
        })


classes = (
    AICopilotProperties,
    AICOPILLOT_OT_connect,
    AICOPILLOT_OT_disconnect,
    AICOPILLOT_OT_start_session,
    AICOPILLOT_OT_stop_session,
    AICOPILLOT_OT_send_state,
    AICOPILLOT_PT_main_panel,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
    bpy.types.Scene.ai_copilot = bpy.props.PointerProperty(type=AICopilotProperties)
    
    # Register handlers
    bpy.app.handlers.load_post.append(load_handler)
    bpy.app.handlers.save_post.append(save_handler)
    bpy.app.handlers.frame_change_pre.append(frame_change_handler)
    
    print("✓ AI Copilot add-on registered")


def unregister():
    # Unregister handlers
    bpy.app.handlers.load_post.remove(load_handler)
    bpy.app.handlers.save_post.remove(save_handler)
    bpy.app.handlers.frame_change_pre.remove(frame_change_handler)
    
    del bpy.types.Scene.ai_copilot
    
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    
    print("✓ AI Copilot add-on unregistered")


if __name__ == "__main__":
    register()
