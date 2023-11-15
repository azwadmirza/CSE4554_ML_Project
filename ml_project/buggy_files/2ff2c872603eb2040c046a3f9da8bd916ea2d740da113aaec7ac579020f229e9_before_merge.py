    def add_unknown_symbol(self, name: str, context: Context, is_import: bool = False,
                           target_name: Optional[str] = None) -> None:
        var = Var(name)
        if self.options.logical_deps and target_name is not None:
            # This makes it possible to add logical fine-grained dependencies
            # from a missing module. We can't use this by default, since in a
            # few places we assume that the full name points to a real
            # definition, but this name may point to nothing.
            var._fullname = target_name
        elif self.type:
            var._fullname = self.type.fullname() + "." + name
        else:
            var._fullname = self.qualified_name(name)
        var.is_ready = True
        if is_import:
            any_type = AnyType(TypeOfAny.from_unimported_type, missing_import_name=var._fullname)
        else:
            any_type = AnyType(TypeOfAny.from_error)
        var.type = any_type
        var.is_suppressed_import = is_import
        self.add_symbol(name, SymbolTableNode(GDEF, var), context)