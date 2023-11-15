    def precreate_dataset_collection(self, structure, allow_unitialized_element=True, completed_collection=None, implicit_output_name=None):
        has_structure = not structure.is_leaf and structure.children_known
        if not has_structure and allow_unitialized_element:
            dataset_collection = model.DatasetCollectionElement.UNINITIALIZED_ELEMENT
        elif not has_structure:
            collection_type_description = structure.collection_type_description
            dataset_collection = model.DatasetCollection(populated=False)
            dataset_collection.collection_type = collection_type_description.collection_type
        else:
            collection_type_description = structure.collection_type_description
            dataset_collection = model.DatasetCollection(populated=False)
            dataset_collection.collection_type = collection_type_description.collection_type
            elements = []
            for index, (identifier, substructure) in enumerate(structure.children):
                # TODO: Open question - populate these now or later?
                element = None
                if completed_collection and implicit_output_name:
                    job = completed_collection[index]
                    if job:
                        it = (jtiodca.dataset_collection for jtiodca in job.output_dataset_collections if jtiodca.name == implicit_output_name)
                        element = next(it, None)
                if element is None:
                    if substructure.is_leaf:
                        element = model.DatasetCollectionElement.UNINITIALIZED_ELEMENT
                    else:
                        element = self.precreate_dataset_collection(substructure, allow_unitialized_element=allow_unitialized_element)

                element = model.DatasetCollectionElement(
                    collection=dataset_collection,
                    element=element,
                    element_identifier=identifier,
                    element_index=index,
                )
                elements.append(element)
            dataset_collection.element_count = len(elements)

        return dataset_collection