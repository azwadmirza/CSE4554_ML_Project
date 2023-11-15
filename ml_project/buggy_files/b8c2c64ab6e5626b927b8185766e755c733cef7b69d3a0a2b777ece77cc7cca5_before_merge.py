    def _normalize_parameters(self, parameters):
        """Normalize a parameter list.
        Get the standard form of a parameter list, which includes:
            1. Use long options to replace short options
            2. Remove the unrecognized parameters
            3. Sort the result parameter list
        An example: ['-g', '-n'] ==> ['--name', '--resource-group']
        """

        from knack.deprecation import Deprecated

        normalized_parameters = []
        try:
            cmd_table = self.cli_ctx.invocation.commands_loader.command_table.get(self.command, None)
            parameter_table = cmd_table.arguments if cmd_table else None
        except AttributeError:
            parameter_table = None

        if parameters:
            rules = {
                '-h': '--help',
                '-o': '--output',
                '--only-show-errors': None,
                '--help': None,
                '--output': None,
                '--query': None,
                '--debug': None,
                '--verbose': None
            }

            if parameter_table:
                for argument in parameter_table.values():
                    options = argument.type.settings['options_list']
                    options = (option for option in options if not isinstance(option, Deprecated))
                    try:
                        sorted_options = sorted(options, key=len, reverse=True)
                        standard_form = sorted_options[0]

                        for option in sorted_options[1:]:
                            rules[option] = standard_form
                        rules[standard_form] = None
                    except TypeError:
                        logger.debug('Unexpected argument options `%s` of type `%s`.', options, type(options).__name__)

            for parameter in parameters:
                if parameter in rules:
                    normalized_form = rules.get(parameter, None) or parameter
                    normalized_parameters.append(normalized_form)
                else:
                    logger.debug('"%s" is an invalid parameter for command "%s".', parameter, self.command)

        return sorted(normalized_parameters)