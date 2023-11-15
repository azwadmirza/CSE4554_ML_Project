    def _get_loadings(self, loadings):
        from hyperspy.api import signals
        data = loadings.T.reshape(
            (-1,) + self.axes_manager.navigation_shape[::-1])
        signal = signals.BaseSignal(
            data,
            axes=(
                [{"size": data.shape[0], "navigate": True}] +
                self.axes_manager._get_navigation_axes_dicts()))
        for axis in signal.axes_manager._axes[1:]:
            axis.navigate = False
        return signal