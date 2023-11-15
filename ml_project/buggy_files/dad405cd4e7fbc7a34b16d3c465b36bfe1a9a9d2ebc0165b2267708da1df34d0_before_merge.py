    def check_data(self):
        def error(err):
            err()
            self.data = None

        # `super().check_data()` clears all messages so we have to remember if
        # it was shown
        # pylint: disable=assignment-from-no-return
        should_show_modified_message = self.Information.modified.is_shown()
        super().check_data()

        if self.data is None:
            return

        self.Information.modified(shown=should_show_modified_message)

        if len(self.data) < 2:
            error(self.Error.not_enough_rows)

        elif not self.data.domain.attributes:
            error(self.Error.no_attributes)

        elif not self.data.is_sparse():
            if np.all(~np.isfinite(self.data.X)):
                error(self.Error.no_valid_data)
            else:
                with warnings.catch_warnings():
                    warnings.filterwarnings(
                        "ignore", "Degrees of freedom .*", RuntimeWarning)
                    if np.nan_to_num(np.nanstd(self.data.X, axis=0)).sum() \
                            == 0:
                        error(self.Error.constant_data)