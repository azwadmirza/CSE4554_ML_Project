    def get_shape(self, ds_id, ds_info):
        """Get numpy array shape for the specified dataset.
        
        Args:
            ds_id (DatasetID): ID of dataset that will be loaded
            ds_info (dict): Dictionary of dataset information from config file
            
        Returns:
            tuple: (rows, cols)
            
        """
        var_path = ds_info.get('file_key', '{}'.format(ds_id.name))
        s = self[var_path + "/shape"]
        if len(s) == 3:
            # time is first dimension of 1
            s = s[1:]
        return s