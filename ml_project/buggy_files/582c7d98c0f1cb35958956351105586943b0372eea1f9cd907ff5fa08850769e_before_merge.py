    def _maybe_right_yaxis(self, ax):
        ypos = ax.get_yaxis().get_ticks_position().strip().lower()

        if self.secondary_y and ypos != 'right':
            orig_ax = ax
            ax = ax.twinx()
            if len(orig_ax.get_lines()) == 0: # no data on left y
                orig_ax.get_yaxis().set_visible(False)
        else:
            ax.get_yaxis().set_visible(True)

        return ax