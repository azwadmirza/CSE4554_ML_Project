    def visit_instance(self, left: Instance) -> bool:
        if left.type.fallback_to_any:
            if isinstance(self.right, NoneType):
                # NOTE: `None` is a *non-subclassable* singleton, therefore no class
                # can by a subtype of it, even with an `Any` fallback.
                # This special case is needed to treat descriptors in classes with
                # dynamic base classes correctly, see #5456.
                return False
            return True
        right = self.right
        if isinstance(right, TupleType) and mypy.typeops.tuple_fallback(right).type.is_enum:
            return self._is_subtype(left, mypy.typeops.tuple_fallback(right))
        if isinstance(right, Instance):
            if TypeState.is_cached_subtype_check(self._subtype_kind, left, right):
                return True
            if not self.ignore_promotions:
                for base in left.type.mro:
                    if base._promote and self._is_subtype(base._promote, self.right):
                        TypeState.record_subtype_cache_entry(self._subtype_kind, left, right)
                        return True
            rname = right.type.fullname()
            # Always try a nominal check if possible,
            # there might be errors that a user wants to silence *once*.
            if ((left.type.has_base(rname) or rname == 'builtins.object') and
                    not self.ignore_declared_variance):
                # Map left type to corresponding right instances.
                t = map_instance_to_supertype(left, right.type)
                nominal = all(self.check_type_parameter(lefta, righta, tvar.variance)
                              for lefta, righta, tvar in
                              zip(t.args, right.args, right.type.defn.type_vars))
                if nominal:
                    TypeState.record_subtype_cache_entry(self._subtype_kind, left, right)
                return nominal
            if right.type.is_protocol and is_protocol_implementation(left, right):
                return True
            return False
        if isinstance(right, TypeType):
            item = right.item
            if isinstance(item, TupleType):
                item = mypy.typeops.tuple_fallback(item)
            if is_named_instance(left, 'builtins.type'):
                return self._is_subtype(TypeType(AnyType(TypeOfAny.special_form)), right)
            if left.type.is_metaclass():
                if isinstance(item, AnyType):
                    return True
                if isinstance(item, Instance):
                    return is_named_instance(item, 'builtins.object')
        if isinstance(right, CallableType):
            # Special case: Instance can be a subtype of Callable.
            call = find_member('__call__', left, left, is_operator=True)
            if call:
                return self._is_subtype(call, right)
            return False
        else:
            return False