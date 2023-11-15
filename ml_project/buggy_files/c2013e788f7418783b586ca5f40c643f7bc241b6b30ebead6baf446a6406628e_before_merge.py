    def __init__(self, src, dest, file_args, module):
        super(TarBzipArchive, self).__init__(src, dest, file_args, module)
        self.zipflag = '-j'