    def _broadcast_item(self, row_lookup, col_lookup, item, to_shape):
        """
        Use numpy to broadcast or reshape item.

        TODO: Add more details for this docstring template.

        Parameters
        ----------
        What arguments does this function have.
        [
        PARAMETER_NAME: PARAMETERS TYPES
            Description.
        ]

        Returns
        -------
        What this returns (if anything)

        Notes
        -----
        Numpy is memory efficient, there shouldn't be performance issue.
        """
        # It is valid to pass a DataFrame or Series to __setitem__ that is larger than
        # the target the user is trying to overwrite. This
        if isinstance(item, (pandas.Series, pandas.DataFrame, Series, DataFrame)):
            # convert indices in lookups to names, as Pandas reindex expects them to be so
            index_values = self.qc.index[row_lookup]
            if not all(idx in item.index for idx in index_values):
                raise ValueError(
                    "Must have equal len keys and value when setting with "
                    "an iterable"
                )
            if hasattr(item, "columns"):
                column_values = self.qc.columns[col_lookup]
                if not all(col in item.columns for col in column_values):
                    # TODO: think if it is needed to handle cases when columns have duplicate names
                    raise ValueError(
                        "Must have equal len keys and value when setting "
                        "with an iterable"
                    )
                item = item.reindex(index=index_values, columns=column_values)
            else:
                item = item.reindex(index=index_values)
        try:
            item = np.array(item)
            if np.prod(to_shape) == np.prod(item.shape):
                return item.reshape(to_shape)
            else:
                return np.broadcast_to(item, to_shape)
        except ValueError:
            from_shape = np.array(item).shape
            raise ValueError(
                "could not broadcast input array from shape {from_shape} into shape "
                "{to_shape}".format(from_shape=from_shape, to_shape=to_shape)
            )