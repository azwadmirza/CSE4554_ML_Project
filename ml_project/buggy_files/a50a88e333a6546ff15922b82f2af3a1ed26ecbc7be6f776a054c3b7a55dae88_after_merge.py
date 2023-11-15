    def partition_by_callable(self, typ: Type,
                              unsound_partition: bool) -> Tuple[List[Type], List[Type]]:
        """Takes in a type and partitions that type into callable subtypes and
        uncallable subtypes.

        Thus, given:
        `callables, uncallables = partition_by_callable(type)`

        If we assert `callable(type)` then `type` has type Union[*callables], and
        If we assert `not callable(type)` then `type` has type Union[*uncallables]

        If unsound_partition is set, assume that anything that is not
        clearly callable is in fact not callable. Otherwise we generate a
        new subtype that *is* callable.

        Guaranteed to not return [], []

        """
        if isinstance(typ, FunctionLike) or isinstance(typ, TypeType):
            return [typ], []

        if isinstance(typ, AnyType):
            return [typ], [typ]

        if isinstance(typ, UnionType):
            callables = []
            uncallables = []
            for subtype in typ.relevant_items():
                # Use unsound_partition when handling unions in order to
                # allow the expected type discrimination.
                subcallables, subuncallables = self.partition_by_callable(subtype,
                                                                          unsound_partition=True)
                callables.extend(subcallables)
                uncallables.extend(subuncallables)
            return callables, uncallables

        if isinstance(typ, TypeVarType):
            # We could do better probably?
            # Refine the the type variable's bound as our type in the case that
            # callable() is true. This unfortuantely loses the information that
            # the type is a type variable in that branch.
            # This matches what is done for isinstance, but it may be possible to
            # do better.
            # If it is possible for the false branch to execute, return the original
            # type to avoid losing type information.
            callables, uncallables = self.partition_by_callable(typ.erase_to_union_or_bound(),
                                                                unsound_partition)
            uncallables = [typ] if len(uncallables) else []
            return callables, uncallables

        # A TupleType is callable if its fallback is, but needs special handling
        # when we dummy up a new type.
        ityp = typ
        if isinstance(typ, TupleType):
            ityp = typ.fallback

        if isinstance(ityp, Instance):
            method = ityp.type.get_method('__call__')
            if method and method.type:
                callables, uncallables = self.partition_by_callable(method.type,
                                                                    unsound_partition=False)
                if len(callables) and not len(uncallables):
                    # Only consider the type callable if its __call__ method is
                    # definitely callable.
                    return [typ], []

            if not unsound_partition:
                fake = self.make_fake_callable(ityp)
                if isinstance(typ, TupleType):
                    fake.type.tuple_type = TupleType(typ.items, fake)
                    return [fake.type.tuple_type], [typ]
                return [fake], [typ]

        if unsound_partition:
            return [], [typ]
        else:
            # We don't know how properly make the type callable.
            return [typ], [typ]