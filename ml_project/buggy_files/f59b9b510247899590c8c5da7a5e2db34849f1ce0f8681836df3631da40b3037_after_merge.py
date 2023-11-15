    def convert_objects(self, datetime=False, numeric=False,
                        timedelta=False, coerce=False, copy=True):
        """
        Attempt to infer better dtype for object columns

        Parameters
        ----------
        datetime : boolean, default False
            If True, convert to date where possible.
        numeric : boolean, default False
            If True, attempt to convert to numbers (including strings), with
            unconvertible values becoming NaN.
        timedelta : boolean, default False
            If True, convert to timedelta where possible.
        coerce : boolean, default False
            If True, force conversion with unconvertible values converted to
            nulls (NaN or NaT)
        copy : boolean, default True
            If True, return a copy even if no copy is necessary (e.g. no
            conversion was done). Note: This is meant for internal use, and
            should not be confused with inplace.

        Returns
        -------
        converted : same as input object
        """

        # Deprecation code to handle usage change
        issue_warning = False
        if datetime == 'coerce':
            datetime = coerce = True
            numeric = timedelta = False
            issue_warning = True
        elif numeric == 'coerce':
            numeric = coerce = True
            datetime = timedelta = False
            issue_warning = True
        elif timedelta == 'coerce':
            timedelta = coerce = True
            datetime = numeric = False
            issue_warning = True
        if issue_warning:
            warnings.warn("The use of 'coerce' as an input is deprecated. "
                          "Instead set coerce=True.",
                          FutureWarning)

        return self._constructor(
            self._data.convert(datetime=datetime,
                               numeric=numeric,
                               timedelta=timedelta,
                               coerce=coerce,
                               copy=copy)).__finalize__(self)