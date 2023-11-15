    def callback(self, output, inputs=[], state=[]):
        self._validate_callback(output, inputs, state)

        callback_id = _create_callback_id(output)
        multi = isinstance(output, (list, tuple))

        self.callback_map[callback_id] = {
            "inputs": [
                {"id": c.component_id, "property": c.component_property}
                for c in inputs
            ],
            "state": [
                {"id": c.component_id, "property": c.component_property}
                for c in state
            ],
        }

        def wrap_func(func):
            @wraps(func)
            def add_context(*args, **kwargs):
                # don't touch the comment on the next line - used by debugger
                output_value = func(*args, **kwargs)  # %% callback invoked %%
                if multi:
                    if not isinstance(output_value, (list, tuple)):
                        raise exceptions.InvalidCallbackReturnValue(
                            "The callback {} is a multi-output.\n"
                            "Expected the output type to be a list"
                            " or tuple but got {}.".format(
                                callback_id, repr(output_value)
                            )
                        )

                    if not len(output_value) == len(output):
                        raise exceptions.InvalidCallbackReturnValue(
                            "Invalid number of output values for {}.\n"
                            " Expected {} got {}".format(
                                callback_id, len(output), len(output_value)
                            )
                        )

                    component_ids = collections.defaultdict(dict)
                    has_update = False
                    for i, o in enumerate(output):
                        val = output_value[i]
                        if val is not no_update:
                            has_update = True
                            o_id, o_prop = o.component_id, o.component_property
                            component_ids[o_id][o_prop] = val

                    if not has_update:
                        raise exceptions.PreventUpdate

                    response = {"response": component_ids, "multi": True}
                else:
                    if output_value is no_update:
                        raise exceptions.PreventUpdate

                    response = {
                        "response": {
                            "props": {output.component_property: output_value}
                        }
                    }

                try:
                    jsonResponse = json.dumps(
                        response, cls=plotly.utils.PlotlyJSONEncoder
                    )
                except TypeError:
                    self._validate_callback_output(output_value, output)
                    raise exceptions.InvalidCallbackReturnValue(
                        dedent(
                            """
                    The callback for property `{property:s}`
                    of component `{id:s}` returned a value
                    which is not JSON serializable.

                    In general, Dash properties can only be
                    dash components, strings, dictionaries, numbers, None,
                    or lists of those.
                    """
                        ).format(
                            property=output.component_property,
                            id=output.component_id,
                        )
                    )

                return jsonResponse

            self.callback_map[callback_id]["callback"] = add_context

            return add_context

        return wrap_func