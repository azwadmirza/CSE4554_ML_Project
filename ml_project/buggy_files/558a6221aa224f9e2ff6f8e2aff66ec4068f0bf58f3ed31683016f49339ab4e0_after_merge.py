    def __getattribute__(self, item):
        default_behaviors = [
            "__init__",
            "series",
            "parent_df",
            "_loc",
            "__arithmetic_op__",
            "__comparisons__",
            "__class__",
        ]
        if item not in default_behaviors:
            method = self.series.__getattribute__(item)
            # Certain operations like `at`, `loc`, `iloc`, etc. are callable because in
            # pandas they are equivalent to classes. They are verified here because they
            # cannot be overridden with the functions below. This generally solves the
            # problem where the instance property is callable, but the class property is
            # not.
            # The isclass check is to ensure that we return the correct type. Some of
            # the objects that are called result in classes being returned, and we don't
            # want to override with our own function.
            is_callable = (
                callable(method)
                and callable(getattr(type(self.series), item))
                and not inspect.isclass(getattr(type(self.series), item))
            )
            try:
                has_inplace_param = is_callable and "inplace" in str(
                    inspect.signature(method)
                )
            # This will occur on Python2
            except AttributeError:
                has_inplace_param = is_callable and "inplace" in str(
                    inspect.getargspec(method)
                )

            if is_callable and has_inplace_param and self.parent_df is not None:

                def inplace_handler(*args, **kwargs):
                    """Replaces the default behavior of methods with inplace kwarg.

                    Note: This method will modify the DataFrame this Series is attached
                        to when `inplace` is True. Instead of rewriting or overriding
                        every method that uses `inplace`, we use this handler.

                        This handler will first check that the keyword argument passed
                        for `inplace` is True, if not then it will just return the
                        result of the operation requested.

                        If `inplace` is True, do the operation, keeping track of the
                        previous length. This is because operations like `dropna` still
                        propagate back to the DataFrame that holds the Series.

                        If the length did not change, we propagate the inplace changes
                        of the operation back to the original DataFrame with
                        `__setitem__`.

                        If the length changed, we just need to do a `reindex` on the
                        parent DataFrame. This will propagate the inplace operation
                        (e.g. `dropna`) back to the parent DataFrame.

                        See notes in SeriesView class about when it is okay to return a
                        pandas Series vs a SeriesView.

                    Returns:
                        If `inplace` is True: None, else: A new Series.
                    """
                    if kwargs.get("inplace", False):
                        prev_len = len(self.series)
                        self.series.__getattribute__(item)(*args, **kwargs)
                        if prev_len == len(self.series):
                            self.parent_df.loc[self._loc] = self.series
                        else:
                            self.parent_df.reindex(index=self.series.index, copy=False)
                        return None
                    else:
                        return self.series.__getattribute__(item)(*args, **kwargs)

                # We replace the method with `inplace_handler` for inplace operations
                method = inplace_handler
            elif is_callable:

                def other_handler(*args, **kwargs):
                    """Replaces the method's args and kwargs with the Series object.

                    Note: This method is needed because sometimes operations like
                        `df['col0'].equals(df['col1'])` do not return the correct value.
                        This mostly has occurred in Python2, but overriding of the
                        method will make the behavior more deterministic for all calls.

                    Returns the result of `__getattribute__` from the Series this wraps.
                    """
                    args = tuple(
                        arg if not isinstance(arg, SeriesView) else arg.series
                        for arg in args
                    )
                    kwargs = {
                        kw: arg if not isinstance(arg, SeriesView) else arg.series
                        for kw, arg in kwargs.items()
                    }
                    return self.series.__getattribute__(item)(*args, **kwargs)

                method = other_handler
            return method
        # We need to do this hack for equality checking.
        elif item == "__class__":
            return self.series.__class__
        else:
            return object.__getattribute__(self, item)