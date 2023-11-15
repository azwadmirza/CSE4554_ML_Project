    def get_prediction(self, start=None, end=None, dynamic=False, index=None,
                       exog=None, **kwargs):
        r"""
        In-sample prediction and out-of-sample forecasting

        Parameters
        ----------
        start : int, str, or datetime, optional
            Zero-indexed observation number at which to start forecasting, ie.,
            the first forecast is start. Can also be a date string to
            parse or a datetime type. Default is the the zeroth observation.
        end : int, str, or datetime, optional
            Zero-indexed observation number at which to end forecasting, ie.,
            the first forecast is start. Can also be a date string to
            parse or a datetime type. However, if the dates index does not
            have a fixed frequency, end must be an integer index if you
            want out of sample prediction. Default is the last observation in
            the sample.
        exog : array_like, optional
            If the model includes exogenous regressors, you must provide
            exactly enough out-of-sample values for the exogenous variables if
            end is beyond the last observation in the sample.
        dynamic : bool, int, str, or datetime, optional
            Integer offset relative to `start` at which to begin dynamic
            prediction. Can also be an absolute date string to parse or a
            datetime type (these are not interpreted as offsets).
            Prior to this observation, true endogenous values will be used for
            prediction; starting with this observation and continuing through
            the end of prediction, forecasted endogenous values will be used
            instead.
        full_results : bool, optional
            If True, returns a FilterResults instance; if False returns a
            tuple with forecasts, the forecast errors, and the forecast error
            covariance matrices. Default is False.
        **kwargs
            Additional arguments may required for forecasting beyond the end
            of the sample. See `FilterResults.predict` for more details.

        Returns
        -------
        forecast : array
            Array of out of sample forecasts.
        """
        if start is None:
            if (self.model.simple_differencing and
                    not self.model._index_generated and
                    not self.model._index_dates):
                start = 0
            else:
                start = self.model._index[0]

        # Handle start, end, dynamic
        _start, _end, _out_of_sample, prediction_index = (
            self.model._get_prediction_index(start, end, index, silent=True))

        # Handle exogenous parameters
        if _out_of_sample and (self.model.k_exog + self.model.k_trend > 0):
            # Create a new faux SARIMAX model for the extended dataset
            nobs = self.model.data.orig_endog.shape[0] + _out_of_sample
            endog = np.zeros((nobs, self.model.k_endog))

            if self.model.k_exog > 0:
                if exog is None:
                    raise ValueError('Out-of-sample forecasting in a model'
                                     ' with a regression component requires'
                                     ' additional exogenous values via the'
                                     ' `exog` argument.')
                exog = np.array(exog)
                required_exog_shape = (_out_of_sample, self.model.k_exog)
                try:
                    exog = exog.reshape(required_exog_shape)
                except ValueError:
                    raise ValueError('Provided exogenous values are not of the'
                                     ' appropriate shape. Required %s, got %s.'
                                     % (str(required_exog_shape),
                                        str(exog.shape)))
                exog = np.c_[self.model.data.orig_exog.T, exog.T].T

            model_kwargs = self._init_kwds.copy()
            model_kwargs['exog'] = exog
            model = SARIMAX(endog, **model_kwargs)
            model.update(self.params, transformed=True, includes_fixed=True)

            # Set the kwargs with the update time-varying state space
            # representation matrices
            for name in self.filter_results.shapes.keys():
                if name == 'obs':
                    continue
                mat = getattr(model.ssm, name)
                if mat.shape[-1] > 1:
                    kwargs[name] = mat[..., -_out_of_sample:]
        elif self.model.k_exog == 0 and exog is not None:
            warn('Exogenous array provided to predict, but additional data not'
                 ' required. `exog` argument ignored.', ValueWarning)

        return super(SARIMAXResults, self).get_prediction(
            start=start, end=end, dynamic=dynamic, index=index, exog=exog,
            **kwargs)