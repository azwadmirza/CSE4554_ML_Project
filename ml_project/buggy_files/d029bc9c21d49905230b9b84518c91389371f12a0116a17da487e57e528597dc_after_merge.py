    def check_method_override_for_base_with_name(
            self, defn: Union[FuncDef, OverloadedFuncDef, Decorator],
            name: str, base: TypeInfo) -> bool:
        """Check if overriding an attribute `name` of `base` with `defn` is valid.

        Return True if the supertype node was not analysed yet, and `defn` was deferred.
        """
        base_attr = base.names.get(name)
        if base_attr:
            # The name of the method is defined in the base class.

            # Point errors at the 'def' line (important for backward compatibility
            # of type ignores).
            if not isinstance(defn, Decorator):
                context = defn
            else:
                context = defn.func

            # Construct the type of the overriding method.
            if isinstance(defn, (FuncDef, OverloadedFuncDef)):
                typ = self.function_type(defn)  # type: Type
                override_class_or_static = defn.is_class or defn.is_static
            else:
                assert defn.var.is_ready
                assert defn.var.type is not None
                typ = defn.var.type
                override_class_or_static = defn.func.is_class or defn.func.is_static
            if isinstance(typ, FunctionLike) and not is_static(context):
                typ = bind_self(typ, self.scope.active_self_type())
            # Map the overridden method type to subtype context so that
            # it can be checked for compatibility.
            original_type = base_attr.type
            original_node = base_attr.node
            if original_type is None:
                if self.pass_num < self.last_pass:
                    # If there are passes left, defer this node until next pass,
                    # otherwise try reconstructing the method type from available information.
                    self.defer_node(defn, defn.info)
                    return True
                elif isinstance(original_node, (FuncDef, OverloadedFuncDef)):
                    original_type = self.function_type(original_node)
                elif isinstance(original_node, Decorator):
                    original_type = self.function_type(original_node.func)
                else:
                    assert False, str(base_attr.node)
            if isinstance(original_node, (FuncDef, OverloadedFuncDef)):
                original_class_or_static = original_node.is_class or original_node.is_static
            elif isinstance(original_node, Decorator):
                fdef = original_node.func
                original_class_or_static = fdef.is_class or fdef.is_static
            else:
                original_class_or_static = False  # a variable can't be class or static
            if isinstance(original_type, AnyType) or isinstance(typ, AnyType):
                pass
            elif isinstance(original_type, FunctionLike) and isinstance(typ, FunctionLike):
                if (isinstance(base_attr.node, (FuncDef, OverloadedFuncDef, Decorator))
                        and not is_static(base_attr.node)):
                    bound = bind_self(original_type, self.scope.active_self_type())
                else:
                    bound = original_type
                original = map_type_from_supertype(bound, defn.info, base)
                # Check that the types are compatible.
                # TODO overloaded signatures
                self.check_override(typ,
                                    cast(FunctionLike, original),
                                    defn.name(),
                                    name,
                                    base.name(),
                                    original_class_or_static,
                                    override_class_or_static,
                                    context)
            elif is_equivalent(original_type, typ):
                # Assume invariance for a non-callable attribute here. Note
                # that this doesn't affect read-only properties which can have
                # covariant overrides.
                #
                # TODO: Allow covariance for read-only attributes?
                pass
            else:
                self.msg.signature_incompatible_with_supertype(
                    defn.name(), name, base.name(), context)
        return False