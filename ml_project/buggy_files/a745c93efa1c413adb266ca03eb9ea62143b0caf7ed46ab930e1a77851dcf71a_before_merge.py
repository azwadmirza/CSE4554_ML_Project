    def __init__(self, endog, exog, offset=None, exposure=None, missing='none',
                 check_rank=True, **kwargs):
        super().__init__(endog, exog, check_rank, missing=missing,
                         offset=offset, exposure=exposure, **kwargs)
        if exposure is not None:
            self.exposure = np.log(self.exposure)
        self._check_inputs(self.offset, self.exposure, self.endog)
        if offset is None:
            delattr(self, 'offset')
        if exposure is None:
            delattr(self, 'exposure')

        # promote dtype to float64 if needed
        dt = np.promote_types(self.endog.dtype, np.float64)
        self.endog = np.asarray(self.endog, dt)
        dt = np.promote_types(self.exog.dtype, np.float64)
        self.exog = np.asarray(self.exog, dt)