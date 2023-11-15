    def __init__(self, endog, exog=None, missing='none', hasconst=None,
                 **kwargs):
        if 'design_info' in kwargs:
            self.design_info = kwargs.pop('design_info')
        if missing != 'none':
            arrays, nan_idx = self.handle_missing(endog, exog, missing,
                                                  **kwargs)
            self.missing_row_idx = nan_idx
            self.__dict__.update(arrays)  # attach all the data arrays
            self.orig_endog = self.endog
            self.orig_exog = self.exog
            self.endog, self.exog = self._convert_endog_exog(self.endog,
                                                             self.exog)
        else:
            self.__dict__.update(kwargs)  # attach the extra arrays anyway
            self.orig_endog = endog
            self.orig_exog = exog
            self.endog, self.exog = self._convert_endog_exog(endog, exog)

        # this has side-effects, attaches k_constant and const_idx
        self._handle_constant(hasconst)
        self._check_integrity()
        self._cache = resettable_cache()