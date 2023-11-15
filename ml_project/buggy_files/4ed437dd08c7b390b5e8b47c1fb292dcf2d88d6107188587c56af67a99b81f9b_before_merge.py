    def sliced_input_collection_structure(self, input_name):
        input_collection = self.example_params[input_name]
        collection_type_description = self.trans.app.dataset_collections_service.collection_type_descriptions.for_collection_type(input_collection.collection.collection_type)
        subcollection_mapping_type = None
        if self.is_implicit_input(input_name):
            subcollection_mapping_type = self.collection_info.subcollection_mapping_type(input_name)

        return get_structure(input_collection, collection_type_description, leaf_subcollection_type=subcollection_mapping_type)