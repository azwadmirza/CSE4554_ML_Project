    def __init__(self, kdf: DataFrame, scol: Optional[spark.Column] = None):
        assert len(kdf._internal._index_map) > 1
        self._kdf = kdf
        if scol is None:
            IndexOpsMixin.__init__(self, kdf._internal.copy(scol=F.struct(self._columns)), kdf)
        else:
            IndexOpsMixin.__init__(self, kdf._internal.copy(scol=scol), kdf)