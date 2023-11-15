        def update_properties(self, update_dict):
            # Sanity checks: check that we don't create a recursive dependency or an orphaned channel
            new_origin_id = update_dict.get('origin_id', self.origin_id)
            if new_origin_id not in (0, self.origin_id):
                new_parent = CollectionNode.get(public_key=self.public_key, id_=new_origin_id)
                if not new_parent:
                    raise ValueError("Target collection does not exists")
                root_path = new_parent.get_parents_ids()
                if new_origin_id == self.id_ or self.id_ in root_path:
                    raise ValueError("Can't move collection into itself or its descendants!")
                if 0 not in root_path:
                    # TODO: add orphan-cleaning hook here
                    raise ValueError("Tried to move collection into an orphaned hierarchy!")
            updated_self = super(CollectionNode, self).update_properties(update_dict)
            if updated_self.origin_id == 0 and self.metadata_type == COLLECTION_NODE:
                # Coerce to ChannelMetadata
                # ACHTUNG! This is a somewhat awkward way to re-create the entry as an instance of
                # another class. Be very careful with it!
                self_dict = updated_self.to_dict()
                updated_self.delete(recursive=False)
                self_dict.pop("rowid")
                self_dict.pop("metadata_type")
                self_dict['infohash'] = random_infohash()
                self_dict["sign_with"] = self._my_key
                updated_self = db.ChannelMetadata.from_dict(self_dict)
            return updated_self