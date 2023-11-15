    def _complete_for_arg(self, arg_action: argparse.Action,
                          text: str, line: str, begidx: int, endidx: int,
                          consumed_arg_values: Dict[str, List[str]], *,
                          cmd_set: Optional[CommandSet] = None) -> List[str]:
        """
        Tab completion routine for an argparse argument
        :return: list of completions
        :raises: CompletionError if the completer or choices function this calls raises one
        """
        # Check if the arg provides choices to the user
        if arg_action.choices is not None:
            arg_choices = arg_action.choices
        else:
            arg_choices = getattr(arg_action, ATTR_CHOICES_CALLABLE, None)

        if arg_choices is None:
            return []

        # If we are going to call a completer/choices function, then set up the common arguments
        args = []
        kwargs = {}
        if isinstance(arg_choices, ChoicesCallable):
            if arg_choices.is_method:
                # figure out what class the completer was defined in
                completer_class = get_defining_class(arg_choices.to_call)

                # Was there a defining class identified? If so, is it a sub-class of CommandSet?
                if completer_class is not None and issubclass(completer_class, CommandSet):
                    # Since the completer function is provided as an unbound function, we need to locate the instance
                    # of the CommandSet to pass in as `self` to emulate a bound method call.
                    # We're searching for candidates that match the completer function's parent type in this order:
                    #   1. Does the CommandSet registered with the command's argparser match as a subclass?
                    #   2. Do any of the registered CommandSets in the Cmd2 application exactly match the type?
                    #   3. Is there a registered CommandSet that is is the only matching subclass?

                    # Now get the CommandSet associated with the current command/subcommand argparser
                    parser_cmd_set = getattr(self._parser, constants.PARSER_ATTR_COMMANDSET, cmd_set)
                    if isinstance(parser_cmd_set, completer_class):
                        # Case 1: Parser's CommandSet is a sub-class of the completer function's CommandSet
                        cmd_set = parser_cmd_set
                    else:
                        # Search all registered CommandSets
                        cmd_set = None
                        candidate_sets = []  # type: List[CommandSet]
                        for installed_cmd_set in self._cmd2_app._installed_command_sets:
                            if type(installed_cmd_set) == completer_class:
                                # Case 2: CommandSet is an exact type match for the completer's CommandSet
                                cmd_set = installed_cmd_set
                                break

                            # Add candidate for Case 3:
                            if isinstance(installed_cmd_set, completer_class):
                                candidate_sets.append(installed_cmd_set)
                        if cmd_set is None and len(candidate_sets) == 1:
                            # Case 3: There exists exactly 1 CommandSet that is a subclass of the completer's CommandSet
                            cmd_set = candidate_sets[0]
                    if cmd_set is None:
                        # No cases matched, raise an error
                        raise CompletionError('Could not find CommandSet instance matching defining type for completer')
                    args.append(cmd_set)
                args.append(self._cmd2_app)

            # Check if arg_choices.to_call expects arg_tokens
            to_call_params = inspect.signature(arg_choices.to_call).parameters
            if ARG_TOKENS in to_call_params:
                # Merge self._parent_tokens and consumed_arg_values
                arg_tokens = {**self._parent_tokens, **consumed_arg_values}

                # Include the token being completed
                arg_tokens.setdefault(arg_action.dest, [])
                arg_tokens[arg_action.dest].append(text)

                # Add the namespace to the keyword arguments for the function we are calling
                kwargs[ARG_TOKENS] = arg_tokens

        # Check if the argument uses a specific tab completion function to provide its choices
        if isinstance(arg_choices, ChoicesCallable) and arg_choices.is_completer:
            args.extend([text, line, begidx, endidx])
            results = arg_choices.to_call(*args, **kwargs)

        # Otherwise use basic_complete on the choices
        else:
            # Check if the choices come from a function
            if isinstance(arg_choices, ChoicesCallable) and not arg_choices.is_completer:
                arg_choices = arg_choices.to_call(*args, **kwargs)

            # Since arg_choices can be any iterable type, convert to a list
            arg_choices = list(arg_choices)

            # If these choices are numbers, and have not yet been sorted, then sort them now
            if not self._cmd2_app.matches_sorted and all(isinstance(x, numbers.Number) for x in arg_choices):
                arg_choices.sort()
                self._cmd2_app.matches_sorted = True

            # Since choices can be various types like int, we must convert them to strings
            for index, choice in enumerate(arg_choices):
                if not isinstance(choice, str):
                    arg_choices[index] = str(choice)

            # Filter out arguments we already used
            used_values = consumed_arg_values.get(arg_action.dest, [])
            arg_choices = [choice for choice in arg_choices if choice not in used_values]

            # Do tab completion on the choices
            results = basic_complete(text, line, begidx, endidx, arg_choices)

        return self._format_completions(arg_action, results)