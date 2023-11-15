    def call_and_store(self, getter_func, data, field_name, field_obj, index=None):
        """Call ``getter_func`` with ``data`` as its argument, and store any `ValidationErrors`.

        :param callable getter_func: Function for getting the serialized/deserialized
            value from ``data``.
        :param data: The data passed to ``getter_func``.
        :param str field_name: Field name.
        :param FieldABC field_obj: Field object that performs the
            serialization/deserialization behavior.
        :param int index: Index of the item being validated, if validating a collection,
            otherwise `None`.
        """
        try:
            value = getter_func(data)
        except ValidationError as err:  # Store validation errors
            self.error_fields.append(field_obj)
            self.error_field_names.append(field_name)
            errors = self.get_errors(index=index)
            # Warning: Mutation!
            if isinstance(err.messages, dict):
                errors[field_name] = err.messages
            elif isinstance(errors.get(field_name), dict):
                errors[field_name].setdefault(FIELD, []).extend(err.messages)
            else:
                errors.setdefault(field_name, []).extend(err.messages)
            # When a Nested field fails validation, the marshalled data is stored
            # on the ValidationError's data attribute
            value = err.data or missing
        return value