    def get_shape(self, ds_id, ds_info):
        """Get numpy array shape for the specified dataset.
        
        Args:
            ds_id (DatasetID): ID of dataset that will be loaded
            ds_info (dict): Dictionary of dataset information from config file
            
        Returns:
            tuple: (rows, cols)
            
        """
        var_path = ds_info.get('file_key', '{}'.format(ds_id.name))
        if var_path + '/shape' not in self:
            # loading a scalar value
            shape = 1
        else:
            shape = self[var_path + '/shape']
            if len(shape) == 3:
                if shape[0] != 1:
                    raise ValueError("Not sure how to load 3D Dataset with more than 1 time")
                else:
                    shape = shape[1:]
        return shape