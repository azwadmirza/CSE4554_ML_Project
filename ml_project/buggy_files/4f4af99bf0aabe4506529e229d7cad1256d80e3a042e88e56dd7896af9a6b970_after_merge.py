    def serialize_using_object_code(self):
        """
        Serialize this library using its object code as the cached
        representation.  We also include its bitcode for further inlining
        with other libraries.
        """
        self._ensure_finalized()
        data = (self._get_compiled_object(),
                self._get_module_for_linking().as_bitcode())
        return (self._name, 'object', data)