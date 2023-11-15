    def _deserialize(self, value, attr, data):
        if not value:  # Falsy values, e.g. '', None, [] are not valid
            raise self.fail('invalid', obj_type=self.OBJ_TYPE)
        data_format = self.format or self.DEFAULT_FORMAT
        func = self.DESERIALIZATION_FUNCS.get(data_format)
        if func:
            try:
                return func(value)
            except (TypeError, AttributeError, ValueError):
                raise self.fail('invalid', obj_type=self.OBJ_TYPE)
        elif data_format:
            try:
                return dt.datetime.strptime(value, data_format)
            except (TypeError, AttributeError, ValueError):
                raise self.fail('invalid', obj_type=self.OBJ_TYPE)
        elif utils.dateutil_available:
            try:
                parsed = utils.from_datestring(value)
                return self._create_data_object_from_parsed_value(parsed)
            except (TypeError, ValueError):
                raise self.fail('invalid', obj_type=self.OBJ_TYPE)
        else:
            warnings.warn(
                'It is recommended that you install python-dateutil '
                'for improved datetime deserialization.',
            )
            raise self.fail('invalid', obj_type=self.OBJ_TYPE)