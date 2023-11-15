    def _handle_kernel_died(self, kernel_id):
        """notice that a kernel died"""
        self.log.warn("Kernel %s died, removing from map.", kernel_id)
        self.delete_mapping_for_kernel(kernel_id)
        self.remove_kernel(kernel_id)