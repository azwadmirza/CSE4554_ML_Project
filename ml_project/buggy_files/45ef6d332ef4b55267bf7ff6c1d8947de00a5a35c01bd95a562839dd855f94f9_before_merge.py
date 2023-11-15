    def __init__(self, src, dest, file_args, module):
        super(TarXzArchive, self).__init__(src, dest, file_args, module)
        self.zipflag = '-J'