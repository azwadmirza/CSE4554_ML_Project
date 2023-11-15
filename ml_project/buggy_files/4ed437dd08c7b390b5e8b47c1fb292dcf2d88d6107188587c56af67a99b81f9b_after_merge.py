    def sliced_input_collection_structure(self, input_name):
        unqualified_recurse = self.tool.profile < 18.09 and "|" not in input_name

        def find_collection(input_dict, input_name):
            for key, value in input_dict.items():
                if key == input_name:
                    return value
                if isinstance(value, dict):
                    if "|" in input_name:
                        prefix, rest_input_name = input_name.split("|", 1)
                        if key == prefix:
                            return find_collection(value, rest_input_name)
                    elif unqualified_recurse:
                        # Looking for "input1" instead of "cond|input1" for instance.
                        # See discussion on https://github.com/galaxyproject/galaxy/issues/6157.
                        unqualified_match = find_collection(value, input_name)
                        if unqualified_match:
                            return unqualified_match

        input_collection = find_collection(self.example_params, input_name)
        if input_collection is None:
            raise Exception("Failed to find referenced collection in inputs.")

        if not hasattr(input_collection, "collection"):
            raise Exception("Referenced input parameter is not a collection.")

        collection_type_description = self.trans.app.dataset_collections_service.collection_type_descriptions.for_collection_type(input_collection.collection.collection_type)
        subcollection_mapping_type = None
        if self.is_implicit_input(input_name):
            subcollection_mapping_type = self.collection_info.subcollection_mapping_type(input_name)

        return get_structure(input_collection, collection_type_description, leaf_subcollection_type=subcollection_mapping_type)