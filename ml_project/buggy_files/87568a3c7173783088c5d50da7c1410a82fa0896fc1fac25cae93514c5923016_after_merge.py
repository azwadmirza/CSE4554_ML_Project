    def add_new_node_to_model_class(self, name: str, typ: MypyType) -> None:
        helpers.add_new_sym_for_info(self.model_classdef.info,
                                     name=name,
                                     sym_type=typ)