    def get_type_name(mode_number):
        """
        We need to maintain this type strings, for the __compare_options method,
        for easier comparision.
        """
        modes = [
            'Active-Backup',
            'Load balance (balance-xor)',
            None,
            'Dynamic link aggregation (802.3ad)',
        ]
        if (not 0 < mode_number <= len(modes)):
            return None
        return modes[mode_number - 1]