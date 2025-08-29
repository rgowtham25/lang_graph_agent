# mcp_clients.py code from earlier answer
from __future__ import annotations
from typing import Dict, Any, Callable, List

# Registry maps server -> ability_name -> function
class MCPRegistry:
    def __init__(self):
        self.registry = {"COMMON": {}, "ATLAS": {}}

    def register(self, server: str, name: str, fn: Callable):
        self.registry.setdefault(server, {})[name] = fn

    def call(self, server: str, name: str, state: Dict[str, Any], log: List[str]) -> Dict[str, Any]:
        fn = self.registry[server][name]
        return fn(state, log)

COMMON = "COMMON"
ATLAS = "ATLAS"
