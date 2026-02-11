# -*- coding: utf-8 -*-
import importlib.util
import os

_node_dir = os.path.dirname(os.path.abspath(__file__))

def _import_node_main():
    main_path = os.path.join(_node_dir, "Node_32_Reserved.py")
    if not os.path.exists(main_path):
        return None
    spec = importlib.util.spec_from_file_location(
        "Node_32_Reserved.main", main_path,
        submodule_search_locations=[_node_dir]
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

class FusionNode:
    def __init__(self):
        self.instance = None
        module = _import_node_main()
        if module and hasattr(module, "Node"):
            self.instance = module.Node()
            
    def execute(self, action, **kwargs):
        if self.instance:
            return self.instance.execute(action, **kwargs)
        return {"status": "error", "message": "Node not loaded"}

Node = FusionNode
