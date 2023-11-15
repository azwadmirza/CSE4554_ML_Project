    def get_vm_tags(self, tag_service=None, tag_association_svc=None, vm_mid=None):
        """
        Return list of tag name associated with virtual machine
        Args:
            tag_service:  Tag service object
            tag_association_svc: Tag association object
            vm_mid: Dynamic object for virtual machine

        Returns: List of tag names associated with the given virtual machine

        """
        # This API returns just names of tags
        # Please use get_tags_for_vm for more tag object details
        tags = []
        if vm_mid is None:
            return tags
        dynamic_managed_object = DynamicID(type='VirtualMachine', id=vm_mid)

        temp_tags_model = self.get_tags_for_object(tag_service, tag_association_svc, dynamic_managed_object)

        for tag_obj in temp_tags_model:
            tags.append(tag_obj.name)

        return tags