    def multifit(self, mask=None, fetch_only_fixed=False,
                 autosave=False, autosave_every=10, show_progressbar=None,
                 **kwargs):
        """Fit the data to the model at all the positions of the
        navigation dimensions.

        Parameters
        ----------

        mask : {None, numpy.array}
            To mask (do not fit) at certain position pass a numpy.array
            of type bool where True indicates that the data will not be
            fitted at the given position.
        fetch_only_fixed : bool
            If True, only the fixed parameters values will be updated
            when changing the positon.
        autosave : bool
            If True, the result of the fit will be saved automatically
            with a frequency defined by autosave_every.
        autosave_every : int
            Save the result of fitting every given number of spectra.

        show_progressbar : None or bool
            If True, display a progress bar. If None the default is set in
            `preferences`.

        **kwargs : key word arguments
            Any extra key word argument will be passed to
            the fit method. See the fit method documentation for
            a list of valid arguments.

        See Also
        --------
        fit

        """
        if show_progressbar is None:
            show_progressbar = preferences.General.show_progressbar

        if autosave is not False:
            fd, autosave_fn = tempfile.mkstemp(
                prefix='hyperspy_autosave-',
                dir='.', suffix='.npz')
            os.close(fd)
            autosave_fn = autosave_fn[:-4]
            messages.information(
                "Autosaving each %s pixels to %s.npz" % (autosave_every,
                                                         autosave_fn))
            messages.information(
                "When multifit finishes its job the file will be deleted")
        if mask is not None and (
            mask.shape != tuple(
                self.axes_manager._navigation_shape_in_array)):
            messages.warning_exit(
                "The mask must be a numpy array of boolen type with "
                " shape: %s" +
                str(self.axes_manager._navigation_shape_in_array))
        masked_elements = 0 if mask is None else mask.sum()
        maxval = self.axes_manager.navigation_size - masked_elements
        if maxval > 0:
            pbar = progressbar.progressbar(maxval=maxval,
                                           disabled=not show_progressbar)
        if 'bounded' in kwargs and kwargs['bounded'] is True:
            if kwargs['fitter'] == 'mpfit':
                self.set_mpfit_parameters_info()
                kwargs['bounded'] = None
            elif kwargs['fitter'] in ("tnc", "l_bfgs_b"):
                self.set_boundaries()
                kwargs['bounded'] = None
            else:
                messages.information(
                    "The chosen fitter does not suppport bounding."
                    "If you require bounding please select one of the "
                    "following fitters instead: mpfit, tnc, l_bfgs_b")
                kwargs['bounded'] = False
        i = 0
        self.axes_manager.disconnect(self.fetch_stored_values)
        for index in self.axes_manager:
            if mask is None or not mask[index[::-1]]:
                self.fetch_stored_values(only_fixed=fetch_only_fixed)
                self.fit(**kwargs)
                i += 1
                if maxval > 0:
                    pbar.update(i)
            if autosave is True and i % autosave_every == 0:
                self.save_parameters2file(autosave_fn)
        if maxval > 0:
            pbar.finish()
        self.axes_manager.connect(self.fetch_stored_values)
        if autosave is True:
            messages.information(
                'Deleting the temporary file %s pixels' % (
                    autosave_fn + 'npz'))
            os.remove(autosave_fn + '.npz')