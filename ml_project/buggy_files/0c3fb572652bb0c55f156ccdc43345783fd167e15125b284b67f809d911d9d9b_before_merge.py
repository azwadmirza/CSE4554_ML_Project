    def prepare_example_dict(ex):
        """ Returns the values in order corresponding to the data.
        
            ex:
                'Some text input'
            or in the case of multi-sequence inputs:
                ('The premise', 'the hypothesis',)
            etc.
        """
        values = list(ex.values())
        if len(values) == 1:
            return values[0]
        return values