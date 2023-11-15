    def return_status_propagate(self, builder, status):
        excptr = self._get_excinfo_argument(builder.function)
        builder.store(status.excinfoptr, excptr)
        self._return_errcode_raw(builder, status.code)