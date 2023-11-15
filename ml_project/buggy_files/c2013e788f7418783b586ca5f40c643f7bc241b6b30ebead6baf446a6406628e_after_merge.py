    def __init__(self, src, b_dest, file_args, module):
        super(TarBzipArchive, self).__init__(src, b_dest, file_args, module)
        self.zipflag = '-j'