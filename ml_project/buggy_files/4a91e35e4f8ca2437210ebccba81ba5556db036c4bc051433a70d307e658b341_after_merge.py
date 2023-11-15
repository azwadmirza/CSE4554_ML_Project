    def create( self, trans, parent, name, collection_type, element_identifiers=None,
                elements=None, implicit_collection_info=None, trusted_identifiers=None,
                hide_source_items=False, tags=None):
        """
        PRECONDITION: security checks on ability to add to parent
        occurred during load.
        """
        # Trust embedded, newly created objects created by tool subsystem.
        if trusted_identifiers is None:
            trusted_identifiers = implicit_collection_info is not None

        if element_identifiers and not trusted_identifiers:
            validate_input_element_identifiers( element_identifiers )

        dataset_collection = self.create_dataset_collection(
            trans=trans,
            collection_type=collection_type,
            element_identifiers=element_identifiers,
            elements=elements,
            hide_source_items=hide_source_items,
        )

        if isinstance( parent, model.History ):
            dataset_collection_instance = self.model.HistoryDatasetCollectionAssociation(
                collection=dataset_collection,
                name=name,
            )
            if implicit_collection_info:
                for input_name, input_collection in implicit_collection_info[ "implicit_inputs" ]:
                    dataset_collection_instance.add_implicit_input_collection( input_name, input_collection )
                for output_dataset in implicit_collection_info.get( "outputs" ):
                    if output_dataset not in trans.sa_session:
                        output_dataset = trans.sa_session.query( type( output_dataset ) ).get( output_dataset.id )
                    if isinstance( output_dataset, model.HistoryDatasetAssociation ):
                        output_dataset.hidden_beneath_collection_instance = dataset_collection_instance
                    elif isinstance( output_dataset, model.HistoryDatasetCollectionAssociation ):
                        dataset_collection_instance.add_implicit_input_collection( input_name, input_collection )
                    else:
                        # dataset collection, don't need to do anything...
                        pass
                    trans.sa_session.add( output_dataset )

                dataset_collection_instance.implicit_output_name = implicit_collection_info[ "implicit_output_name" ]

            log.debug("Created collection with %d elements" % ( len( dataset_collection_instance.collection.elements ) ) )
            # Handle setting hid
            parent.add_dataset_collection( dataset_collection_instance )

        elif isinstance( parent, model.LibraryFolder ):
            dataset_collection_instance = self.model.LibraryDatasetCollectionAssociation(
                collection=dataset_collection,
                folder=parent,
                name=name,
            )

        else:
            message = "Internal logic error - create called with unknown parent type %s" % type( parent )
            log.exception( message )
            raise MessageException( message )
        tags = tags or {}
        if implicit_collection_info:
            for k, v in implicit_collection_info.get('implicit_inputs', []):
                for tag in [t for t in v.tags if t.user_tname == 'name']:
                    tags[tag.value] = tag
        for _, tag in tags.items():
            dataset_collection_instance.tags.append(tag.copy(cls=model.HistoryDatasetCollectionTagAssociation))

        return self.__persist( dataset_collection_instance )