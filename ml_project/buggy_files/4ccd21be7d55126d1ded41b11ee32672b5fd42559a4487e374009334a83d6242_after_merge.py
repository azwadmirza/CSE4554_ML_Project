            def inner(df, func, *args, **kwargs):
                """
                Parameters
                ----------
                df  : (DataFrame|Series)[GroupBy]
                    Data (may be grouped).
                func  : function
                    To be applied on the (grouped) data.
                *args, *kwargs  : optional
                    Transmitted to `df.apply()`.
                """
                # Precompute total iterations
                total = getattr(df, 'ngroups', None)
                if total is None:  # not grouped
                    total = len(df) if isinstance(df, Series) \
                        else df.size // len(df)
                else:
                    total += 1  # pandas calls update once too many

                # Init bar
                if deprecated_t[0] is not None:
                    t = deprecated_t[0]
                    deprecated_t[0] = None
                else:
                    t = tclass(*targs, total=total, **tkwargs)

                # Define bar updating wrapper
                def wrapper(*args, **kwargs):
                    t.update()
                    return func(*args, **kwargs)

                # Apply the provided function (in *args and **kwargs)
                # on the df using our wrapper (which provides bar updating)
                result = getattr(df, df_function)(wrapper, *args, **kwargs)

                # Close bar and return pandas calculation result
                t.close()
                return result