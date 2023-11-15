    def _remove_background_cli(
            self, signal_range, background_estimator, fast=True,
            zero_fill=False, show_progressbar=None):
        signal_range = signal_range_from_roi(signal_range)
        from hyperspy.models.model1d import Model1D
        model = Model1D(self)
        model.append(background_estimator)
        background_estimator.estimate_parameters(
            self,
            signal_range[0],
            signal_range[1],
            only_current=False)
        if fast and not self._lazy:
            try:
                axis = self.axes_manager.signal_axes[0].axis
                result = self - background_estimator.function_nd(axis)
            except MemoryError:
                result = self - model.as_signal(
                    show_progressbar=show_progressbar)
        else:
            model.set_signal_range(signal_range[0], signal_range[1])
            model.multifit(show_progressbar=show_progressbar)
            model.reset_signal_range()
            result = self - model.as_signal(show_progressbar=show_progressbar)

        if zero_fill:
            if self._lazy:
                low_idx = result.axes_manager[-1].value2index(signal_range[0])
                z = da.zeros(low_idx, chunks=(low_idx,))
                cropped_da = result.data[low_idx:]
                result.data = da.concatenate([z, cropped_da])
            else:
                result.isig[:signal_range[0]] = 0
        return result