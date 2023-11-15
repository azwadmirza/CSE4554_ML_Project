    def _combine_frame(self, other, func, fill_value=None, level=None):
        this, other = self.align(other, join='outer', level=level,
                                 copy=False)
        new_index, new_columns = this.index, this.columns

        if level is not None:
            raise NotImplementedError

        if not self and not other:
            return SparseDataFrame(index=new_index)

        new_data = {}
        if fill_value is not None:
            # TODO: be a bit more intelligent here
            for col in new_columns:
                if col in this and col in other:
                    dleft = this[col].to_dense()
                    dright = other[col].to_dense()
                    result = dleft._binop(dright, func, fill_value=fill_value)
                    result = result.to_sparse(fill_value=this[col].fill_value)
                    new_data[col] = result
        else:
            for col in new_columns:
                if col in this and col in other:
                    new_data[col] = func(this[col], other[col])

        return self._constructor(data=new_data, index=new_index,
                                 columns=new_columns)