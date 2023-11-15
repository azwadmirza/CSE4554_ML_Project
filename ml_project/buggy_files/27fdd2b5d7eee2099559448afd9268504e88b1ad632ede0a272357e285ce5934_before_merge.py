    def __init__(self, *args, **options):
        super().__init__(*args, **options)
        self._path_index = {}
        self._s3 = None