    def update_item(self, attribute, value=None, action=None, condition=None, conditional_operator=None, **expected_values):
        """
        Updates an item using the UpdateItem operation.

        This should be used for updating a single attribute of an item.

        :param attribute: The name of the attribute to be updated
        :param value: The new value for the attribute.
        :param action: The action to take if this item already exists.
            See: http://docs.aws.amazon.com/amazondynamodb/latest/APIReference/API_UpdateItem.html#DDB-UpdateItem-request-AttributeUpdate
        """
        warnings.warn("`Model.update_item` is deprecated in favour of `Model.update` now")

        self._conditional_operator_check(conditional_operator)
        args, save_kwargs = self._get_save_args(null_check=False)
        attribute_cls = None
        for attr_name, attr_cls in self._get_attributes().items():
            if attr_name == attribute:
                value = attr_cls.serialize(value)
                attribute_cls = attr_cls
                break
        if not attribute_cls:
            raise ValueError("Attribute {0} specified does not exist".format(attr_name))
        if save_kwargs.get(pythonic(RANGE_KEY)):
            kwargs = {pythonic(RANGE_KEY): save_kwargs.get(pythonic(RANGE_KEY))}
        else:
            kwargs = {}
        if len(expected_values):
            kwargs.update(expected=self._build_expected_values(expected_values, UPDATE_FILTER_OPERATOR_MAP))
        kwargs[pythonic(ATTR_UPDATES)] = {
            attribute_cls.attr_name: {
                ACTION: action.upper() if action else None,
            }
        }
        if action is not None and action.upper() != DELETE:
            kwargs[pythonic(ATTR_UPDATES)][attribute_cls.attr_name][VALUE] = {ATTR_TYPE_MAP[attribute_cls.attr_type]: value}
        kwargs[pythonic(RETURN_VALUES)] = ALL_NEW
        kwargs.update(conditional_operator=conditional_operator)
        kwargs.update(condition=condition)
        data = self._get_connection().update_item(
            *args,
            **kwargs
        )
        self._throttle.add_record(data.get(CONSUMED_CAPACITY))

        for name, value in data.get(ATTRIBUTES).items():
            attr_name = self._dynamo_to_python_attr(name)
            attr = self._get_attributes().get(attr_name)
            if attr:
                setattr(self, attr_name, attr.deserialize(value.get(ATTR_TYPE_MAP[attr.attr_type])))
        return data