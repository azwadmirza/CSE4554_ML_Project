    def visit_instance(self, t: Instance, from_fallback: bool = False) -> Type:
        """This visitor method tracks situations like this:

               x: A  # When analyzing this type we will get an Instance from SemanticAnalyzerPass1.
                     # Now we need to update this to actual analyzed TupleType.
               class A(NamedTuple):
                   attr: str

        If from_fallback is True, then we always return an Instance type. This is needed
        since TupleType and TypedDictType fallbacks are always instances.
        """
        info = t.type
        # Special case, analyzed bases transformed the type into TupleType.
        if info.tuple_type and not from_fallback:
            items = [it.accept(self) for it in info.tuple_type.items]
            info.tuple_type.items = items
            return TupleType(items, Instance(info, []))
        # Update forward Instances to corresponding analyzed NamedTuples.
        if info.replaced and info.replaced.tuple_type:
            tp = info.replaced.tuple_type
            if self.check_recursion(tp):
                # The key idea is that when we recursively return to a type already traversed,
                # then we break the cycle and put AnyType as a leaf.
                return AnyType(TypeOfAny.from_error)
            return tp.copy_modified(fallback=Instance(info.replaced, [],
                                                      line=t.line)).accept(self)
        # Same as above but for TypedDicts.
        if info.replaced and info.replaced.typeddict_type:
            td = info.replaced.typeddict_type
            if self.check_recursion(td):
                # We also break the cycles for TypedDicts as explained above for NamedTuples.
                return AnyType(TypeOfAny.from_error)
            return td.copy_modified(fallback=Instance(info.replaced, [],
                                                      line=t.line)).accept(self)
        if self.check_recursion(t):
            # We also need to break a potential cycle with normal (non-synthetic) instance types.
            return Instance(t.type, [AnyType(TypeOfAny.from_error)] * len(t.type.defn.type_vars),
                            line=t.line)
        return super().visit_instance(t)