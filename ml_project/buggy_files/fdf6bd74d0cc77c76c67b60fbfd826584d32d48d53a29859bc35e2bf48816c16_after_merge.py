    def ensure_implicit_collections_populated(self, history, params):
        if not self.collection_info:
            return

        history = history or self.tool.get_default_history_by_trans(self.trans)
        if self.invocation_step.is_new:
            self.precreate_output_collections(history, params)
            for output_name, implicit_collection in self.implicit_collections.items():
                self.invocation_step.add_output(output_name, implicit_collection)
        else:
            collections = {}
            for output_assoc in self.invocation_step.output_dataset_collections:
                implicit_collection = output_assoc.dataset_collection
                assert hasattr(implicit_collection, "history_content_type")  # make sure it is an HDCA and not a DC
                collections[output_assoc.output_name] = output_assoc.dataset_collection
            self.implicit_collections = collections
        self.invocation_step.implicit_collection_jobs = self.implicit_collection_jobs