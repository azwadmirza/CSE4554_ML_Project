    def _upload_dataset(self, trans, library_id, folder_id, replace_dataset=None, **kwd):
        # Set up the traditional tool state/params
        cntrller = 'api'
        tool_id = 'upload1'
        message = None
        tool = trans.app.toolbox.get_tool(tool_id)
        state = tool.new_state(trans)
        populate_state(trans, tool.inputs, kwd, state.inputs)
        tool_params = state.inputs
        dataset_upload_inputs = []
        for input_name, input in tool.inputs.items():
            if input.type == "upload_dataset":
                dataset_upload_inputs.append(input)
        # Library-specific params
        server_dir = kwd.get('server_dir', '')
        upload_option = kwd.get('upload_option', 'upload_file')
        response_code = 200
        if upload_option == 'upload_directory':
            full_dir, import_dir_desc = validate_server_directory_upload(trans, server_dir)
            message = 'Select a directory'
        elif upload_option == 'upload_paths':
            # Library API already checked this - following check isn't actually needed.
            validate_path_upload(trans)
        # Some error handling should be added to this method.
        try:
            # FIXME: instead of passing params here ( which have been processed by util.Params(), the original kwd
            # should be passed so that complex objects that may have been included in the initial request remain.
            library_bunch = upload_common.handle_library_params(trans, kwd, folder_id, replace_dataset)
        except Exception:
            response_code = 500
            message = "Unable to parse upload parameters, please report this error."
        # Proceed with (mostly) regular upload processing if we're still errorless
        if response_code == 200:
            if upload_option == 'upload_file':
                tool_params = upload_common.persist_uploads(tool_params, trans)
                uploaded_datasets = upload_common.get_uploaded_datasets(trans, cntrller, tool_params, dataset_upload_inputs, library_bunch=library_bunch)
            elif upload_option == 'upload_directory':
                uploaded_datasets, response_code, message = self._get_server_dir_uploaded_datasets(trans, kwd, full_dir, import_dir_desc, library_bunch, response_code, message)
            elif upload_option == 'upload_paths':
                uploaded_datasets, response_code, message = self._get_path_paste_uploaded_datasets(trans, kwd, library_bunch, response_code, message)
            if upload_option == 'upload_file' and not uploaded_datasets:
                response_code = 400
                message = 'Select a file, enter a URL or enter text'
        if response_code != 200:
            return (response_code, message)
        json_file_path = upload_common.create_paramfile(trans, uploaded_datasets)
        data_list = [ud.data for ud in uploaded_datasets]
        job_params = {}
        job_params['link_data_only'] = json.dumps(kwd.get('link_data_only', 'copy_files'))
        job_params['uuid'] = json.dumps(kwd.get('uuid', None))
        job, output = upload_common.create_job(trans, tool_params, tool, json_file_path, data_list, folder=library_bunch.folder, job_params=job_params)
        trans.sa_session.add(job)
        trans.sa_session.flush()
        return output