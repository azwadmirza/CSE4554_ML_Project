    def check_compatibility(self, name: str, base1: TypeInfo,
                            base2: TypeInfo, ctx: Context) -> None:
        """Check if attribute name in base1 is compatible with base2 in multiple inheritance.

        Assume base1 comes before base2 in the MRO, and that base1 and base2 don't have
        a direct subclass relationship (i.e., the compatibility requirement only derives from
        multiple inheritance).
        """
        if name == '__init__':
            # __init__ can be incompatible -- it's a special case.
            return
        first = base1[name]
        second = base2[name]
        first_type = first.type
        if first_type is None and isinstance(first.node, FuncDef):
            first_type = self.function_type(cast(FuncDef, first.node))
        second_type = second.type
        if second_type is None and isinstance(second.node, FuncDef):
            second_type = self.function_type(cast(FuncDef, second.node))
        # TODO: What if some classes are generic?
        if (isinstance(first_type, FunctionLike) and
                isinstance(second_type, FunctionLike)):
            # Method override
            first_sig = method_type(cast(FunctionLike, first_type))
            second_sig = method_type(cast(FunctionLike, second_type))
            ok = is_subtype(first_sig, second_sig)
        elif first_type and second_type:
            ok = is_equivalent(first_type, second_type)
        else:
            if first_type is None:
                self.msg.cannot_determine_type_in_base(name, base1.name(), ctx)
            if second_type is None:
                self.msg.cannot_determine_type_in_base(name, base2.name(), ctx)
            ok = True
        if not ok:
            self.msg.base_class_definitions_incompatible(name, base1, base2,
                                                         ctx)