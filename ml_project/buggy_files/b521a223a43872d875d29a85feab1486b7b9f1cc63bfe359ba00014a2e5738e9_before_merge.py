    def get_functions(self):
        for f in capa.features.extractors.ida.helpers.get_functions(ignore_thunks=True, ignore_libs=True):
            yield add_va_int_cast(f)