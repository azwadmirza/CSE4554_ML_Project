    def check_method_or_accessor_override_for_base(self, defn: Union[FuncBase, Decorator],
                                                   base: TypeInfo) -> None:
        """Check if method definition is compatible with a base class."""
        if base:
            name = defn.name()
            base_attr = base.names.get(name)
            if base_attr:
                # First, check if we override a final (always an error, even with Any types).
                if is_final_node(base_attr.node):
                    self.msg.cant_override_final(name, base.name(), defn)
                # Second, final can't override anything writeable independently of types.
                if defn.is_final:
                    self.check_no_writable(name, base_attr.node, defn)

            # Check the type of override.
            if name not in ('__init__', '__new__', '__init_subclass__'):
                # Check method override
                # (__init__, __new__, __init_subclass__ are special).
                self.check_method_override_for_base_with_name(defn, name, base)
                if name in nodes.inplace_operator_methods:
                    # Figure out the name of the corresponding operator method.
                    method = '__' + name[3:]
                    # An inplace operator method such as __iadd__ might not be
                    # always introduced safely if a base class defined __add__.
                    # TODO can't come up with an example where this is
                    #      necessary; now it's "just in case"
                    self.check_method_override_for_base_with_name(defn, method,
                                                                  base)