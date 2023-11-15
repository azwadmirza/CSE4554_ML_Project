    def get_referrers_ex(
        self,
        scls: so.Object,
        *,
        scls_type: Optional[Type[so.Object_T]] = None,
    ) -> Dict[
        Tuple[Type[so.Object_T], str],
        FrozenSet[so.Object_T],
    ]:
        try:
            refs = self._refs_to[scls.id]
        except KeyError:
            return {}
        else:
            result = {}

            if scls_type is not None:
                for (st, fn), ids in refs.items():
                    if issubclass(st, scls_type):
                        result[st, fn] = frozenset(
                            self.get_by_id(objid) for objid in ids)
            else:
                for (st, fn), ids in refs.items():
                    result[st, fn] = frozenset(  # type: ignore
                        self.get_by_id(objid) for objid in ids)

            return result  # type: ignore