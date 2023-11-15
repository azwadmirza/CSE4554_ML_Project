    def process_newtype_declaration(self, s: AssignmentStmt) -> None:
        """Check if s declares a NewType; if yes, store it in symbol table."""
        # Extract and check all information from newtype declaration
        name, call = self.analyze_newtype_declaration(s)
        if name is None or call is None:
            return

        old_type = self.check_newtype_args(name, call, s)
        call.analyzed = NewTypeExpr(name, old_type, line=call.line)
        if old_type is None:
            return

        # Create the corresponding class definition if the aliased type is subtypeable
        if isinstance(old_type, TupleType):
            newtype_class_info = self.build_newtype_typeinfo(name, old_type, old_type.fallback)
            newtype_class_info.tuple_type = old_type
        elif isinstance(old_type, Instance):
            if old_type.type.is_protocol:
                self.fail("NewType cannot be used with protocol classes", s)
            newtype_class_info = self.build_newtype_typeinfo(name, old_type, old_type)
        else:
            message = "Argument 2 to NewType(...) must be subclassable (got {})"
            self.fail(message.format(self.msg.format(old_type)), s)
            return

        check_for_explicit_any(old_type, self.options, self.is_typeshed_stub_file, self.msg,
                               context=s)

        if 'unimported' in self.options.disallow_any and has_any_from_unimported_type(old_type):
            self.msg.unimported_type_becomes_any("Argument 2 to NewType(...)", old_type, s)

        # If so, add it to the symbol table.
        node = self.lookup(name, s)
        if node is None:
            self.fail("Could not find {} in current namespace".format(name), s)
            return
        # TODO: why does NewType work in local scopes despite always being of kind GDEF?
        node.kind = GDEF
        call.analyzed.info = node.node = newtype_class_info