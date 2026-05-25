"""
Blender Add-on Event Handlers
Hooks for Blender events to track state changes
"""

import bpy
from datetime import datetime


_last_state = {}
_last_selection = set()
_last_mode = None


def on_scene_update(context=None):
    """Handler for scene updates (load factory, etc.)"""
    print(f"🔄 Scene updated at {datetime.now().isoformat()}")
    
    # Reset tracking state
    global _last_state, _last_selection, _last_mode
    _last_state = {}
    _last_selection = set()
    _last_mode = None


def on_selection_change(context=None):
    """Handler for selection changes"""
    if context is None:
        context = bpy.context
    
    current_selection = set(obj.name for obj in context.selected_objects)
    
    if current_selection != _last_selection:
        print(f"🎯 Selection changed: {len(current_selection)} objects")
        _last_selection = current_selection
        
        # Could trigger state send here if needed


def on_mode_change(context=None):
    """Handler for mode changes (Object, Edit, Sculpt, etc.)"""
    if context is None:
        context = bpy.context
    
    active_obj = context.active_object
    if not active_obj:
        return
    
    current_mode = active_obj.mode
    
    if current_mode != _last_mode:
        print(f"🔧 Mode changed: {_last_mode} → {current_mode}")
        _last_mode = current_mode
        
        # Trigger immediate state update on mode change
        from . import send_blender_state, is_connected
        if is_connected:
            send_blender_state()


def on_depsgraph_update(context=None):
    """Handler for dependency graph updates (general scene changes)"""
    if context is None:
        context = bpy.context
    
    # Check for mode changes
    active_obj = context.active_object
    if active_obj:
        current_mode = active_obj.mode
        if current_mode != _last_mode:
            on_mode_change(context)
    
    # Check for selection changes
    current_selection = set(obj.name for obj in context.selected_objects)
    if current_selection != _last_selection:
        on_selection_change(context)


def register_handlers():
    """Register all event handlers"""
    if on_depsgraph_update not in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.append(on_depsgraph_update)
    
    if on_scene_update not in bpy.app.handlers.load_factory_startup_post:
        bpy.app.handlers.load_factory_startup_post.append(on_scene_update)
    
    print("✅ Event handlers registered")


def unregister_handlers():
    """Unregister all event handlers"""
    if on_depsgraph_update in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.remove(on_depsgraph_update)
    
    if on_scene_update in bpy.app.handlers.load_factory_startup_post:
        bpy.app.handlers.load_factory_startup_post.remove(on_scene_update)
    
    print("👋 Event handlers unregistered")
