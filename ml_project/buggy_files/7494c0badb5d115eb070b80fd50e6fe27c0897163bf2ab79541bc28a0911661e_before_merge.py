    def __init__(self, file_id, bot, file_size=None, file_path=None, **kwargs):
        # Required
        self.file_id = str(file_id)

        # Optionals
        self.file_size = file_size
        if file_path:
            self.file_path = str(file_path)

        self.bot = bot

        self._id_attrs = (self.file_id,)