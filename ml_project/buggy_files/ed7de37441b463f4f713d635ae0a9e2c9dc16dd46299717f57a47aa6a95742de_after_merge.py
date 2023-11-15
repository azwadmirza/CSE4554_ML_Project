    def dataset_states_and_extensions_summary(self):
        if not hasattr(self, '_dataset_states_and_extensions_summary'):
            db_session = object_session(self)

            dc = alias(DatasetCollection.table)
            de = alias(DatasetCollectionElement.table)
            hda = alias(HistoryDatasetAssociation.table)
            dataset = alias(Dataset.table)

            select_from = dc.outerjoin(de, de.c.dataset_collection_id == dc.c.id)

            depth_collection_type = self.collection_type
            while ":" in depth_collection_type:
                child_collection = alias(DatasetCollection.table)
                child_collection_element = alias(DatasetCollectionElement.table)
                select_from = select_from.outerjoin(child_collection, child_collection.c.id == de.c.child_collection_id)
                select_from = select_from.outerjoin(child_collection_element, child_collection_element.c.dataset_collection_id == child_collection.c.id)

                de = child_collection_element
                depth_collection_type = depth_collection_type.split(":", 1)[1]

            select_from = select_from.outerjoin(hda, hda.c.id == de.c.hda_id).outerjoin(dataset, hda.c.dataset_id == dataset.c.id)
            select_stmt = select([hda.c.extension, dataset.c.state]).select_from(select_from).where(dc.c.id == self.id).distinct()
            extensions = set()
            states = set()
            for extension, state in db_session.execute(select_stmt).fetchall():
                if state is not None:
                    # query may return (None, None) if not collection elements present
                    states.add(state)
                    extensions.add(extension)

            self._dataset_states_and_extensions_summary = (states, extensions)

        return self._dataset_states_and_extensions_summary