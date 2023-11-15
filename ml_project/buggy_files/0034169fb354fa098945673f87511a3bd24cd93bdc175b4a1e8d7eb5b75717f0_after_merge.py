def set_collection_elements(dataset_collection, type, dataset_instances):
    element_index = 0
    elements = []
    for element in type.generate_elements(dataset_instances):
        element.element_index = element_index
        element.collection = dataset_collection
        elements.append(element)

        element_index += 1

    dataset_collection.element_count = element_index
    return dataset_collection