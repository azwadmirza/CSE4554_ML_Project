    def get_referrers_ex(
        self,
        scls: so.Object,
        *,
        scls_type: Optional[Type[so.Object_T]] = None,
    ) -> Dict[
        Tuple[Type[so.Object_T], str],
        FrozenSet[so.Object_T],
    ]:
        raise NotImplementedError