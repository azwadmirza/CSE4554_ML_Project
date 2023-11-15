    def to_json(self, trans, kwd={}, job=None, workflow_building_mode=False):
        """
        Recursively creates a tool dictionary containing repeats, dynamic options and updated states.
        """
        history_id = kwd.get('history_id', None)
        history = None
        if workflow_building_mode is workflow_building_modes.USE_HISTORY or workflow_building_mode is workflow_building_modes.DISABLED:
            # We don't need a history when exporting a workflow for the workflow editor or when downloading a workflow
            try:
                if history_id is not None:
                    history = self.history_manager.get_owned(trans.security.decode_id(history_id), trans.user, current_history=trans.history)
                else:
                    history = trans.get_history()
                if history is None and job is not None:
                    history = self.history_manager.get_owned(job.history.id, trans.user, current_history=trans.history)
                if history is None:
                    raise exceptions.MessageException('History unavailable. Please specify a valid history id')
            except Exception as e:
                raise exceptions.MessageException('[history_id=%s] Failed to retrieve history. %s.' % (history_id, str(e)))

        # build request context
        request_context = WorkRequestContext(app=trans.app, user=trans.user, history=history, workflow_building_mode=workflow_building_mode)

        # load job parameters into incoming
        tool_message = ''
        tool_warnings = ''
        if job:
            try:
                job_params = job.get_param_values(self.app, ignore_errors=True)
                tool_warnings = self.check_and_update_param_values(job_params, request_context, update_values=True)
                self._map_source_to_history(request_context, self.inputs, job_params)
                tool_message = self._compare_tool_version(job)
                params_to_incoming(kwd, self.inputs, job_params, self.app)
            except Exception as e:
                raise exceptions.MessageException(str(e))

        # create parameter object
        params = Params(kwd, sanitize=False)

        # expand incoming parameters (parameters might trigger multiple tool executions,
        # here we select the first execution only in order to resolve dynamic parameters)
        expanded_incomings, _ = expand_meta_parameters(trans, self, params.__dict__)
        if expanded_incomings:
            params.__dict__ = expanded_incomings[0]

        # do param translation here, used by datasource tools
        if self.input_translator:
            self.input_translator.translate(params)

        set_dataset_matcher_factory(request_context, self)
        # create tool state
        state_inputs = {}
        state_errors = {}
        populate_state(request_context, self.inputs, params.__dict__, state_inputs, state_errors)

        # create tool model
        tool_model = self.to_dict(request_context)
        tool_model['inputs'] = []
        self.populate_model(request_context, self.inputs, state_inputs, tool_model['inputs'])
        unset_dataset_matcher_factory(request_context)

        # create tool help
        tool_help = ''
        if self.help:
            tool_help = self.help.render(static_path=url_for('/static'), host_url=url_for('/', qualified=True))
            tool_help = unicodify(tool_help, 'utf-8')

        # update tool model
        tool_model.update({
            'id'            : self.id,
            'help'          : tool_help,
            'citations'     : bool(self.citations),
            'biostar_url'   : self.app.config.biostar_url,
            'sharable_url'  : self.sharable_url,
            'message'       : tool_message,
            'warnings'      : tool_warnings,
            'versions'      : self.tool_versions,
            'requirements'  : [{'name' : r.name, 'version' : r.version} for r in self.requirements],
            'errors'        : state_errors,
            'state_inputs'  : params_to_strings(self.inputs, state_inputs, self.app),
            'job_id'        : trans.security.encode_id(job.id) if job else None,
            'job_remap'     : self._get_job_remap(job),
            'history_id'    : trans.security.encode_id(history.id) if history else None,
            'display'       : self.display_interface,
            'action'        : url_for(self.action),
            'method'        : self.method,
            'enctype'       : self.enctype
        })
        return tool_model