from pathlib import Path
from typing import Any

import streamlit.components.v1 as components

_component = components.declare_component(
    "dashboard_chart_builder",
    path=str(Path(__file__).parent / "components" / "chart_builder"),
)


def drag_drop(items: list[dict[str, Any]], reset_key: int, key: str) -> list[dict[str, Any]]:
    """Render a native drag-and-drop board and return its current containers."""
    return _component(items=items, resetKey=reset_key, default=items, key=key)
