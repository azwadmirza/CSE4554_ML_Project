    def add_new_node_to_model_class(self, name: str, typ: MypyType) -> None:
        var = self.create_new_var(name, typ)
        self.model_classdef.info.names[name] = SymbolTableNode(MDEF, var, plugin_generated=True)