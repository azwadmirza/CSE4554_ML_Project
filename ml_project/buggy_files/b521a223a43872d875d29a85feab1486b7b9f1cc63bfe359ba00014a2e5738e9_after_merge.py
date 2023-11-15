    def get_functions(self):
        import capa.features.extractors.ida.helpers as ida_helpers
        for f in ida_helpers.get_functions(ignore_thunks=True, ignore_libs=True):
            yield add_va_int_cast(f)