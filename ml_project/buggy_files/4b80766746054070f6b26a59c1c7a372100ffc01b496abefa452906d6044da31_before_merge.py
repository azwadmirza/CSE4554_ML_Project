    def get_referrers_ex(
        self,
        scls: so.Object,
    ) -> Dict[
        Tuple[Type[so.Object], str],
        FrozenSet[so.Object],
    ]:
        raise NotImplementedError