        def handle_output(name, output, hidden=None):
            if output.parent:
                parent_to_child_pairs.append((output.parent, name))
                child_dataset_names.add(name)
            if async_tool and name in incoming:
                # HACK: output data has already been created as a result of the async controller
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
                    input_ext,
                    python_template_version=tool.python_template_version,
                )
                create_datasets = True
                dataset = None

                if completed_job:
                    for output_dataset in completed_job.output_datasets:
                        if output_dataset.name == name:
                            create_datasets = False
                            completed_data = output_dataset.dataset
                            dataset = output_dataset.dataset.dataset
                            break

                data = app.model.HistoryDatasetAssociation(extension=ext, dataset=dataset, create_dataset=create_datasets, flush=False)
                if create_datasets:
                    from_work_dir = output.from_work_dir
                    if from_work_dir is not None:
                        data.dataset.created_from_basename = os.path.basename(from_work_dir)
                if hidden is None:
                    hidden = output.hidden
                if not hidden and dataset_collection_elements is not None:  # Mapping over a collection - hide datasets
                    hidden = True
                if hidden:
                    data.visible = False
                if dataset_collection_elements is not None and name in dataset_collection_elements:
                    dataset_collection_elements[name].hda = data
                trans.sa_session.add(data)
                if not completed_job:
                    trans.app.security_agent.set_all_dataset_permissions(data.dataset, output_permissions, new=True)
            data.copy_tags_to(preserved_tags)

            if not completed_job and trans.app.config.legacy_eager_objectstore_initialization:
                # Must flush before setting object store id currently.
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
            if completed_job:
                data.blurb = completed_data.blurb
                data.peek = completed_data.peek
                data._metadata = completed_data._metadata
            else:
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