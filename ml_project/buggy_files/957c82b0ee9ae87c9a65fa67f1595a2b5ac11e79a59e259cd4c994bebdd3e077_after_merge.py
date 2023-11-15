    def _get_axis_number(self, axis):
        return (
            getattr(pandas, type(self).__name__)()._get_axis_number(axis)
            if axis is not None
            else 0
        )