    def _groupby_and_aggregate(self, grouper, how, *args, **kwargs):
        """ revaluate the obj with a groupby aggregation """

        if grouper is None:
            self._set_binner()
            grouper = self.grouper

        obj = self._selected_obj

        try:
            grouped = groupby(obj, by=None, grouper=grouper, axis=self.axis)
        except TypeError:

            # panel grouper
            grouped = PanelGroupBy(obj, grouper=grouper, axis=self.axis)

        try:
            result = grouped.aggregate(how, *args, **kwargs)
        except Exception:

            # we have a non-reducing function
            # try to evaluate
            result = grouped.apply(how, *args, **kwargs)

        result = self._apply_loffset(result)

        return self._wrap_result(result)