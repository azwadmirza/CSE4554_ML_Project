    def _get_value(self, index, col, takeable=False):

        if takeable:
            series = self._iget_item_cache(col)
            return com.maybe_box_datetimelike(series._values[index])

        series = self._get_item_cache(col)
        engine = self.index._engine

        try:
            return engine.get_value(series._values, index)
        except KeyError:
            # GH 20629
            if self.index.nlevels > 1:
                # partial indexing forbidden
                raise
        except (TypeError, ValueError):
            pass

        # we cannot handle direct indexing
        # use positional
        col = self.columns.get_loc(col)
        index = self.index.get_loc(index)
        return self._get_value(index, col, takeable=True)