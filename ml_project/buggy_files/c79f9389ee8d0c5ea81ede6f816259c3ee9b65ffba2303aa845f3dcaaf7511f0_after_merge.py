    def visit_instance(self, left: Instance) -> bool:
        right = self.right
        if isinstance(right, Instance):
            if TypeState.is_cached_subtype_check(self._subtype_kind, left, right):
                return True
            if not self.ignore_promotions:
                for base in left.type.mro:
                    if base._promote and self._is_proper_subtype(base._promote, right):
                        TypeState.record_subtype_cache_entry(self._subtype_kind, left, right)
                        return True

            if left.type.has_base(right.type.fullname()):
                def check_argument(leftarg: Type, rightarg: Type, variance: int) -> bool:
                    if variance == COVARIANT:
                        return self._is_proper_subtype(leftarg, rightarg)
                    elif variance == CONTRAVARIANT:
                        return self._is_proper_subtype(rightarg, leftarg)
                    else:
                        return mypy.sametypes.is_same_type(leftarg, rightarg)
                # Map left type to corresponding right instances.
                left = map_instance_to_supertype(left, right.type)
                if self.erase_instances:
                    erased = erase_type(left)
                    assert isinstance(erased, Instance)
                    left = erased

                nominal = all(check_argument(ta, ra, tvar.variance) for ta, ra, tvar in
                              zip(left.args, right.args, right.type.defn.type_vars))
                if nominal:
                    TypeState.record_subtype_cache_entry(self._subtype_kind, left, right)
                return nominal
            if (right.type.is_protocol and
                    is_protocol_implementation(left, right, proper_subtype=True)):
                return True
            return False
        if isinstance(right, CallableType):
            call = find_member('__call__', left, left, is_operator=True)
            if call:
                return self._is_proper_subtype(call, right)
            return False
        return False