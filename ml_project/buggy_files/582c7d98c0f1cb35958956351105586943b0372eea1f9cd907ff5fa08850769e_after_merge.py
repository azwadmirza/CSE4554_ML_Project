    def _maybe_right_yaxis(self, ax):
        _types = (list, tuple, np.ndarray)
        sec_true = isinstance(self.secondary_y, bool) and self.secondary_y
        list_sec = isinstance(self.secondary_y, _types)
        has_sec = list_sec and len(self.secondary_y) > 0
        all_sec = list_sec and len(self.secondary_y) == self.nseries

        if (sec_true or has_sec) and not hasattr(ax, 'right_ax'):
            orig_ax, new_ax = ax, ax.twinx()
            orig_ax.right_ax, new_ax.left_ax = new_ax, orig_ax

            if len(orig_ax.get_lines()) == 0: # no data on left y
                orig_ax.get_yaxis().set_visible(False)

            if len(new_ax.get_lines()) == 0:
                new_ax.get_yaxis().set_visible(False)

            if sec_true or all_sec:
                ax = new_ax
        else:
            ax.get_yaxis().set_visible(True)

        return ax