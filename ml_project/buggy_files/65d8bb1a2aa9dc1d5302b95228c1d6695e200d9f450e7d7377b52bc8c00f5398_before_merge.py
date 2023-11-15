    def __init__(
        self,
        axis: Index,
        groupings: Sequence["grouper.Grouping"],
        sort: bool = True,
        group_keys: bool = True,
        mutated: bool = False,
        indexer: Optional[np.ndarray] = None,
    ):
        assert isinstance(axis, Index), axis

        self._filter_empty_groups = self.compressed = len(groupings) != 1
        self.axis = axis
        self._groupings: List[grouper.Grouping] = list(groupings)
        self.sort = sort
        self.group_keys = group_keys
        self.mutated = mutated
        self.indexer = indexer