    def __init__(self, src, dest, file_args, module):
        super(TarArchive, self).__init__(src, dest, file_args, module)
        # argument to tar
        self.zipflag = ''