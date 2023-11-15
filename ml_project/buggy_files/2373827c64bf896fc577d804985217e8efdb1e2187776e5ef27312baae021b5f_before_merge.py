    def encode_dict_ids( self, a_dict, kind=None ):
        """
        Encode all ids in dictionary. Ids are identified by (a) an 'id' key or
        (b) a key that ends with '_id'
        """
        for key, val in a_dict.items():
            if key == 'id' or key.endswith('_id'):
                a_dict[ key ] = self.encode_id( val, kind=kind )

        return a_dict