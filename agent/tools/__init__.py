import importlib
import inspect
import pkgutil
from typing import Iterable, Type, List

from agent.tools.base import Tool, ToolRegistry


# built lazily on first use (avoid import cost and circularity)
_BUILTIN_TOOLS: dict[str, Type[Tool]] | None = None

def discovery_tool_classes() -> Iterable[Type[Tool]]:
    """Yield every concrete (instantiable) tool subclass in this package

    Abstract base classes are skipped
    """
    for module_info in pkgutil.iter_modules(__path__):
        module = importlib.import_module(f"{__name__}.{module_info.name}")
        for _, obj in inspect.getmembers(module, inspect.isclass):
            if (issubclass(obj, Tool)
                and obj is not Tool
                and not inspect.isabstract(obj)
            ):
                yield obj

def _try_instantiate(cls: Type[Tool]) -> Tool | None:
    try:
        return cls()
    except TypeError:
        pass

    create = getattr(cls, "create", None)
    if callable(create):
        try:
            return cls.create()
        except TypeError:
            pass
    return None


def create_default_tool() -> List[Tool]:
    tools: List[Tool] = []
    seen_names: set[str] = set()

    for cls in discovery_tool_classes():
        tool = _try_instantiate(cls)
        if tool is None:
            continue
        if tool.name in seen_names:
            continue
        seen_names.add(tool.name)
        tools.append(tool)
    return tools


def resolve_tool(name: str) -> Type[Tool]:
    global _BUILTIN_TOOLS
    if _BUILTIN_TOOLS is None:
        _BUILTIN_TOOLS = {t.name: type(t) for t in create_default_tool()}
    cls = _BUILTIN_TOOLS.get(name)
    if cls is None:
        raise KeyError(f"Unknown tool: {name!r} available: {sorted(_BUILTIN_TOOLS.keys())}")
    return cls
