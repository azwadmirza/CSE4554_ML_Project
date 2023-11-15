    def _consume_inline_attribute(self):
        # type: () -> Tuple[unicode, List[unicode]]
        line = next(self._line_iter)
        _type, colon, _desc = self._partition_field_on_colon(line)
        if not colon:
            _type, _desc = _desc, _type
        _descs = [_desc] + self._dedent(self._consume_to_end())
        _descs = self.__class__(_descs, self._config).lines()
        return _type, _descs