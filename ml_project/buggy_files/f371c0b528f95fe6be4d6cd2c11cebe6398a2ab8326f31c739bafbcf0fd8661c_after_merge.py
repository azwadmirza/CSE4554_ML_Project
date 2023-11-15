    def return_status_propagate(self, builder, status):
        trystatus = self.check_try_status(builder)
        excptr = self._get_excinfo_argument(builder.function)
        builder.store(status.excinfoptr, excptr)
        with builder.if_then(builder.not_(trystatus.in_try)):
            self._return_errcode_raw(builder, status.code)