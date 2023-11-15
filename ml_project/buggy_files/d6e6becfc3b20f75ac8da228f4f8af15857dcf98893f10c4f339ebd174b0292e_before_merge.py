    def conf_int(self, method='endpoint', alpha=0.05, **kwds):
        # TODO: this performs metadata wrapping, and that should be handled
        #       by attach_* methods. However, they do not currently support
        #       this use case.
        conf_int = super(PredictionResults, self).conf_int(
            method, alpha, **kwds)

        # Create a dataframe
        if self.row_labels is not None:
            conf_int = pd.DataFrame(conf_int, index=self.row_labels)

            # Attach the endog names
            ynames = self.model.data.ynames
            if not type(ynames) == list:
                ynames = [ynames]
            names = (['lower %s' % name for name in ynames] +
                     ['upper %s' % name for name in ynames])
            conf_int.columns = names

        return conf_int