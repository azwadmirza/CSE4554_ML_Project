    def update(self, attributes=None, actions=None, condition=None, conditional_operator=None, **expected_values):
        """
        Updates an item using the UpdateItem operation.

        :param attributes: A dictionary of attributes to update in the following format
                            {
                                attr_name: {'value': 10, 'action': 'ADD'},
                                next_attr: {'value': True, 'action': 'PUT'},
                            }
        """
        if attributes is not None and not isinstance(attributes, dict):
            raise TypeError("the value of `attributes` is expected to be a dictionary")
        if actions is not None and not isinstance(actions, list):
            raise TypeError("the value of `actions` is expected to be a list")

        self._conditional_operator_check(conditional_operator)
        args, save_kwargs = self._get_save_args(null_check=False)
        kwargs = {
            pythonic(RETURN_VALUES):  ALL_NEW,
            'conditional_operator': conditional_operator,
        }

        if attributes:
            kwargs[pythonic(ATTR_UPDATES)] = {}

        if pythonic(RANGE_KEY) in save_kwargs:
            kwargs[pythonic(RANGE_KEY)] = save_kwargs[pythonic(RANGE_KEY)]

        if expected_values:
            kwargs['expected'] = self._build_expected_values(expected_values, UPDATE_FILTER_OPERATOR_MAP)

        attrs = self._get_attributes()
        attributes = attributes or {}
        for attr, params in attributes.items():
            attribute_cls = attrs[attr]
            action = params['action'] and params['action'].upper()
            attr_values = {ACTION: action}
            if 'value' in params:
                attr_values[VALUE] = self._serialize_value(attribute_cls, params['value'])

            kwargs[pythonic(ATTR_UPDATES)][attribute_cls.attr_name] = attr_values

        kwargs.update(condition=condition)
        kwargs.update(actions=actions)
        data = self._get_connection().update_item(*args, **kwargs)
        self._throttle.add_record(data.get(CONSUMED_CAPACITY))
        for name, value in data[ATTRIBUTES].items():
            attr_name = self._dynamo_to_python_attr(name)
            attr = self._get_attributes().get(attr_name)
            if attr:
                setattr(self, attr_name, attr.deserialize(value.get(ATTR_TYPE_MAP[attr.attr_type])))
        return data