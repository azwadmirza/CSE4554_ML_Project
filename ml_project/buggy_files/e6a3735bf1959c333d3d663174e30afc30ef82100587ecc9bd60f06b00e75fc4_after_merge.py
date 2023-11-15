    def update(self, update_expression, expression_attribute_names, expression_attribute_values):
        # Update subexpressions are identifiable by the operator keyword, so split on that and
        # get rid of the empty leading string.
        parts = [p for p in re.split(r'\b(SET|REMOVE|ADD|DELETE)\b', update_expression, flags=re.I) if p]
        # make sure that we correctly found only operator/value pairs
        assert len(parts) % 2 == 0, "Mismatched operators and values in update expression: '{}'".format(update_expression)
        for action, valstr in zip(parts[:-1:2], parts[1::2]):
            action = action.upper()

            # "Should" retain arguments in side (...)
            values = re.split(r',(?![^(]*\))', valstr)
            for value in values:
                # A Real value
                value = value.lstrip(":").rstrip(",").strip()
                for k, v in expression_attribute_names.items():
                    value = re.sub(r'{0}\b'.format(k), v, value)

                if action == "REMOVE":
                    key = value
                    attr, list_index = attribute_is_list(key.split('.')[0])
                    if '.' not in key:
                        if list_index:
                            new_list = DynamoType(self.attrs[attr])
                            new_list.delete(None, list_index)
                            self.attrs[attr] = new_list
                        else:
                            self.attrs.pop(value, None)
                    else:
                        # Handle nested dict updates
                        self.attrs[attr].delete('.'.join(key.split('.')[1:]))
                elif action == 'SET':
                    key, value = value.split("=", 1)
                    key = key.strip()
                    value = value.strip()

                    # check whether key is a list
                    attr, list_index = attribute_is_list(key.split('.')[0])
                    # If value not exists, changes value to a default if needed, else its the same as it was
                    value = self._get_default(value)
                    # If operation == list_append, get the original value and append it
                    value = self._get_appended_list(value, expression_attribute_values)

                    if type(value) != DynamoType:
                        if value in expression_attribute_values:
                            dyn_value = DynamoType(expression_attribute_values[value])
                        else:
                            dyn_value = DynamoType({"S": value})
                    else:
                        dyn_value = value

                    if '.' in key and attr not in self.attrs:
                        raise ValueError  # Setting nested attr not allowed if first attr does not exist yet
                    elif attr not in self.attrs:
                        self.attrs[attr] = dyn_value  # set new top-level attribute
                    else:
                        self.attrs[attr].set('.'.join(key.split('.')[1:]), dyn_value, list_index)  # set value recursively

                elif action == 'ADD':
                    key, value = value.split(" ", 1)
                    key = key.strip()
                    value_str = value.strip()
                    if value_str in expression_attribute_values:
                        dyn_value = DynamoType(expression_attribute_values[value])
                    else:
                        raise TypeError

                    # Handle adding numbers - value gets added to existing value,
                    # or added to 0 if it doesn't exist yet
                    if dyn_value.is_number():
                        existing = self.attrs.get(key, DynamoType({"N": '0'}))
                        if not existing.same_type(dyn_value):
                            raise TypeError()
                        self.attrs[key] = DynamoType({"N": str(
                            decimal.Decimal(existing.value) +
                            decimal.Decimal(dyn_value.value)
                        )})

                    # Handle adding sets - value is added to the set, or set is
                    # created with only this value if it doesn't exist yet
                    # New value must be of same set type as previous value
                    elif dyn_value.is_set():
                        existing = self.attrs.get(key, DynamoType({dyn_value.type: {}}))
                        if not existing.same_type(dyn_value):
                            raise TypeError()
                        new_set = set(existing.value).union(dyn_value.value)
                        self.attrs[key] = DynamoType({existing.type: list(new_set)})
                    else:  # Number and Sets are the only supported types for ADD
                        raise TypeError

                elif action == 'DELETE':
                    key, value = value.split(" ", 1)
                    key = key.strip()
                    value_str = value.strip()
                    if value_str in expression_attribute_values:
                        dyn_value = DynamoType(expression_attribute_values[value])
                    else:
                        raise TypeError

                    if not dyn_value.is_set():
                        raise TypeError
                    existing = self.attrs.get(key, None)
                    if existing:
                        if not existing.same_type(dyn_value):
                            raise TypeError
                        new_set = set(existing.value).difference(dyn_value.value)
                        self.attrs[key] = DynamoType({existing.type: list(new_set)})
                else:
                    raise NotImplementedError('{} update action not yet supported'.format(action))