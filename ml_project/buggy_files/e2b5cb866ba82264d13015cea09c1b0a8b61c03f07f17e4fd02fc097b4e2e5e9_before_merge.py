    def on_setexceptionbreakpoints_request(self, py_db, request):
        '''
        :param SetExceptionBreakpointsRequest request:
        '''
        # : :type arguments: SetExceptionBreakpointsArguments
        arguments = request.arguments
        filters = arguments.filters
        exception_options = arguments.exceptionOptions
        self.api.remove_all_exception_breakpoints(py_db)

        # Can't set these in the DAP.
        condition = None
        expression = None
        notify_on_first_raise_only = False

        ignore_libraries = 1 if py_db.get_use_libraries_filter() else 0

        if exception_options:
            break_raised = True
            break_uncaught = True

            for option in exception_options:
                option = ExceptionOptions(**option)
                if not option.path:
                    continue

                notify_on_handled_exceptions = 1 if option.breakMode == 'always' else 0
                notify_on_unhandled_exceptions = 1 if option.breakMode in ('unhandled', 'userUnhandled') else 0
                exception_paths = option.path

                exception_names = []
                if len(exception_paths) == 0:
                    continue

                elif len(exception_paths) == 1:
                    if 'Python Exceptions' in exception_paths[0]['names']:
                        exception_names = ['BaseException']

                else:
                    path_iterator = iter(exception_paths)
                    if 'Python Exceptions' in next(path_iterator)['names']:
                        for path in path_iterator:
                            for ex_name in path['names']:
                                exception_names.append(ex_name)

                for exception_name in exception_names:
                    self.api.add_python_exception_breakpoint(
                        py_db,
                        exception_name,
                        condition,
                        expression,
                        notify_on_handled_exceptions,
                        notify_on_unhandled_exceptions,
                        notify_on_first_raise_only,
                        ignore_libraries
                    )

        else:
            break_raised = 'raised' in filters
            break_uncaught = 'uncaught' in filters
            if break_raised or break_uncaught:
                notify_on_handled_exceptions = 1 if break_raised else 0
                notify_on_unhandled_exceptions = 1 if break_uncaught else 0
                exception = 'BaseException'

                self.api.add_python_exception_breakpoint(
                    py_db,
                    exception,
                    condition,
                    expression,
                    notify_on_handled_exceptions,
                    notify_on_unhandled_exceptions,
                    notify_on_first_raise_only,
                    ignore_libraries
                )

        if break_raised or break_uncaught:
            btype = None
            if self._options.django_debug:
                btype = 'django'
            elif self._options.flask_debug:
                btype = 'jinja2'

            if btype:
                self.api.add_plugins_exception_breakpoint(
                    py_db, btype, 'BaseException')  # Note: Exception name could be anything here.

        # Note: no body required on success.
        set_breakpoints_response = pydevd_base_schema.build_response(request)
        return NetCommand(CMD_RETURN, 0, set_breakpoints_response, is_json=True)