    def prototype(self, plugin_type):
        plugin_type_object = self.get(plugin_type)
        if not hasattr(plugin_type_object, 'prototype_elements'):
            raise Exception("Cannot pre-determine structure for collection of type %s" % plugin_type)

        dataset_collection = model.DatasetCollection()
        for e in plugin_type_object.prototype_elements():
            e.collection = dataset_collection
        return dataset_collection