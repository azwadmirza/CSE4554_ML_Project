            def __call__(self, parser, namespace, values, option_string=None):
                ''' The SplitAction will take the given ID parameter and spread the parsed
                parts of the id into the individual backing fields.

                Since the id value is expected to be of type `IterateValue`, all the backing
                (dest) fields will also be of type `IterateValue`
                '''
                try:
                    for value in [values] if isinstance(values, str) else values:
                        parts = parse_resource_id(value)
                        for arg in [arg for arg in arguments.values() if arg.id_part]:
                            existing_values = getattr(namespace, arg.name, None)
                            if existing_values is None:
                                existing_values = IterateValue()
                            existing_values.append(parts[arg.id_part])
                            setattr(namespace, arg.name, existing_values)
                except Exception as ex:
                    raise ValueError(ex)