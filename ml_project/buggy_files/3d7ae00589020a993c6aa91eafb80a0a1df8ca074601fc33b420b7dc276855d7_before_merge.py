    def get_referrers_ex(
        self,
        scls: so.Object,
    ) -> Dict[
        Tuple[Type[so.Object], str],
        FrozenSet[so.Object],
    ]:
        try:
            refs = self._refs_to[scls.id]
        except KeyError:
            return {}
        else:
            result = {}

            for (st, fn), ids in refs.items():
                result[st, fn] = frozenset(
                    self.get_by_id(objid) for objid in ids)

            return result