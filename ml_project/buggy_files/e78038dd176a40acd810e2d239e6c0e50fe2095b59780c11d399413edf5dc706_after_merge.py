def add_id_parameters(command_table):

    def split_action(arguments):
        class SplitAction(argparse.Action): #pylint: disable=too-few-public-methods

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
                            elif isinstance(existing_values, str):
                                logger.warning(
                                    "Property '%s=%s' being overriden by value '%s' from IDs parameter.", # pylint: disable=line-too-long
                                    arg.name, existing_values, parts[arg.id_part]
                                )
                                existing_values = IterateValue()
                                existing_values.append(parts[arg.id_part])
                            setattr(namespace, arg.name, existing_values)
                except Exception as ex:
                    raise ValueError(ex)

        return SplitAction

    def command_loaded_handler(command):
        if not 'name' in [arg.id_part for arg in command.arguments.values() if arg.id_part]:
            # Only commands with a resource name are candidates for an id parameter
            return
        if command.name.split()[-1] == 'create':
            # Somewhat blunt hammer, but any create commands will not have an automatic id
            # parameter
            return

        required_arguments = []
        optional_arguments = []
        for arg in [argument for argument in command.arguments.values() if argument.id_part]:
            if arg.options.get('required', False):
                required_arguments.append(arg)
            else:
                optional_arguments.append(arg)
            arg.required = False

        def required_values_validator(namespace):
            errors = [arg for arg in required_arguments
                      if getattr(namespace, arg.name, None) is None]

            if errors:
                missing_required = ' '.join((arg.options_list[0] for arg in errors))
                raise ValueError('({} | {}) are required'.format(missing_required, '--ids'))

        group_name = 'Resource Id'
        for key, arg in command.arguments.items():
            if command.arguments[key].id_part:
                command.arguments[key].arg_group = group_name

        command.add_argument('ids',
                             '--ids',
                             metavar='RESOURCE_ID',
                             dest=argparse.SUPPRESS,
                             help="One or more resource IDs. If provided, no other 'Resource Id' "
                                  "arguments should be specified.",
                             action=split_action(command.arguments),
                             nargs='+',
                             type=ResourceId,
                             validator=required_values_validator,
                             arg_group=group_name)

    for command in command_table.values():
        command_loaded_handler(command)