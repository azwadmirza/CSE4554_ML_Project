    def _is_missing(self) -> bool:
        try:
            self._dereference_node(
                throw_on_resolution_failure=False, throw_on_missing=True
            )
            return False
        except MissingMandatoryValue:
            ret = True

        assert isinstance(ret, bool)
        return ret