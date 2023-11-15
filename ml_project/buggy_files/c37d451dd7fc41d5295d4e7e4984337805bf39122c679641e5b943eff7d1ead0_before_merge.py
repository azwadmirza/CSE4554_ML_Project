    def _normalize_parameters(self, thing, action=None, additional_args=dict()):
        '''
        arguments can be fuzzy.  Deal with all the forms.
        '''

        # final args are the ones we'll eventually return, so first update
        # them with any additional args specified, which have lower priority
        # than those which may be parsed/normalized next
        final_args = dict()
        if additional_args:
            if isinstance(additional_args, string_types):
                templar = Templar(loader=None)
                if templar._contains_vars(additional_args):
                    final_args['_variable_params'] = additional_args
                else:
                    raise AnsibleParserError("Complex args containing variables cannot use bare variables, and must use the full variable style ('{{var_name}}')")
            elif isinstance(additional_args, dict):
                final_args.update(additional_args)
            else:
                raise AnsibleParserError('Complex args must be a dictionary or variable string ("{{var}}").')

        # how we normalize depends if we figured out what the module name is
        # yet.  If we have already figured it out, it's an 'old style' invocation.
        # otherwise, it's not

        if action is not None:
            args = self._normalize_old_style_args(thing, action)
        else:
            (action, args) = self._normalize_new_style_args(thing)

            # this can occasionally happen, simplify
            if args and 'args' in args:
                tmp_args = args.pop('args')
                if isinstance(tmp_args, string_types):
                    tmp_args = parse_kv(tmp_args)
                args.update(tmp_args)

        # only internal variables can start with an underscore, so
        # we don't allow users to set them directy in arguments
        if args and action not in ('command', 'win_command', 'shell', 'win_shell', 'script', 'raw'):
            for arg in args:
                if arg.startswith('_ansible_'):
                    raise AnsibleError("invalid parameter specified for action '%s': '%s'" % (action, arg))

        # finally, update the args we're going to return with the ones
        # which were normalized above
        if args:
            final_args.update(args)

        return (action, final_args)