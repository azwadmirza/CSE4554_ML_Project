    def __init__(self, data=None, index=None, dtype=None, name=None, copy=False, fastpath=False,
                 anchor=None):
        if isinstance(data, _InternalFrame):
            assert dtype is None
            assert name is None
            assert not copy
            assert not fastpath
            IndexOpsMixin.__init__(self, data, anchor)
        else:
            if isinstance(data, pd.Series):
                assert index is None
                assert dtype is None
                assert name is None
                assert not copy
                assert anchor is None
                assert not fastpath
                s = data
            else:
                s = pd.Series(
                    data=data, index=index, dtype=dtype, name=name, copy=copy, fastpath=fastpath)
            kdf = DataFrame(s)
            IndexOpsMixin.__init__(self, kdf._internal.copy(
                scol=kdf._internal._sdf[kdf._internal.data_columns[0]]), kdf)