    def __init__(self, kdf: DataFrame, scol: Optional[spark.Column] = None) -> None:
        assert len(kdf._internal._index_map) == 1
        if scol is None:
            IndexOpsMixin.__init__(
                self, kdf._internal.copy(scol=kdf._internal.index_scols[0]), kdf)
        else:
            IndexOpsMixin.__init__(self, kdf._internal.copy(scol=scol), kdf)