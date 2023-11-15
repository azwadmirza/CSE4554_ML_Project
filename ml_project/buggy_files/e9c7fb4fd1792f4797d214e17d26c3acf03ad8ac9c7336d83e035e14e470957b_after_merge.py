    def _get_referrers(
        self,
        scls: so.Object,
        *,
        scls_type: Optional[Type[so.Object_T]] = None,
        field_name: Optional[str] = None,
    ) -> FrozenSet[so.Object_T]:

        try:
            refs = self._refs_to[scls.id]
        except KeyError:
            return frozenset()
        else:
            referrers: Set[so.Object] = set()

            if scls_type is not None:
                if field_name is not None:
                    for (st, fn), ids in refs.items():
                        if issubclass(st, scls_type) and fn == field_name:
                            referrers.update(
                                self.get_by_id(objid) for objid in ids)
                else:
                    for (st, _), ids in refs.items():
                        if issubclass(st, scls_type):
                            referrers.update(
                                self.get_by_id(objid) for objid in ids)
            elif field_name is not None:
                for (_, fn), ids in refs.items():
                    if fn == field_name:
                        referrers.update(
                            self.get_by_id(objid) for objid in ids)
            else:
                refids = itertools.chain.from_iterable(refs.values())
                referrers.update(self.get_by_id(objid) for objid in refids)

            return frozenset(referrers)  # type: ignore