def collect_primary_datasets(job_context, output, input_ext):
    tool = job_context.tool
    job_working_directory = job_context.job_working_directory
    sa_session = job_context.sa_session

    # Loop through output file names, looking for generated primary
    # datasets in form specified by discover dataset patterns or in tool provided metadata.
    primary_output_assigned = False
    new_outdata_name = None
    primary_datasets = {}
    for output_index, (name, outdata) in enumerate(output.items()):
        dataset_collectors = [DEFAULT_DATASET_COLLECTOR]
        if name in tool.outputs:
            dataset_collectors = [dataset_collector(description) for description in tool.outputs[name].dataset_collector_descriptions]
        filenames = odict.odict()
        for discovered_file in discover_files(name, job_context.tool_provided_metadata, dataset_collectors, job_working_directory, outdata):
            filenames[discovered_file.path] = discovered_file
        for filename_index, (filename, discovered_file) in enumerate(filenames.items()):
            extra_file_collector = discovered_file.collector
            fields_match = discovered_file.match
            if not fields_match:
                # Before I guess pop() would just have thrown an IndexError
                raise Exception("Problem parsing metadata fields for file %s" % filename)
            designation = fields_match.designation
            if filename_index == 0 and extra_file_collector.assign_primary_output and output_index == 0:
                new_outdata_name = fields_match.name or "%s (%s)" % (outdata.name, designation)
                # Move data from temp location to dataset location
                job_context.object_store.update_from_file(outdata.dataset, file_name=filename, create=True)
                primary_output_assigned = True
                continue
            if name not in primary_datasets:
                primary_datasets[name] = odict.odict()
            visible = fields_match.visible
            ext = fields_match.ext
            if ext == "input":
                ext = input_ext
            dbkey = fields_match.dbkey
            if dbkey == INPUT_DBKEY_TOKEN:
                dbkey = job_context.input_dbkey
            # Create new primary dataset
            new_primary_name = fields_match.name or "%s (%s)" % (outdata.name, designation)
            info = outdata.info

            # TODO: should be able to disambiguate files in different directories...
            new_primary_filename = os.path.split(filename)[-1]
            new_primary_datasets_attributes = job_context.tool_provided_metadata.get_new_dataset_meta_by_basename(name, new_primary_filename)

            primary_data = job_context.create_dataset(
                ext,
                designation,
                visible,
                dbkey,
                new_primary_name,
                filename,
                info=info,
                init_from=outdata,
                dataset_attributes=new_primary_datasets_attributes,
            )
            # Associate new dataset with job
            job_context.add_output_dataset_association('__new_primary_file_%s|%s__' % (name, designation), primary_data)

            if new_primary_datasets_attributes:
                extra_files_path = new_primary_datasets_attributes.get('extra_files', None)
                if extra_files_path:
                    extra_files_path_joined = os.path.join(job_working_directory, extra_files_path)
                    primary_data.dataset.create_extra_files_path()
                    for root, dirs, files in os.walk(extra_files_path_joined):
                        extra_dir = os.path.join(primary_data.extra_files_path, root.replace(extra_files_path_joined, '', 1).lstrip(os.path.sep))
                        extra_dir = os.path.normpath(extra_dir)
                        for f in files:
                            job_context.object_store.update_from_file(
                                primary_data.dataset,
                                extra_dir=extra_dir,
                                alt_name=f,
                                file_name=os.path.join(root, f),
                                create=True,
                                preserve_symlinks=True
                            )
            job_context.add_datasets_to_history([primary_data], for_output_dataset=outdata)
            # Add dataset to return dict
            primary_datasets[name][designation] = primary_data
        if primary_output_assigned:
            outdata.name = new_outdata_name
            outdata.init_meta()
            outdata.set_meta()
            outdata.set_peek()
            sa_session.add(outdata)

    sa_session.flush()
    return primary_datasets