    def populate_collection_elements(self, collection, root_collection_builder, filenames, name=None, metadata_source_name=None, final_job_state='ok'):
        # TODO: allow configurable sorting.
        #    <sort by="lexical" /> <!-- default -->
        #    <sort by="reverse_lexical" />
        #    <sort regex="example.(\d+).fastq" by="1:numerical" />
        #    <sort regex="part_(\d+)_sample_([^_]+).fastq" by="2:lexical,1:numerical" />
        if name is None:
            name = "unnamed output"

        element_datasets = {'element_identifiers': [], 'datasets': [], 'tag_lists': [], 'paths': [], 'extra_files': []}
        for filename, discovered_file in filenames.items():
            create_dataset_timer = ExecutionTimer()
            fields_match = discovered_file.match
            if not fields_match:
                raise Exception("Problem parsing metadata fields for file %s" % filename)
            element_identifiers = fields_match.element_identifiers
            designation = fields_match.designation
            visible = fields_match.visible
            ext = fields_match.ext
            dbkey = fields_match.dbkey
            extra_files = fields_match.extra_files
            # galaxy.tools.parser.output_collection_def.INPUT_DBKEY_TOKEN
            if dbkey == "__input__":
                dbkey = self.input_dbkey

            # Create new primary dataset
            dataset_name = fields_match.name or designation

            link_data = discovered_file.match.link_data

            sources = discovered_file.match.sources
            hashes = discovered_file.match.hashes
            created_from_basename = discovered_file.match.created_from_basename

            dataset = self.create_dataset(
                ext=ext,
                designation=designation,
                visible=visible,
                dbkey=dbkey,
                name=dataset_name,
                metadata_source_name=metadata_source_name,
                link_data=link_data,
                sources=sources,
                hashes=hashes,
                created_from_basename=created_from_basename,
                final_job_state=final_job_state,
            )
            log.debug(
                "(%s) Created dynamic collection dataset for path [%s] with element identifier [%s] for output [%s] %s",
                self.job_id(),
                filename,
                designation,
                name,
                create_dataset_timer,
            )
            element_datasets['element_identifiers'].append(element_identifiers)
            element_datasets['extra_files'].append(extra_files)
            element_datasets['datasets'].append(dataset)
            element_datasets['tag_lists'].append(discovered_file.match.tag_list)
            element_datasets['paths'].append(filename)

        self.add_tags_to_datasets(datasets=element_datasets['datasets'], tag_lists=element_datasets['tag_lists'])
        for (element_identifiers, dataset) in zip(element_datasets['element_identifiers'], element_datasets['datasets']):
            current_builder = root_collection_builder
            for element_identifier in element_identifiers[:-1]:
                current_builder = current_builder.get_level(element_identifier)
            current_builder.add_dataset(element_identifiers[-1], dataset)

            # Associate new dataset with job
            element_identifier_str = ":".join(element_identifiers)
            association_name = '__new_primary_file_{}|{}__'.format(name, element_identifier_str)
            self.add_output_dataset_association(association_name, dataset)

        root_collection_builder.populate()
        self.flush()
        self.update_object_store_with_datasets(datasets=element_datasets['datasets'], paths=element_datasets['paths'], extra_files=element_datasets['extra_files'])
        add_datasets_timer = ExecutionTimer()
        self.add_datasets_to_history(element_datasets['datasets'])
        log.debug(
            "(%s) Add dynamic collection datasets to history for output [%s] %s",
            self.job_id(),
            name,
            add_datasets_timer,
        )
        self.set_datasets_metadata(datasets=element_datasets['datasets'])