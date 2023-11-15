    def _enable_read_access(self):
        """! @brief Ensure flash is accessible by initing the algo for verify.
        
        Not all flash memories are always accessible. For instance, external QSPI. Initing the
        flash algo for the VERIFY operation is the canonical way to ensure that the flash is
        memory mapped and accessible.
        """
        if not self.algo_inited_for_read:
            self.flash.init(self.flash.Operation.VERIFY)
            self.algo_inited_for_read = True