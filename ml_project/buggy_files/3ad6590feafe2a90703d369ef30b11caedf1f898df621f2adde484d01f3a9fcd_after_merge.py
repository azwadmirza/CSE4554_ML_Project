    def __init__(self, src, b_dest, file_args, module):
        super(TarArchive, self).__init__(src, b_dest, file_args, module)
        # argument to tar
        self.zipflag = ''