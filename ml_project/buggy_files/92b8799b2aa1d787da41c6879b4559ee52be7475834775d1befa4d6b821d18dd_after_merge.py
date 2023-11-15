    def find(self, module_name):
        for finder in self.finders:
            try:
                section = finder.find(module_name)
            except Exception as exception:
                # isort has to be able to keep trying to identify the correct import section even if one approach fails
                if config.get('verbose', False):
                    print('{} encountered an error ({}) while trying to identify the {} module'.format(finder.__name__,
                                                                                                       str(exception),
                                                                                                       module_name))
            if section is not None:
                return section