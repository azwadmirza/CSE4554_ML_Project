    def update_permissions(self, trans, dataset_id, payload, **kwd):
        """
        PUT /api/datasets/{encoded_dataset_id}/permissions
        Updates permissions of a dataset.

        :rtype:     dict
        :returns:   dictionary containing new permissions
        """
        if payload:
            kwd.update(payload)
        hda_ldda = kwd.get('hda_ldda', 'hda')
        dataset_assoc = self.get_hda_or_ldda(trans, hda_ldda=hda_ldda, dataset_id=dataset_id)
        if hda_ldda == "hda":
            self.hda_manager.update_permissions(trans, dataset_assoc, **kwd)
            return self.hda_manager.serialize_dataset_association_roles(trans, dataset_assoc)
        else:
            self.ldda_manager.update_permissions(trans, dataset_assoc, **kwd)
            return self.ldda_manager.serialize_dataset_association_roles(trans, dataset_assoc)