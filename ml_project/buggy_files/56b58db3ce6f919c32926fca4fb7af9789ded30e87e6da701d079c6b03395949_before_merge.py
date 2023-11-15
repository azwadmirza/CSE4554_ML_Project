    def __call__(self, projectables, nonprojectables=None, **info):
        if len(projectables) != 2:
            raise ValueError("Expected 2 datasets, got %d" %
                             (len(projectables), ))
        info = combine_info(*projectables)
        info['name'] = self.info['name']

        return Dataset(projectables[0] - projectables[1], **info)