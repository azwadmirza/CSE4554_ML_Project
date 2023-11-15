    def mapping(self):

        ''' Load objects mapping.
        '''
        file_dir = os.path.dirname(ensure_text(__file__, sys.getfilesystemencoding()))

        with open(os.path.join(file_dir, 'obj_map.json')) as infile:
            self.objects = json.load(infile)