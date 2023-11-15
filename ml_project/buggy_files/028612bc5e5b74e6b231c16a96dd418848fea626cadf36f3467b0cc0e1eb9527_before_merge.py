    def visit_instance(self, inst: Instance) -> None:
        # TODO: Combine Instances that are exactly the same?
        type_ref = inst.type_ref
        if type_ref is None:
            return  # We've already been here.
        del inst.type_ref
        node = lookup_qualified(self.modules, type_ref, self.quick_and_dirty)
        if isinstance(node, TypeInfo):
            inst.type = node
            # TODO: Is this needed or redundant?
            # Also fix up the bases, just in case.
            for base in inst.type.bases:
                if base.type is NOT_READY:
                    base.accept(self)
        for a in inst.args:
            a.accept(self)