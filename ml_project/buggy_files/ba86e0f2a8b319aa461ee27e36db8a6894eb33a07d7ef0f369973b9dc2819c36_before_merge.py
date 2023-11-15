    def _get_xticks(self):
        index = self.data.index
        is_datetype = index.inferred_type in ('datetime', 'date')

        if self.use_index:
            if index.is_numeric() or is_datetype:
                """
                Matplotlib supports numeric values or datetime objects as
                xaxis values. Taking LBYL approach here, by the time
                matplotlib raises exception when using non numeric/datetime
                values for xaxis, several actions are already taken by plt.
                """
                x = index.values
            else:
                self._need_to_set_index = True
                x = range(len(index))
        else:
            x = range(len(index))

        return x