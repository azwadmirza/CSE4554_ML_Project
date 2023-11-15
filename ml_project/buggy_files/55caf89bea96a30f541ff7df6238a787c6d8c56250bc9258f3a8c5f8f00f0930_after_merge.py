    def get_referrers_ex(
        self,
        scls: so.Object,
        *,
        scls_type: Optional[Type[so.Object_T]] = None,
    ) -> Dict[
        Tuple[Type[so.Object_T], str],
        FrozenSet[so.Object_T],
    ]:
        base = self._base_schema.get_referrers_ex(scls, scls_type=scls_type)
        top = self._top_schema.get_referrers_ex(scls, scls_type=scls_type)
        return {
            k: base.get(k, frozenset()) | top.get(k, frozenset())
            for k in itertools.chain(base, top)
        }