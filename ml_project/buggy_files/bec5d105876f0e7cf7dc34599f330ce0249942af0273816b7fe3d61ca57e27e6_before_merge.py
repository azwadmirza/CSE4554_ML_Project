    def __init__(self, path, engine=None,
                 date_format=None, datetime_format=None, **engine_kwargs):
        # validate that this engine can handle the extension
        ext = os.path.splitext(path)[-1]
        self.check_extension(ext)

        self.path = path
        self.sheets = {}
        self.cur_sheet = None

        if date_format is None:
            self.date_format = 'YYYY-MM-DD'
        else:
            self.date_format = date_format
        if datetime_format is None:
            self.datetime_format = 'YYYY-MM-DD HH:MM:SS'
        else:
            self.datetime_format = datetime_format