    def __init__(self, ctx):
        super(DirectoryOutput, self).__init__(ctx)
        if self.root_dir.startswith('file://'):
            self.root_dir = self.root_dir[len('file://'):]
        if self.ctx.output_path is not None:
            if not os.path.exists(self.root_dir):
                os.makedirs(self.root_dir)