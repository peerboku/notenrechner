"""Session-level linear undo/redo stack.

Usage:
    import undo_stack
    undo_stack.push(action)   # after a user action completes
    undo_stack.undo()         # returns True if something was undone
    undo_stack.redo()         # returns True if something was redone
    undo_stack.clear()        # on class switch or destructive structural change
"""
from __future__ import annotations

_undo: list = []
_redo: list = []
_listeners: list = []   # callables notified whenever the stack changes


def add_listener(cb) -> None:
    """Register a callback that fires whenever the stack state changes."""
    _listeners.append(cb)


def _notify() -> None:
    for cb in _listeners:
        cb()


def push(action) -> None:
    """Record a completed action. Clears the redo stack (linear history)."""
    _undo.append(action)
    _redo.clear()
    _notify()


def undo() -> bool:
    """Undo the most recent action. Returns True if an action was undone."""
    if not _undo:
        return False
    action = _undo.pop()
    action.undo()
    _redo.append(action)
    _notify()
    return True


def redo() -> bool:
    """Redo the most recently undone action. Returns True if an action was redone."""
    if not _redo:
        return False
    action = _redo.pop()
    action.redo()
    _undo.append(action)
    _notify()
    return True


def clear() -> None:
    """Clear both stacks (call on class switch or after a destructive structural change)."""
    _undo.clear()
    _redo.clear()
    _notify()


def can_undo() -> bool:
    return bool(_undo)


def can_redo() -> bool:
    return bool(_redo)
