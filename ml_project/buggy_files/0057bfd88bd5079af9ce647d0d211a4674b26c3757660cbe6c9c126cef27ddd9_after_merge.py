    def _astype(self, dtype, copy=False, errors='raise', values=None,
                klass=None, mgr=None, **kwargs):
        """Coerce to the new type

        Parameters
        ----------
        dtype : str, dtype convertible
        copy : boolean, default False
            copy if indicated
        errors : str, {'raise', 'ignore'}, default 'ignore'
            - ``raise`` : allow exceptions to be raised
            - ``ignore`` : suppress exceptions. On error return original object

        Returns
        -------
        Block
        """
        errors_legal_values = ('raise', 'ignore')

        if errors not in errors_legal_values:
            invalid_arg = ("Expected value of kwarg 'errors' to be one of {}. "
                           "Supplied value is '{}'".format(
                               list(errors_legal_values), errors))
            raise ValueError(invalid_arg)

        if (inspect.isclass(dtype) and
                issubclass(dtype, (PandasExtensionDtype, ExtensionDtype))):
            msg = ("Expected an instance of {}, but got the class instead. "
                   "Try instantiating 'dtype'.".format(dtype.__name__))
            raise TypeError(msg)

        # may need to convert to categorical
        if self.is_categorical_astype(dtype):

            # deprecated 17636
            if ('categories' in kwargs or 'ordered' in kwargs):
                if isinstance(dtype, CategoricalDtype):
                    raise TypeError(
                        "Cannot specify a CategoricalDtype and also "
                        "`categories` or `ordered`. Use "
                        "`dtype=CategoricalDtype(categories, ordered)`"
                        " instead.")
                warnings.warn("specifying 'categories' or 'ordered' in "
                              ".astype() is deprecated; pass a "
                              "CategoricalDtype instead",
                              FutureWarning, stacklevel=7)

            categories = kwargs.get('categories', None)
            ordered = kwargs.get('ordered', None)
            if com._any_not_none(categories, ordered):
                dtype = CategoricalDtype(categories, ordered)

            if is_categorical_dtype(self.values):
                # GH 10696/18593: update an existing categorical efficiently
                return self.make_block(self.values.astype(dtype, copy=copy))

            return self.make_block(Categorical(self.values, dtype=dtype))

        # convert dtypes if needed
        dtype = pandas_dtype(dtype)

        # astype processing
        if is_dtype_equal(self.dtype, dtype):
            if copy:
                return self.copy()
            return self

        if klass is None:
            if dtype == np.object_:
                klass = ObjectBlock
        try:
            # force the copy here
            if values is None:

                if self.is_extension:
                    values = self.values.astype(dtype)
                else:
                    if issubclass(dtype.type,
                                  (compat.text_type, compat.string_types)):

                        # use native type formatting for datetime/tz/timedelta
                        if self.is_datelike:
                            values = self.to_native_types()

                        # astype formatting
                        else:
                            values = self.get_values()

                    else:
                        values = self.get_values(dtype=dtype)

                    # _astype_nansafe works fine with 1-d only
                    values = astype_nansafe(values.ravel(), dtype, copy=True)

                # TODO(extension)
                # should we make this attribute?
                try:
                    values = values.reshape(self.shape)
                except AttributeError:
                    pass

            newb = make_block(values, placement=self.mgr_locs,
                              klass=klass, ndim=self.ndim)
        except Exception:  # noqa: E722
            if errors == 'raise':
                raise
            newb = self.copy() if copy else self

        if newb.is_numeric and self.is_numeric:
            if newb.shape != self.shape:
                raise TypeError(
                    "cannot set astype for copy = [{copy}] for dtype "
                    "({dtype} [{shape}]) to different shape "
                    "({newb_dtype} [{newb_shape}])".format(
                        copy=copy, dtype=self.dtype.name,
                        shape=self.shape, newb_dtype=newb.dtype.name,
                        newb_shape=newb.shape))
        return newb