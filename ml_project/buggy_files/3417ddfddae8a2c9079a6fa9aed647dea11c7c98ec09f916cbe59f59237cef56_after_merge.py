            def inner(df, func, *args, **kwargs):
                """
                Parameters
                ----------
                df  : (DataFrame|Series)[GroupBy]
                    Data (may be grouped).
                func  : function
                    To be applied on the (grouped) data.
                **kwargs  : optional
                    Transmitted to `df.apply()`.
                """

                # Precompute total iterations
                total = tkwargs.pop("total", getattr(df, 'ngroups', None))
                if total is None:  # not grouped
                    if df_function == 'applymap':
                        total = df.size
                    elif isinstance(df, Series):
                        total = len(df)
                    elif _Rolling_and_Expanding is None or \
                            not isinstance(df, _Rolling_and_Expanding):
                        # DataFrame or Panel
                        axis = kwargs.get('axis', 0)
                        if axis == 'index':
                            axis = 0
                        elif axis == 'columns':
                            axis = 1
                        # when axis=0, total is shape[axis1]
                        total = df.size // df.shape[axis]

                # Init bar
                if deprecated_t[0] is not None:
                    t = deprecated_t[0]
                    deprecated_t[0] = None
                else:
                    t = tclass(*targs, total=total, **tkwargs)

                if len(args) > 0:
                    # *args intentionally not supported (see #244, #299)
                    TqdmDeprecationWarning(
                        "Except func, normal arguments are intentionally" +
                        " not supported by" +
                        " `(DataFrame|Series|GroupBy).progress_apply`." +
                        " Use keyword arguments instead.",
                        fp_write=getattr(t.fp, 'write', sys.stderr.write))

                try:
                    func = df._is_builtin_func(func)
                except TypeError:
                    pass

                # Define bar updating wrapper
                def wrapper(*args, **kwargs):
                    # update tbar correctly
                    # it seems `pandas apply` calls `func` twice
                    # on the first column/row to decide whether it can
                    # take a fast or slow code path; so stop when t.total==t.n
                    t.update(n=1 if not t.total or t.n < t.total else 0)
                    return func(*args, **kwargs)

                # Apply the provided function (in **kwargs)
                # on the df using our wrapper (which provides bar updating)
                result = getattr(df, df_function)(wrapper, **kwargs)

                # Close bar and return pandas calculation result
                t.close()
                return result