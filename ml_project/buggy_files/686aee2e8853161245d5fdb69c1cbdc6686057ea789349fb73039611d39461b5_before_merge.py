    def _unserialize(cls, codegen, state):
        name, kind, data = state
        self = codegen.create_library(name)
        assert isinstance(self, cls)
        if kind == 'bitcode':
            # No need to re-run optimizations, just make the module ready
            self._final_module = ll.parse_bitcode(data)
            self._finalize_final_module()
            return self
        elif kind == 'object':
            self.enable_object_caching()
            self._set_compiled_object(data)
            self._finalize_final_module()
            return self
        else:
            raise ValueError("unsupported serialization kind %r" % (kind,))