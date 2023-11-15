    def check_method_override_for_base_with_name(
            self, defn: FuncBase, name: str, base: TypeInfo) -> None:
        base_attr = base.names.get(name)
        if base_attr:
            # The name of the method is defined in the base class.

            # Construct the type of the overriding method.
            typ = self.method_type(defn)
            # Map the overridden method type to subtype context so that
            # it can be checked for compatibility.
            original_type = base_attr.type
            if original_type is None:
                if isinstance(base_attr.node, FuncDef):
                    original_type = self.function_type(base_attr.node)
                elif isinstance(base_attr.node, Decorator):
                    original_type = self.function_type(base_attr.node.func)
                else:
                    assert False, str(base_attr.node)
            if isinstance(original_type, FunctionLike):
                original = map_type_from_supertype(
                    method_type(original_type),
                    defn.info, base)
                # Check that the types are compatible.
                # TODO overloaded signatures
                self.check_override(typ,
                                    cast(FunctionLike, original),
                                    defn.name(),
                                    name,
                                    base.name(),
                                    defn)
            else:
                self.msg.signature_incompatible_with_supertype(
                    defn.name(), name, base.name(), defn)