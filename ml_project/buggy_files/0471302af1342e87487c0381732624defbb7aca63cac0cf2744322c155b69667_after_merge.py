    def preprocess(self, nb, resources, km=None):
        self.output_hook_stack = collections.defaultdict(list)  # maps to list of hooks, where the last is used
        self.output_objects = {}
        try:
            result = super(VoilaExecutePreprocessor, self).preprocess(nb, resources=resources, km=km)
        except CellExecutionError as e:
            self.log.error(e)
            result = (nb, resources)
        return result