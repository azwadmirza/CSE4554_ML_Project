    def assign_type(self, expr: Expression,
                    type: Type,
                    declared_type: Optional[Type],
                    restrict_any: bool = False) -> None:
        if not isinstance(expr, BindableTypes):
            return None
        if not literal(expr):
            return
        self.invalidate_dependencies(expr)

        if declared_type is None:
            # Not sure why this happens.  It seems to mainly happen in
            # member initialization.
            return
        if not is_subtype(type, declared_type):
            # Pretty sure this is only happens when there's a type error.

            # Ideally this function wouldn't be called if the
            # expression has a type error, though -- do other kinds of
            # errors cause this function to get called at invalid
            # times?
            return

        enclosing_type = self.most_recent_enclosing_type(expr, type)
        if (isinstance(enclosing_type, AnyType)
                and not restrict_any):
            # If x is Any and y is int, after x = y we do not infer that x is int.
            # This could be changed.
            if not isinstance(type, AnyType):
                # We narrowed type from Any in a recent frame (probably an
                # isinstance check), but now it is reassigned, so broaden back
                # to Any (which is the most recent enclosing type)
                self.put(expr, enclosing_type)
        elif (isinstance(type, AnyType)
              and not (isinstance(declared_type, UnionType)
                       and any(isinstance(item, AnyType) for item in declared_type.items))):
            # Assigning an Any value doesn't affect the type to avoid false negatives, unless
            # there is an Any item in a declared union type.
            self.put(expr, declared_type)
        else:
            self.put(expr, type)

        for i in self.try_frames:
            # XXX This should probably not copy the entire frame, but
            # just copy this variable into a single stored frame.
            self.allow_jump(i)