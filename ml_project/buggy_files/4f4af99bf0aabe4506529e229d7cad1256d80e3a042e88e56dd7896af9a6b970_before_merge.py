    def serialize_using_object_code(self):
        """
        Serialize this library using its object code as the cached
        representation.
        """
        self._ensure_finalized()
        ll_module = self._final_module
        return (self._name, 'object', self._get_compiled_object())