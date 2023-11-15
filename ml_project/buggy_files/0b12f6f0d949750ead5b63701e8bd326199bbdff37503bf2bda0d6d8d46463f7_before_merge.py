    def mapping(self):

        ''' Load objects mapping.
        '''
        with open(os.path.join(os.path.dirname(__file__), 'obj_map.json')) as infile:
            self.objects = json.load(infile)