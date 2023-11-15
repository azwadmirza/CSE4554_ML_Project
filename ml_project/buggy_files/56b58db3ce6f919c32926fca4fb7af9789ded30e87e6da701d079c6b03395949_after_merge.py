    def __call__(self, projectables, nonprojectables=None, **info):
        if len(projectables) != 2:
            raise ValueError("Expected 2 datasets, got %d" %
                             (len(projectables), ))
        info = combine_metadata(*projectables)
        info['name'] = self.attrs['name']

        return Dataset(projectables[0] - projectables[1], **info)