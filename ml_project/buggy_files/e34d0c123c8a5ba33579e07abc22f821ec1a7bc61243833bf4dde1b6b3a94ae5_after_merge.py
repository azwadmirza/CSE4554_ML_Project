    def _get_names(self, arr):
        if isinstance(arr, DataFrame):
            if isinstance(arr.columns, MultiIndex):
                # Flatten MultiIndexes into "simple" column names
                return [".".join((level for level in c if level)) for c in arr.columns]
            else:
                return list(arr.columns)
        elif isinstance(arr, Series):
            if arr.name:
                return [arr.name]
            else:
                return
        else:
            try:
                return arr.dtype.names
            except AttributeError:
                pass

        return None