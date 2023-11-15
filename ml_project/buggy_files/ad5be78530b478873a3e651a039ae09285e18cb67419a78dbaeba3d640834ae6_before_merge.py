    def summary(self, alpha=.05, start=None):
        # Create the model name

        # See if we have an ARIMA component
        order = ''
        if self.model.k_ar + self.model.k_diff + self.model.k_ma > 0:
            if self.model.k_ar == self.model.k_ar_params:
                order_ar = self.model.k_ar
            else:
                order_ar = tuple(self.polynomial_ar.nonzero()[0][1:])
            if self.model.k_ma == self.model.k_ma_params:
                order_ma = self.model.k_ma
            else:
                order_ma = tuple(self.polynomial_ma.nonzero()[0][1:])
            # If there is simple differencing, then that is reflected in the
            # dependent variable name
            k_diff = 0 if self.model.simple_differencing else self.model.k_diff
            order = '(%s, %d, %s)' % (order_ar, k_diff, order_ma)
        # See if we have an SARIMA component
        seasonal_order = ''
        has_seasonal = (
            self.model.k_seasonal_ar +
            self.model.k_seasonal_diff +
            self.model.k_seasonal_ma
        ) > 0
        if has_seasonal:
            if self.model.k_ar == self.model.k_ar_params:
                order_seasonal_ar = (
                    int(self.model.k_seasonal_ar / self.model.seasonal_periods)
                )
            else:
                order_seasonal_ar = (
                    tuple(self.polynomial_seasonal_ar.nonzero()[0][1:])
                )
            if self.model.k_ma == self.model.k_ma_params:
                order_seasonal_ma = (
                    int(self.model.k_seasonal_ma / self.model.seasonal_periods)
                )
            else:
                order_seasonal_ma = (
                    tuple(self.polynomial_seasonal_ma.nonzero()[0][1:])
                )
            # If there is simple differencing, then that is reflected in the
            # dependent variable name
            k_seasonal_diff = self.model.k_seasonal_diff
            if self.model.simple_differencing:
                k_seasonal_diff = 0
            seasonal_order = ('(%s, %d, %s, %d)' %
                              (str(order_seasonal_ar), k_seasonal_diff,
                               str(order_seasonal_ma),
                               self.model.seasonal_periods))
            if not order == '':
                order += 'x'
        model_name = (
            '%s%s%s' % (self.model.__class__.__name__, order, seasonal_order)
            )
        return super(SARIMAXResults, self).summary(
            alpha=alpha, start=start, model_name=model_name
        )