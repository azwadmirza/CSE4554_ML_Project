    def register(self, impl):
        sigs = impl.function_signatures
        impl.function_signatures = []
        self.functions.append((impl, sigs))
        return impl