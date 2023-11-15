    def _use_dynamic_x(self):
        freq = self._index_freq()

        ax = self._get_ax(0)
        ax_freq = getattr(ax, 'freq', None)
        if freq is None: # convert irregular if axes has freq info
            freq = ax_freq
        else: # do not use tsplot if irregular was plotted first
            if (ax_freq is None) and (len(ax.get_lines()) > 0):
                return False

        return (freq is not None) and self._is_dynamic_freq(freq)