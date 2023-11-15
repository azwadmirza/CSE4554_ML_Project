    def get_tags_for_vm(self, vm_mid=None):
        """
        Return list of tag object associated with virtual machine
        Args:
            vm_mid: Dynamic object for virtual machine

        Returns: List of tag object associated with the given virtual machine

        """
        return self.get_tags_for_dynamic_obj(mid=vm_mid, type='VirtualMachine')