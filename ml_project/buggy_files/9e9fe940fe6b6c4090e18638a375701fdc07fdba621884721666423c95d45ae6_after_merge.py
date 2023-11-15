def collect_dynamic_outputs(
    job_context,
    output_collections,
):
    # unmapped outputs do not correspond to explicit outputs of the tool, they were inferred entirely
    # from the tool provided metadata (e.g. galaxy.json).
    for unnamed_output_dict in job_context.tool_provided_metadata.get_unnamed_outputs():
        assert "destination" in unnamed_output_dict
        assert "elements" in unnamed_output_dict
        destination = unnamed_output_dict["destination"]
        elements = unnamed_output_dict["elements"]

        assert "type" in destination
        destination_type = destination["type"]
        assert destination_type in ["library_folder", "hdca", "hdas"]

        # three destination types we need to handle here - "library_folder" (place discovered files in a library folder),
        # "hdca" (place discovered files in a history dataset collection), and "hdas" (place discovered files in a history
        # as stand-alone datasets).
        if destination_type == "library_folder":
            # populate a library folder (needs to be already have been created)
            library_folder = job_context.get_library_folder(destination)
            persist_elements_to_folder(job_context, elements, library_folder)
        elif destination_type == "hdca":
            # create or populate a dataset collection in the history
            assert "collection_type" in unnamed_output_dict
            object_id = destination.get("object_id")
            if object_id:
                hdca = job_context.get_hdca(object_id)
            else:
                name = unnamed_output_dict.get("name", "unnamed collection")
                collection_type = unnamed_output_dict["collection_type"]
                collection_type_description = COLLECTION_TYPE_DESCRIPTION_FACTORY.for_collection_type(collection_type)
                structure = UninitializedTree(collection_type_description)
                hdca = job_context.create_hdca(name, structure)
            error_message = unnamed_output_dict.get("error_message")
            if error_message:
                hdca.collection.handle_population_failed(error_message)
            else:
                persist_elements_to_hdca(job_context, elements, hdca, collector=DEFAULT_DATASET_COLLECTOR)
        elif destination_type == "hdas":
            persist_hdas(elements, job_context, final_job_state=job_context.final_job_state)

    for name, has_collection in output_collections.items():
        output_collection_def = job_context.output_collection_def(name)
        if not output_collection_def:
            continue

        if not output_collection_def.dynamic_structure:
            continue

        # Could be HDCA for normal jobs or a DC for mapping
        # jobs.
        if hasattr(has_collection, "collection"):
            collection = has_collection.collection
        else:
            collection = has_collection

        # We are adding dynamic collections, which may be precreated, but their actually state is still new!
        collection.populated_state = collection.populated_states.NEW

        try:
            collection_builder = builder.BoundCollectionBuilder(collection)
            dataset_collectors = [dataset_collector(description) for description in output_collection_def.dataset_collector_descriptions]
            output_name = output_collection_def.name
            filenames = job_context.find_files(output_name, collection, dataset_collectors)
            job_context.populate_collection_elements(
                collection,
                collection_builder,
                filenames,
                name=output_collection_def.name,
                metadata_source_name=output_collection_def.metadata_source,
                final_job_state=job_context.final_job_state,
            )
        except Exception:
            log.exception("Problem gathering output collection.")
            collection.handle_population_failed("Problem building datasets for collection.")

        job_context.add_dataset_collection(has_collection)