    def predict(self, exog=None, transform=True, *args, **kwargs):
        """
        Call self.model.predict with self.params as the first argument.

        Parameters
        ----------
        exog : array-like, optional
            The values for which you want to predict.
        transform : bool, optional
            If the model was fit via a formula, do you want to pass
            exog through the formula. Default is True. E.g., if you fit
            a model y ~ log(x1) + log(x2), and transform is True, then
            you can pass a data structure that contains x1 and x2 in
            their original form. Otherwise, you'd need to log the data
            first.
        args, kwargs :
            Some models can take additional arguments or keywords, see the
            predict method of the model for the details.

        Returns
        -------
        prediction : ndarray, pandas.Series or pandas.DataFrame
            See self.model.predict

        """
        import pandas as pd

        exog_index = exog.index if _is_using_pandas(exog, None) else None

        if transform and hasattr(self.model, 'formula') and exog is not None:
            from patsy import dmatrix
            exog = pd.DataFrame(exog)  # user may pass series, if one predictor
            if exog_index is None:  # user passed in a dictionary
                exog_index = exog.index
            exog = dmatrix(self.model.data.design_info.builder,
                           exog, return_type="dataframe")
            if len(exog) < len(exog_index):
                # missing values, rows have been dropped
                if exog_index is not None:
                    exog = exog.reindex(exog_index)
                else:
                    import warnings
                    warnings.warn("nan rows have been dropped", ValueWarning)

        if exog is not None:
            exog = np.asarray(exog)
            if exog.ndim == 1 and (self.model.exog.ndim == 1 or
                                   self.model.exog.shape[1] == 1):
                exog = exog[:, None]
            exog = np.atleast_2d(exog)  # needed in count model shape[1]

        predict_results = self.model.predict(self.params, exog, *args, **kwargs)

        if exog_index is not None and not hasattr(predict_results, 'predicted_values'):

            if predict_results.ndim == 1:
                return pd.Series(predict_results, index=exog_index)
            else:
                return pd.DataFrame(predict_results, index=exog_index)

        else:

            return predict_results