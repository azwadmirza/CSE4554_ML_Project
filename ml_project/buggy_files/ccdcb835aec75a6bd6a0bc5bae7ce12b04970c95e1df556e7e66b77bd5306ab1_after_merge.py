    def execute(self, tool, trans, incoming={}, return_job=False, set_output_hid=True, history=None, job_params=None, rerun_remap_job_id=None, execution_cache=None, dataset_collection_elements=None):
        """
        Executes a tool, creating job and tool outputs, associating them, and
        submitting the job to the job queue. If history is not specified, use
        trans.history as destination for tool's output datasets.
        """
        self._check_access(tool, trans)
        app = trans.app
        if execution_cache is None:
            execution_cache = ToolExecutionCache(trans)
        current_user_roles = execution_cache.current_user_roles
        history, inp_data, inp_dataset_collections = self._collect_inputs(tool, trans, incoming, history, current_user_roles)

        # Build name for output datasets based on tool name and input names
        on_text = self._get_on_text(inp_data)

        # format='input" previously would give you a random extension from
        # the input extensions, now it should just give "input" as the output
        # format.
        input_ext = 'data' if tool.profile < 16.04 else "input"
        input_dbkey = incoming.get("dbkey", "?")
        preserved_tags = {}
        for name, data in reversed(inp_data.items()):
            if not data:
                data = NoneDataset(datatypes_registry=app.datatypes_registry)
                continue

            # Convert LDDA to an HDA.
            if isinstance(data, LibraryDatasetDatasetAssociation):
                data = data.to_history_dataset_association(None)
                inp_data[name] = data

            if tool.profile < 16.04:
                input_ext = data.ext

            if data.dbkey not in [None, '?']:
                input_dbkey = data.dbkey

            identifier = getattr(data, "element_identifier", None)
            if identifier is not None:
                incoming["%s|__identifier__" % name] = identifier

            for tag in [t for t in data.tags if t.user_tname == 'name']:
                preserved_tags[tag.value] = tag

        # Collect chromInfo dataset and add as parameters to incoming
        (chrom_info, db_dataset) = app.genome_builds.get_chrom_info(input_dbkey, trans=trans, custom_build_hack_get_len_from_fasta_conversion=tool.id != 'CONVERTER_fasta_to_len')
        if db_dataset:
            inp_data.update({"chromInfo": db_dataset})
        incoming["chromInfo"] = chrom_info

        # Determine output dataset permission/roles list
        existing_datasets = [inp for inp in inp_data.values() if inp]
        if existing_datasets:
            output_permissions = app.security_agent.guess_derived_permissions_for_datasets(existing_datasets)
        else:
            # No valid inputs, we will use history defaults
            output_permissions = app.security_agent.history_get_default_permissions(history)

        # Add the dbkey to the incoming parameters
        incoming["dbkey"] = input_dbkey
        # wrapped params are used by change_format action and by output.label; only perform this wrapping once, as needed
        wrapped_params = self._wrapped_params(trans, tool, incoming, inp_data)

        out_data = odict()
        input_collections = dict((k, v[0][0]) for k, v in inp_dataset_collections.items())
        output_collections = OutputCollections(
            trans,
            history,
            tool=tool,
            tool_action=self,
            input_collections=input_collections,
            dataset_collection_elements=dataset_collection_elements,
            on_text=on_text,
            incoming=incoming,
            params=wrapped_params.params,
            job_params=job_params,
        )

        # Keep track of parent / child relationships, we'll create all the
        # datasets first, then create the associations
        parent_to_child_pairs = []
        child_dataset_names = set()
        object_store_populator = ObjectStorePopulator(app)

        def handle_output(name, output, hidden=None):
            if output.parent:
                parent_to_child_pairs.append((output.parent, name))
                child_dataset_names.add(name)
            # What is the following hack for? Need to document under what
            # conditions can the following occur? (james@bx.psu.edu)
            # HACK: the output data has already been created
            #      this happens i.e. as a result of the async controller
            if name in incoming:
                dataid = incoming[name]
                data = trans.sa_session.query(app.model.HistoryDatasetAssociation).get(dataid)
                assert data is not None
                out_data[name] = data
            else:
                ext = determine_output_format(
                    output,
                    wrapped_params.params,
                    inp_data,
                    inp_dataset_collections,
                    input_ext
                )
                data = app.model.HistoryDatasetAssociation(extension=ext, create_dataset=True, flush=False)
                if hidden is None:
                    hidden = output.hidden
                if not hidden and dataset_collection_elements is not None:  # Mapping over a collection - hide datasets
                    hidden = True
                if hidden:
                    data.visible = False
                if dataset_collection_elements is not None and name in dataset_collection_elements:
                    dataset_collection_elements[name].hda = data
                trans.sa_session.add(data)
                trans.app.security_agent.set_all_dataset_permissions(data.dataset, output_permissions, new=True)
            for _, tag in preserved_tags.items():
                data.tags.append(tag.copy())

            # Must flush before setting object store id currently.
            # TODO: optimize this.
            trans.sa_session.flush()
            object_store_populator.set_object_store_id(data)

            # This may not be neccesary with the new parent/child associations
            data.designation = name
            # Copy metadata from one of the inputs if requested.

            # metadata source can be either a string referencing an input
            # or an actual object to copy.
            metadata_source = output.metadata_source
            if metadata_source:
                if isinstance(metadata_source, string_types):
                    metadata_source = inp_data.get(metadata_source)

            if metadata_source is not None:
                data.init_meta(copy_from=metadata_source)
            else:
                data.init_meta()
            # Take dbkey from LAST input
            data.dbkey = str(input_dbkey)
            # Set state
            data.blurb = "queued"
            # Set output label
            data.name = self.get_output_name(output, data, tool, on_text, trans, incoming, history, wrapped_params.params, job_params)
            # Store output
            out_data[name] = data
            if output.actions:
                # Apply pre-job tool-output-dataset actions; e.g. setting metadata, changing format
                output_action_params = dict(out_data)
                output_action_params.update(incoming)
                output.actions.apply_action(data, output_action_params)
            # Also set the default values of actions of type metadata
            self.set_metadata_defaults(output, data, tool, on_text, trans, incoming, history, wrapped_params.params, job_params)
            # Flush all datasets at once.
            return data

        for name, output in tool.outputs.items():
            if not filter_output(output, incoming):
                handle_output_timer = ExecutionTimer()
                if output.collection:
                    collections_manager = app.dataset_collections_service
                    element_identifiers = []
                    known_outputs = output.known_outputs(input_collections, collections_manager.type_registry)
                    # Just to echo TODO elsewhere - this should be restructured to allow
                    # nested collections.
                    for output_part_def in known_outputs:
                        # Add elements to top-level collection, unless nested...
                        current_element_identifiers = element_identifiers
                        current_collection_type = output.structure.collection_type

                        for parent_id in (output_part_def.parent_ids or []):
                            # TODO: replace following line with formal abstractions for doing this.
                            current_collection_type = ":".join(current_collection_type.split(":")[1:])
                            name_to_index = dict((value["name"], index) for (index, value) in enumerate(current_element_identifiers))
                            if parent_id not in name_to_index:
                                if parent_id not in current_element_identifiers:
                                    index = len(current_element_identifiers)
                                    current_element_identifiers.append(dict(
                                        name=parent_id,
                                        collection_type=current_collection_type,
                                        src="new_collection",
                                        element_identifiers=[],
                                    ))
                                else:
                                    index = name_to_index[parent_id]
                            current_element_identifiers = current_element_identifiers[index]["element_identifiers"]

                        effective_output_name = output_part_def.effective_output_name
                        element = handle_output(effective_output_name, output_part_def.output_def, hidden=True)
                        # TODO: this shouldn't exist in the top-level of the history at all
                        # but for now we are still working around that by hiding the contents
                        # there.
                        # Following hack causes dataset to no be added to history...
                        child_dataset_names.add(effective_output_name)

                        history.add_dataset(element, set_hid=set_output_hid, quota=False)
                        trans.sa_session.add(element)
                        trans.sa_session.flush()

                        current_element_identifiers.append({
                            "__object__": element,
                            "name": output_part_def.element_identifier,
                        })
                        log.info(element_identifiers)

                    if output.dynamic_structure:
                        assert not element_identifiers  # known_outputs must have been empty
                        element_kwds = dict(elements=collections_manager.ELEMENTS_UNINITIALIZED)
                    else:
                        element_kwds = dict(element_identifiers=element_identifiers)
                    output_collections.create_collection(
                        output=output,
                        name=name,
                        tags=preserved_tags,
                        **element_kwds
                    )
                    log.info("Handled collection output named %s for tool %s %s" % (name, tool.id, handle_output_timer))
                else:
                    handle_output(name, output)
                    log.info("Handled output named %s for tool %s %s" % (name, tool.id, handle_output_timer))

        add_datasets_timer = ExecutionTimer()
        # Add all the top-level (non-child) datasets to the history unless otherwise specified
        datasets_to_persist = []
        for name in out_data.keys():
            if name not in child_dataset_names and name not in incoming:  # don't add children; or already existing datasets, i.e. async created
                data = out_data[name]
                datasets_to_persist.append(data)
        # Set HID and add to history.
        # This is brand new and certainly empty so don't worry about quota.
        # TOOL OPTIMIZATION NOTE - from above loop to the job create below 99%+
        # of execution time happens within in history.add_datasets.
        history.add_datasets(trans.sa_session, datasets_to_persist, set_hid=set_output_hid, quota=False, flush=False)

        # Add all the children to their parents
        for parent_name, child_name in parent_to_child_pairs:
            parent_dataset = out_data[parent_name]
            child_dataset = out_data[child_name]
            parent_dataset.children.append(child_dataset)

        log.info("Added output datasets to history %s" % add_datasets_timer)
        job_setup_timer = ExecutionTimer()
        # Create the job object
        job, galaxy_session = self._new_job_for_session(trans, tool, history)
        self._record_inputs(trans, tool, job, incoming, inp_data, inp_dataset_collections, current_user_roles)
        self._record_outputs(job, out_data, output_collections)
        job.object_store_id = object_store_populator.object_store_id
        if job_params:
            job.params = dumps(job_params)
        job.set_handler(tool.get_job_handler(job_params))
        trans.sa_session.add(job)
        # Now that we have a job id, we can remap any outputs if this is a rerun and the user chose to continue dependent jobs
        # This functionality requires tracking jobs in the database.
        if app.config.track_jobs_in_database and rerun_remap_job_id is not None:
            self._remap_job_on_rerun(trans=trans,
                                     galaxy_session=galaxy_session,
                                     rerun_remap_job_id=rerun_remap_job_id,
                                     current_job=job,
                                     out_data=out_data)

        log.info("Setup for job %s complete, ready to flush %s" % (job.log_str(), job_setup_timer))

        job_flush_timer = ExecutionTimer()
        trans.sa_session.flush()
        log.info("Flushed transaction for job %s %s" % (job.log_str(), job_flush_timer))
        # Some tools are not really executable, but jobs are still created for them ( for record keeping ).
        # Examples include tools that redirect to other applications ( epigraph ).  These special tools must
        # include something that can be retrieved from the params ( e.g., REDIRECT_URL ) to keep the job
        # from being queued.
        if 'REDIRECT_URL' in incoming:
            # Get the dataset - there should only be 1
            for name in inp_data.keys():
                dataset = inp_data[name]
            redirect_url = tool.parse_redirect_url(dataset, incoming)
            # GALAXY_URL should be include in the tool params to enable the external application
            # to send back to the current Galaxy instance
            GALAXY_URL = incoming.get('GALAXY_URL', None)
            assert GALAXY_URL is not None, "GALAXY_URL parameter missing in tool config."
            redirect_url += "&GALAXY_URL=%s" % GALAXY_URL
            # Job should not be queued, so set state to ok
            job.set_state(app.model.Job.states.OK)
            job.info = "Redirected to: %s" % redirect_url
            trans.sa_session.add(job)
            trans.sa_session.flush()
            trans.response.send_redirect(url_for(controller='tool_runner', action='redirect', redirect_url=redirect_url))
        else:
            # Put the job in the queue if tracking in memory
            app.job_manager.job_queue.put(job.id, job.tool_id)
            trans.log_event("Added job to the job queue, id: %s" % str(job.id), tool_id=job.tool_id)
            return job, out_data