    def get_referrers_ex(
        self,
        scls: so.Object,
    ) -> Dict[
        Tuple[Type[so.Object], str],
        FrozenSet[so.Object],
    ]:
        base = self._base_schema.get_referrers_ex(scls)
        top = self._top_schema.get_referrers_ex(scls)
        return {
            k: base.get(k, frozenset()) | top.get(k, frozenset())
            for k in itertools.chain(base, top)
        }